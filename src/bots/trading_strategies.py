# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright (C) 2021-2025
#
# All rights reserved.
#
import numpy as np
import pandas as pd

from src.bots.config import TechnicalIndicatorsConfig


def calculate_sma_signal(df: pd.DataFrame, config: TechnicalIndicatorsConfig) -> float:
    """Calculate SMA crossover signal."""
    short_sma = df["close"].rolling(window=config.sma_short_period).mean()
    long_sma = df["close"].rolling(window=config.sma_long_period).mean()

    if short_sma.iloc[-1] > long_sma.iloc[-1]:
        return 1.0
    elif short_sma.iloc[-1] < long_sma.iloc[-1]:
        return -1.0
    return 0.0


def calculate_vwap_signal(df: pd.DataFrame, config: TechnicalIndicatorsConfig) -> float:
    """Calculate VWAP signal."""
    df["vwap"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
    current_price = df["close"].iloc[-1]
    vwap = df["vwap"].iloc[-1]

    threshold = config.vwap_threshold
    if current_price > vwap * (1 + threshold):
        return -1.0
    elif current_price < vwap * (1 - threshold):
        return 1.0
    return 0.0


def calculate_rsi_signal(df: pd.DataFrame, config: TechnicalIndicatorsConfig) -> float:
    """Calculate RSI signal."""
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=config.rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=config.rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    current_rsi = rsi.iloc[-1]
    if current_rsi < config.rsi_oversold:
        return 1.0
    elif current_rsi > config.rsi_overbought:
        return -1.0
    return 0.0


def calculate_macd_signal(df: pd.DataFrame, config: TechnicalIndicatorsConfig) -> float:
    """Calculate MACD signal."""
    short_ema = df["close"].ewm(span=config.macd_short_period, adjust=False).mean()
    long_ema = df["close"].ewm(span=config.macd_long_period, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=config.macd_signal_period, adjust=False).mean()

    if macd.iloc[-1] > signal_line.iloc[-1]:
        return 1.0
    elif macd.iloc[-1] < signal_line.iloc[-1]:
        return -1.0
    return 0.0


def calculate_volatility(df: pd.DataFrame) -> float:
    """Calculate historical volatility for position sizing."""
    if df.empty:
        return 0.0

    df["returns"] = df["close_price"].astype(float).pct_change()
    return df["returns"].std() * np.sqrt(252)