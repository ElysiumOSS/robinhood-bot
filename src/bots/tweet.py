
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright (C) 2021-2025
#
# All rights reserved.
#

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
