"""This module contains the PerformanceAnalyzer class."""

from datetime import datetime
from typing import Any, Dict, List, TypedDict

import pandas as pd


class PerformanceReport(TypedDict):
    """A dictionary representing the performance report."""

    total_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    risk_adjusted_return: float
    alpha: float
    beta: float
    information_ratio: float


class PerformanceAnalyzer:
    """A class to analyze the performance of a trading bot."""

    def __init__(self) -> None:
        """Initialize the PerformanceAnalyzer."""
        self.trade_history: List[Dict[str, Any]] = []
        self.daily_returns: pd.Series = pd.Series()
        self.benchmark_returns: pd.Series = pd.Series()

    def add_trade(self, trade: Dict[str, Any]) -> None:
        """
        Record a new trade with enhanced metrics.

        :param trade: The trade to record.
        """
        self.trade_history.append(
            {
                **trade,
                "timestamp": datetime.now(),
            }
        )

    def get_performance_report(self) -> PerformanceReport:
        """
        Generate comprehensive performance report.

        :return: A dictionary containing the performance report.
        """
        if not self.trade_history:
            return self._empty_performance_report()

        metrics: PerformanceReport = {
            "total_return": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "risk_adjusted_return": 0.0,
            "alpha": 0.0,
            "beta": 0.0,
            "information_ratio": 0.0,
        }

        return metrics

    def _empty_performance_report(self) -> PerformanceReport:
        """Return an empty performance report."""
        return {
            "total_return": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "risk_adjusted_return": 0.0,
            "alpha": 0.0,
            "beta": 0.0,
            "information_ratio": 0.0,
        }
