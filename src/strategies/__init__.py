from __future__ import absolute_import

__version__ = "1.0.0"
__author__ = "Mike Odnis"
__email__ = "mike@mikeodnis.dev"
__license__ = "MIT License"
__credits__ = ""

from .simple_moving_average import TradeBotSimpleMovingAverage
from .vwap_bot import TradeBotVWAP
from .trading_strategies import (
    calculate_macd_signal,
    calculate_rsi_signal,
    calculate_sentiment_signal,
    calculate_sma_signal,
    calculate_volatility,
    calculate_vwap_signal,
)

__all__ = [
    "TradeBotSimpleMovingAverage",
    "TradeBotVWAP",
    "calculate_macd_signal",
    "calculate_rsi_signal",
    "calculate_sentiment_signal",
    "calculate_sma_signal",
    "calculate_volatility",
    "calculate_vwap_signal",
]
