import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, ForeignKey, Integer, Float

from app.models.base import BaseModel

class Item(BaseModel):
    __tablename__ = 'items'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    hsn_code = Column(String, nullable=True)
    IMEI_number = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    purchase_price = Column(Float, nullable=False)
    sale_price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    gst_rate = Column(Float, nullable=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
