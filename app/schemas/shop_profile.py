from typing import Optional

from pydantic import Field, BaseModel


class ShopProfileReq(BaseModel):
    shop_name: str = Field(..., min_length=1, max_length=100, description="Shop Name")
    gstin: str = Field(..., description="gst number")
    address: str = Field(..., description="shop address")
    phone: str = Field(..., description="phone number")
    email: str = Field(..., description="email")
    bank_name: str = Field(..., description="Bank name")
    account_number: str = Field(..., description="Bank account number")
    ifsc_code: str = Field(..., description="IFSC code")
    qr_code_url: str = Field(..., description="QR code url")
    authorized_signatory: str = Field(..., description="Authorized signatory")

class ShopProfile(BaseModel):
    id: str
    shop_name: str
    gstin: Optional[str]
    address: str
    phone: str
    email: Optional[str]
    bank_name: Optional[str]
    account_number: Optional[str]
    ifsc_code:  Optional[str]
    qr_code_url:  Optional[str]
    authorized_signatory: Optional[str]
