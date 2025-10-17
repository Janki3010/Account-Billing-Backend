import uuid
from sqlalchemy import UUID, Column, ForeignKey, String, Float, Integer, DateTime
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Invoice(BaseModel):
    __tablename__ = 'invoices'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=True)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shop_profiles.id"), nullable=True)
    invoice_date = Column(DateTime, nullable=False)
    invoice_number = Column(String, unique=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=True)
    net_amount = Column(Float, nullable=True)
    total_gst = Column(Float, nullable=True)
    total_discount = Column(Float, nullable=True)
    status = Column(String, default='unpaid')

    items = relationship("InvoiceItem", backref="invoice", cascade="all, delete-orphan")

class InvoiceItem(BaseModel):
    __tablename__ = "invoice_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    rate = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    cgst_rate = Column(Float, nullable=True, default=9.0)
    sgst_rate = Column(Float, nullable=True, default=9.0)
    cgst_amount = Column(Float, nullable=True, default=0.0)
    sgst_amount = Column(Float, nullable=True, default=0.0)
    amount = Column(Float, nullable=False)


# CREATE TABLE invoices (
#     invoice_id INT AUTO_INCREMENT PRIMARY KEY,
#     party_id INT NOT NULL,
#     invoice_date DATE NOT NULL,
#     invoice_number VARCHAR(50) UNIQUE NOT NULL,
#     total_amount DECIMAL(12,2) NOT NULL,
#     tax_amount DECIMAL(12,2) NOT NULL,
#     net_amount DECIMAL(12,2) NOT NULL,
#     status ENUM('paid','unpaid','partial') DEFAULT 'unpaid',
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (party_id) REFERENCES parties(party_id)
# );

# CREATE TABLE invoice_items (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     invoice_id INT NOT NULL,
#     item_id INT NOT NULL,
#     quantity INT NOT NULL,
#     rate DECIMAL(12,2) NOT NULL,
#     discount DECIMAL(12,2) DEFAULT 0.00,
#     amount DECIMAL(12,2) NOT NULL,
#     FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id),
#     FOREIGN KEY (item_id) REFERENCES items(item_id)
# );
