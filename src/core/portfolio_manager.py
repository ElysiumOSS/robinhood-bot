"""This module contains the PortfolioManager class."""

from dataclasses import dataclass
from typing import Dict

import numpy as np

from src.data.position import Position


@dataclass
class PortfolioMetrics:
    """Data class for portfolio metrics."""

    total_equity: float
    cash_available: float
    positions: Dict[str, Position]
    sector_exposure: Dict[str, float]
    beta_weighted_delta: float
    sharpe_ratio: float
    sortino_ratio: float


class PortfolioManager:
    """A class to manage a trading portfolio."""

    def __init__(self, initial_capital: float, max_position_size: float = 0.2) -> None:
        """
        Initialize the PortfolioManager.

        :param initial_capital: The initial capital of the portfolio.
        :param max_position_size: The maximum size of a single position.
        """
        self.initial_capital = initial_capital
        self.max_position_size = max_position_size
        self.positions: Dict[str, Position] = {}

    def calculate_position_size(self, ticker: str, signal_strength: float, volatility: float) -> float:
        """
        Calculate optimal position size using Kelly Criterion and volatility adjustment.

        :param ticker: The ticker symbol of the stock.
        :param signal_strength: The strength of the trading signal.
        :param volatility: The volatility of the stock.
        :return: The optimal position size.
        """
        portfolio_metrics = self.get_portfolio_metrics()
        available_capital = portfolio_metrics.cash_available

        # Kelly Criterion calculation
        win_rate = 0.55  # Historical win rate
        win_loss_ratio = 1.5  # Historical profit/loss ratio
        kelly_percentage = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

        # Volatility adjustment
        vol_factor = np.exp(-volatility)

        # Position size calculation
        base_size = available_capital * kelly_percentage * vol_factor
        adjusted_size = base_size * abs(signal_strength)

        # Apply position limits
        max_allowed = available_capital * self.max_position_size
        return min(adjusted_size, max_allowed)

    def get_portfolio_metrics(self) -> PortfolioMetrics:
        """
        Calculate comprehensive portfolio metrics.

        :return: A PortfolioMetrics object.
        """
        total_equity = sum(pos.equity for pos in self.positions.values())

        return PortfolioMetrics(
            total_equity=total_equity,
            cash_available=self.initial_capital - total_equity,
            positions=self.positions,
            sector_exposure={},
            beta_weighted_delta=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
        )
