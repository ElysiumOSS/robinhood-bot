"""This module contains the trading strategies for the trading bot."""

import re

import numpy as np
import pandas as pd
import tweepy
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.api.ticker_to_company import TICKER_TO_COMPANY
from src.core.config import SentimentAnalysisConfig, TechnicalIndicatorsConfig
from src.utils.credentials import TwitterCredentials


def calculate_sma_signal(df: pd.DataFrame, config: TechnicalIndicatorsConfig) -> float:
    """Calculate SMA crossover signal."""
    short_sma = df["close"].rolling(window=config.sma_short_period).mean()
    long_sma = df["close"].rolling(window=config.sma_long_period).mean()

    if short_sma.iloc[-1] > long_sma.iloc[-1]:
        return 1.0
    if short_sma.iloc[-1] < long_sma.iloc[-1]:
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
    if current_price < vwap * (1 - threshold):
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
    if current_rsi > config.rsi_overbought:
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
    if macd.iloc[-1] < signal_line.iloc[-1]:
        return -1.0
    return 0.0


def calculate_volatility(df: pd.DataFrame) -> float:
    """Calculate historical volatility for position sizing."""
    if df.empty:
        return 0.0

    df["returns"] = df["close_price"].astype(float).pct_change()
    return df["returns"].std() * np.sqrt(252)


def calculate_sentiment_signal(ticker: str, config: SentimentAnalysisConfig) -> float:
    """
    Calculates a trading signal based on Twitter sentiment.
    Returns a float between -1.0 (strong sell) and 1.0 (strong buy).
    """
    if not config.enable_sentiment:
        return 0.0

    try:
        twitter_credentials = TwitterCredentials()
        if twitter_credentials.empty_credentials:
            print("Twitter credentials are not set. Skipping sentiment analysis.")
            return 0.0

        auth = tweepy.AppAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        company_name = TICKER_TO_COMPANY.get(ticker, ticker)
        query = f"({company_name} OR ${ticker}) lang:en -filter:retweets"

        tweets = tweepy.Cursor(
            api.search_tweets,
            q=query,
            lang="en",
            result_type="mixed",
            tweet_mode="extended",
        ).items(config.max_tweets_analyze)

        sentiment_scores = []
        vader_analyzer = SentimentIntensityAnalyzer()

        for tweet in tweets:
            clean_text = re.sub(r"http\S+|www\S+|https\S+", "", tweet.full_text, flags=re.MULTILINE)
            clean_text = re.sub(r"[@#$]\w+", "", clean_text)

            vader_score = vader_analyzer.polarity_scores(clean_text)["compound"]
            textblob_score = TextBlob(clean_text).sentiment.polarity

            # Combine scores
            combined_score = (vader_score * 0.7) + (textblob_score * 0.3)
            sentiment_scores.append(combined_score)

        if not sentiment_scores or len(sentiment_scores) < config.min_sentiment_samples:
            return 0.0

        avg_sentiment = np.mean(sentiment_scores)

        if avg_sentiment > config.sentiment_threshold_buy:
            return 1.0
        if avg_sentiment < config.sentiment_threshold_sell:
            return -1.0
        return 0.0

    except tweepy.TweepyException as e:
        print(f"Error in sentiment analysis for {ticker}: {e}")
        return 0.0
