import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String

from app.models.base import BaseModel


class Company(BaseModel):
    __tablename__ = 'companies'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)