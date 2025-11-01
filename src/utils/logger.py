"""This module contains the logger configuration for the trading bot."""

import logging

logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("trade_bot.log"),  # Log to a file named trade_bot.log
        logging.StreamHandler(),  # Also log to the console
    ],
)

logger = logging.getLogger(__name__)
