from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class InvoiceItemCreate(BaseModel):
    item_id: str
    quantity: int
    discount: Optional[float] = 0.0

class InvoiceCreate(BaseModel):
    party_id: str
    invoice_date: datetime
    items: List[InvoiceItemCreate]
    shop_id: str


class InvoiceItemResponse(BaseModel):
    item_id: str
    quantity: int
    discount: Optional[float] = 0.0

    class Config:
        orm_mode = True

class InvoiceResponse(BaseModel):
    id: str
    invoice_number: str
    total_amount: float
    tax_amount: Optional[float]
    net_amount: Optional[float]
    status: str
    invoice_date: datetime
    items: List[InvoiceItemResponse] = []

    class Config:
        orm_mode = True
