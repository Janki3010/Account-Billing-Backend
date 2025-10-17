import uuid
from sqlalchemy import UUID, Column, String
from app.models.base import BaseModel


class ShopProfile(BaseModel):
    __tablename__ = "shop_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_name = Column(String, nullable=False)
    gstin = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=True)
    qr_code_url = Column(String, nullable=True)
    authorized_signatory = Column(String, nullable=True)
