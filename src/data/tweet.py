"""This module contains the Tweet class."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Tweet:
    """Data class representing a tweet."""

    text: str
    created_at: datetime
    user_followers: int
    retweet_count: int
    favorite_count: int
