#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class TwitterCredentials:
    """A class to hold Twitter API credentials."""

    consumer_key: str = os.getenv("TWITTER_CONSUMER_KEY")
    consumer_secret: str = os.getenv("TWITTER_CONSUMER_SECRET")

    @property
    def empty_credentials(self) -> bool:
        """Returns True is any credential is empty; False otherwise"""
        return not (bool(self.consumer_key) and bool(self.consumer_secret))


@dataclass
class RobinhoodCredentials:
    """A class to hold Robinhood API credentials."""

    user: str = os.getenv("ROBINHOOD_USER")
    password: str = os.getenv("ROBINHOOD_PASS")
    mfa_code: str = os.getenv("ROBINHOOD_MFA_CODE")

    def __post_init__(self):
        print(f"Loaded credentials: User={self.user}")

    @property
    def empty_credentials(self) -> bool:
        """Returns True is any credential is empty; False otherwise"""
        return not (bool(self.user) and bool(self.password) and bool(self.mfa_code))
