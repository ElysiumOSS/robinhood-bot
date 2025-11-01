from __future__ import absolute_import

__version__ = "1.0.0"
__author__ = "Mike Odnis"
__email__ = "mike@mikeodnis.dev"
__license__ = "MIT License"
__credits__ = ""

from src.core import (
    TradeBot,
    TradingConfig,
    OrderType,
    StrategyType,
    PortfolioManager,
    PerformanceAnalyzer,
)
from src.data import OrderResult, Position, SMAPosition, Tweet
from src.strategies import (
    TradeBotSimpleMovingAverage,
    TradeBotVWAP,
    calculate_macd_signal,
    calculate_rsi_signal,
    calculate_sentiment_signal,
    calculate_sma_signal,
    calculate_volatility,
    calculate_vwap_signal,
)
from src.utils import RobinhoodCredentials, TwitterCredentials, logger

__all__ = [
    "TradeBot",
    "TradingConfig",
    "OrderType",
    "StrategyType",
    "PortfolioManager",
    "PerformanceAnalyzer",
    "OrderResult",
    "Position",
    "SMAPosition",
    "Tweet",
    "TradeBotSimpleMovingAverage",
    "TradeBotVWAP",
    "calculate_macd_signal",
    "calculate_rsi_signal",
    "calculate_sentiment_signal",
    "calculate_sma_signal",
    "calculate_volatility",
    "calculate_vwap_signal",
    "RobinhoodCredentials",
    "TwitterCredentials",
    "logger",
]
