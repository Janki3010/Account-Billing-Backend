from sqlalchemy import func, extract

from app.models.invoice import InvoiceItem, Invoice
from app.models.items import Item
from app.repositories.base_repository import BaseRepository
from app.utils.db import get_db


class ItemRepository(BaseRepository):
    def __init__(self):
        super().__init__(Item)

    def add_party_data(self, data):
        db_data = Item(
            name=data.name,
            description=data.description,
            hsn_code=data.hsn_code,
            IMEI_number=data.IMEI_number,
            unit=data.unit,
            purchase_price=data.purchase_price,
            sale_price=data.sale_price,
            stock_quantity=data.stock_quantity,
            gst_rate=data.gst_rate,
            company_id=data.company_id
        )
        return self.save(db_data)

    def get_all_items(self):
        return self.get_all()

    def get_item_by_id(self, item_id):
        return self.get_by_id(item_id)


    def update_stock(self, item_id, qty):
        item = self.get_item_by_id(item_id)
        item_stock = item.stock_quantity
        stock = item_stock - qty
        return self.update_by_id(item_id, {"stock_quantity": stock})


    def get_top_products(self, limit=5):
        with get_db() as db:
            result = (
                db.query(
                    Item.name,
                    func.sum(InvoiceItem.quantity).label("total_sold")
                )
                .join(InvoiceItem, InvoiceItem.item_id == Item.id)
                .group_by(Item.id)
                .order_by(func.sum(InvoiceItem.quantity).desc())
                .limit(limit)
                .all()
            )
            return result

    def get_low_stock_products(self, threshold=3):
        with get_db() as db:
            return db.query(Item).filter(Item.stock_quantity <= threshold).all()

    def get_top_products_by_year(self, year: int, limit: int = 5):
        with get_db() as db:
            result = (
                db.query(
                    Item.name,
                    func.sum(InvoiceItem.quantity).label("total_sold")
                )
                .join(InvoiceItem, InvoiceItem.item_id == Item.id)
                .join(Invoice, Invoice.id == InvoiceItem.invoice_id)
                .filter(extract("year", Invoice.created_at) == year)
                .group_by(Item.id)
                .order_by(func.sum(InvoiceItem.quantity).desc())
                .limit(limit)
                .all()
            )
            return result


