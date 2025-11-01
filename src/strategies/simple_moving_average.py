"""This module contains the TradeBotSimpleMovingAverage class."""

from datetime import datetime, timezone
from typing import Dict, Optional, Tuple, TypedDict

import numpy as np
import pandas as pd

from src.core.base_trade_bot import TradeBot
from src.core.config import StrategyType, TradingConfig, OrderType
from src.data.order_result import OrderResult
from src.utils.logger import logger


class TechnicalIndicators(TypedDict):
    """A dictionary representing the technical indicators."""

    sma: float
    std: float
    momentum: float
    volatility: float


class TradeBotSimpleMovingAverage(TradeBot):
    """
    Enhanced Simple Moving Average trading bot that implements a sophisticated SMA strategy
    with dynamic thresholds, trend analysis, and risk management.
    """

    def __init__(self, config: Optional[TradingConfig] = None) -> None:
        """
        Initialize the SMA trading bot with configuration.

        :param config: Optional trading configuration. If None, uses default config.
        """
        super().__init__(config=config if config else TradingConfig())
        self.strategy_type = StrategyType.SMA_CROSSOVER
        self._validate_sma_config()

    def _validate_sma_config(self) -> None:
        """Validate SMA-specific configuration parameters."""
        if self.config.technical_indicators.sma_short_period >= self.config.technical_indicators.sma_long_period:
            raise ValueError("Short period must be less than long period")

        if self.config.technical_indicators.momentum_lookback_period <= 0:
            raise ValueError("Momentum lookback period must be positive")

    def calculate_technical_indicators(self, df: pd.DataFrame, period: int) -> TechnicalIndicators:
        """
        Calculate technical indicators for the given period.

        :param df: DataFrame containing price data
        :param period: Rolling window period for calculations
        :return: Dictionary containing calculated technical indicators
        """
        if df is None or df.empty or not period:
            logger.warning("Invalid data provided for technical indicator calculation")
            return {"sma": 0.0, "std": 0.0, "momentum": 0.0, "volatility": 0.0}

        try:
            df = df.copy()
            df["close_price"] = pd.to_numeric(df["close_price"], errors="coerce")

            # Handle NaN values
            df = df.dropna(subset=["close_price"])

            if len(df) < period:
                logger.warning("Insufficient data points for period %s", period)
                return {"sma": 0.0, "std": 0.0, "momentum": 0.0, "volatility": 0.0}

            # Calculate SMA and Standard Deviation
            df["SMA"] = df["close_price"].rolling(window=period, min_periods=1).mean()
            df["STD"] = df["close_price"].rolling(window=period, min_periods=1).std()

            # Calculate Momentum (rate of change)
            df["momentum"] = df["close_price"].pct_change(self.config.technical_indicators.momentum_lookback_period)

            # Calculate Historical Volatility
            df["log_return"] = np.log(df["close_price"] / df["close_price"].shift(1))
            df["volatility"] = df["log_return"].rolling(window=period).std() * np.sqrt(252)

            return {
                "sma": round(df["SMA"].iloc[-1], 4),
                "std": round(df["STD"].iloc[-1], 4),
                "momentum": round(df["momentum"].iloc[-1], 4),
                "volatility": round(df["volatility"].iloc[-1], 4),
            }

        except (pd.errors.EmptyDataError, KeyError, ValueError) as e:
            logger.error("Error calculating technical indicators: %s", str(e))
            return {"sma": 0.0, "std": 0.0, "momentum": 0.0, "volatility": 0.0}

    def analyze_market_conditions(
        self, short_term: TechnicalIndicators, long_term: TechnicalIndicators
    ) -> Tuple[float, float, bool]:
        """
        Analyze market conditions using technical indicators.
        Returns neutral values if insufficient data.
        """
        try:
            # Validate SMA values
            if not long_term.get("sma") or long_term["sma"] == 0:
                logger.warning("Invalid or zero long-term SMA value")
                return 0.0, 0.0, False

            if not short_term.get("sma"):
                logger.warning("Invalid short-term SMA value")
                return 0.0, 0.0, False

            # Calculate trend strength using multiple factors
            price_trend = (short_term["sma"] - long_term["sma"]) / long_term["sma"]

            # Validate volatility values
            volatility_ratio = (
                short_term.get("volatility", 0) / long_term.get("volatility", 1)
                if long_term.get("volatility", 0) > 0
                else 1.0
            )

            trend_strength = abs(price_trend) * (1 + volatility_ratio)
            signal_strength = price_trend * (1 + abs(short_term.get("momentum", 0)))
            momentum_signal = short_term.get("momentum", 0) > self.config.technical_indicators.momentum_threshold

            return trend_strength, signal_strength, momentum_signal

        except (KeyError, ValueError, ZeroDivisionError) as e:
            logger.warning("Error in market conditions analysis: %s", str(e))
            return 0.0, 0.0, False

    def calculate_position_size(self, ticker: str, signal_strength: float) -> float:
        """
        Calculate position size based on signal strength and risk parameters.

        :param ticker: Stock ticker symbol
        :param signal_strength: Strength of the trading signal
        :return: Position size in dollars
        """
        account_value = self.get_current_cash_position()

        # Use 25% of available cash per trade
        base_position = min(account_value * 0.25, self.config.risk_management.max_trade_amount)

        # Adjust based on signal strength
        adjusted_position = base_position * abs(signal_strength)

        # Ensure position meets minimum requirements
        return max(
            min(adjusted_position, self.config.risk_management.max_trade_amount),
            self.config.risk_management.min_trade_amount,
        )

    def make_order_recommendation(self, ticker: str) -> Optional[OrderType]:
        """
        Generate trading signals based on SMA strategy and market conditions.

        :param ticker: Stock ticker symbol
        :return: OrderType recommendation
        """
        try:
            if not ticker:
                return None

            # Get historical data and current market conditions
            stock_history_df = self.get_stock_history_dataframe(ticker, interval="5minute", span="day")
            current_price = self.get_current_market_price(ticker)
            position = self.get_current_positions().get(ticker)

            if position and self.check_risk_management(current_price, position):
                logger.info("Risk management triggered for %s", ticker)
                return OrderType.SELL_RECOMMENDATION

            short_term = self.calculate_technical_indicators(
                stock_history_df,
                self.config.technical_indicators.sma_short_period,
            )
            long_term = self.calculate_technical_indicators(
                stock_history_df,
                self.config.technical_indicators.sma_long_period,
            )

            (
                trend_strength,
                signal_strength,
                momentum_signal,
            ) = self.analyze_market_conditions(short_term, long_term)

            threshold = (
                self.config.threshold_percentage * (1 + trend_strength)
                if self.config.enable_dynamic_threshold
                else self.config.threshold_percentage
            )

            if signal_strength > threshold and momentum_signal:
                return OrderType.BUY_RECOMMENDATION
            if signal_strength < -threshold or (signal_strength < 0 and not momentum_signal):
                return OrderType.SELL_RECOMMENDATION

            return OrderType.HOLD_RECOMMENDATION

        except (pd.errors.EmptyDataError, KeyError, ValueError) as e:
            logger.error("Error generating order recommendation: %s", str(e))
            return OrderType.HOLD_RECOMMENDATION

    def execute_trade(self, ticker: str) -> OrderResult:
        """
        Execute trade based on strategy recommendation and position sizing.

        :param ticker: Stock ticker symbol
        :return: OrderResult containing trade execution details
        """
        try:
            if not self.config.should_trade_now(datetime.now(timezone.utc)):
                return OrderResult(success=False, error_message="Outside trading hours", amount=0.0)

            recommendation = self.make_order_recommendation(ticker)

            if recommendation == OrderType.BUY_RECOMMENDATION:
                stock_history_df = self.get_stock_history_dataframe(ticker, interval="5minute", span="day")
                short_term = self.calculate_technical_indicators(
                    stock_history_df,
                    self.config.technical_indicators.sma_short_period,
                )
                long_term = self.calculate_technical_indicators(
                    stock_history_df,
                    self.config.technical_indicators.sma_long_period,
                )
                _,
                signal_strength,
                _ = self.analyze_market_conditions(short_term, long_term)
                position_size = self.calculate_position_size(ticker, signal_strength)
                return self.place_order(ticker, OrderType.BUY_RECOMMENDATION, position_size)

            if recommendation == OrderType.SELL_RECOMMENDATION:
                position = self.get_current_positions().get(ticker)
                if position:
                    return self.place_order(ticker, OrderType.SELL_RECOMMENDATION, position.equity)

            return OrderResult(success=True, error_message="No trade conditions met", amount=0.0)

        except (pd.errors.EmptyDataError, KeyError, ValueError) as e:
            logger.error("Error executing trade: %s", str(e))
            return OrderResult(success=False, error_message=str(e), amount=0.0)
