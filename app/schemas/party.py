from enum import Enum

from pydantic import BaseModel, Field, EmailStr


class PartyType(str, Enum):
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    BOTH = "both"

class PartyReq(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Party Name")
    type: PartyType = Field(..., description="Party Type")
    phone: str = Field(..., description="Phone")
    email:  EmailStr = Field(..., description="User email")
    address: str = Field(..., description="Full Address")
    gst_number: str = Field(..., description="GST Number")
