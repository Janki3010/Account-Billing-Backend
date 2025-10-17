import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String

from app.models.base import BaseModel

class Party(BaseModel):
    __tablename__ = 'parties'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False, default='customer')
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    gst_number = Column(String, nullable=True)
