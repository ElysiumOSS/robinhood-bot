"""This module contains the OrderResult class."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class OrderResult:
    """Data class representing the result of a trading order."""

    success: bool
    order_id: Optional[str] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    amount: float = 0.0
    price: float = 0.0
    timestamp: datetime = datetime.now(timezone.utc)
