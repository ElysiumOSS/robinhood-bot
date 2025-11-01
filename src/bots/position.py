
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright (C) 2021-2025
#
# All rights reserved.
#

from dataclasses import dataclass


@dataclass
class Position:
    """Data class representing a trading position."""

    quantity: float
    average_buy_price: float
    current_price: float
    equity: float
    unrealized_pl: float
    unrealized_pl_pct: float
    highest_price: float
