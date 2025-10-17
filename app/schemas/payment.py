from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from enum import Enum

class PaymentMode(str, Enum):
    cash = "cash"
    UPI = "UPI"
    card = "card"
    bank_transfer = "bank transfer"

class PaymentRequest(BaseModel):
    party_id: str
    invoice_id: Optional[str]
    payment_mode: PaymentMode
    amount: float
    transaction_date: datetime