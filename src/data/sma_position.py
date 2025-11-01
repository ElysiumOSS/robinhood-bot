"""This module contains the SMAPosition class."""

from dataclasses import dataclass

from src.data.position import Position


@dataclass
class SMAPosition(Position):
    """Data class representing a trading position with SMA-specific metrics."""

    short_term_sma: float
    long_term_sma: float
    current_momentum: float
    current_volatility: float
    trend_strength: float
