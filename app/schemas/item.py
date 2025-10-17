from pydantic import Field, BaseModel


class ItemRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Item Name")
    description: str = Field(..., description="Item description")
    hsn_code: str = Field(..., description="Item hsn code")
    IMEI_number: str = Field(..., description="Item IMEI number")
    unit: str = Field(..., description="Item unit")
    purchase_price: float = Field(..., description="Item purchase price")
    sale_price: float = Field(..., description="Item sale price")
    stock_quantity: int = Field(..., description="Item stock Quantity")
    gst_rate: float = Field(..., description="Gst rate")
    # company_name: str = Field(..., description="Company name of the item")
    company_id: str = Field(..., description="company Id")

class UpdateRequest(BaseModel):
    id: str
    name: str
    description: str
    hsn_code: str
    IMEI_number: str
    unit: str
    purchase_price: float
    sale_price: float
    stock_quantity: int
    gst_rate: float
    company_id: str
