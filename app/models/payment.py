import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Float, DateTime, ForeignKey

from app.models.base import BaseModel

class Payment(BaseModel):
    __tablename__ = 'payments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=True)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True)
    payment_mode = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)
