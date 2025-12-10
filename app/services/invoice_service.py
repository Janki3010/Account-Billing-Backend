from datetime import datetime
from fastapi import HTTPException

from app.config.constants import InvoiceStatus
from app.models.invoice import InvoiceItem, Invoice
from app.repositories.invoice_item_repositor import InvoiceItemRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.item_repository import ItemRepository
from app.schemas.invoice import InvoiceCreate, InvoiceResponse
from app.services.party_service import PartyService


class InvoiceService:
    def __init__(self):
        self.invoice_repository = InvoiceRepository()
        self.invoice_item_repository = InvoiceItemRepository()
        self.item_repository = ItemRepository()
        self.party_service = PartyService()

    def generate_invoice_number(self) -> str:
        year = datetime.now().year
        prefix = f"INV-{year}"

        last_invoice = self.invoice_repository.get_last_invoice()

        if last_invoice:
            try:
                last_number = int(last_invoice.split("-")[-1])
            except:
                last_number = 0
        else:
            last_number = 0

        new_number = last_number + 1
        return f"{prefix}-{new_number:04d}"

    def add_invoice(self, invoice_data: InvoiceCreate):
        invoice_number = self.generate_invoice_number()

        total_amount = 0
        total_cgst = 0
        total_sgst = 0
        total_discount = 0
        net_amount = 0
        invoice_items = []
        stock_updates = []

        for item in invoice_data.items:
            product = self.item_repository.get_item_by_id(item.item_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Item not found: {item.item_id}")

            if product.stock_quantity < item.quantity:
                raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")

            base_price = product.sale_price * item.quantity
            discount_value = base_price * (item.discount / 100) if item.discount else 0
            taxable_value = base_price - discount_value

            gst_rate = product.gst_rate or 0.0
            cgst_rate = gst_rate / 2
            sgst_rate = gst_rate / 2

            cgst_amount = taxable_value * (cgst_rate / 100)
            sgst_amount = taxable_value * (sgst_rate / 100)
            total_tax = cgst_amount + sgst_amount

            line_total = taxable_value + total_tax

            total_amount += taxable_value
            total_cgst += cgst_amount
            total_sgst += sgst_amount
            total_discount += discount_value
            net_amount += line_total

            invoice_item = InvoiceItem(
                item_id=item.item_id,
                quantity=item.quantity,
                rate=product.sale_price,
                discount=item.discount,
                cgst_rate=cgst_rate,
                sgst_rate=sgst_rate,
                cgst_amount=cgst_amount,
                sgst_amount=sgst_amount,
                amount=line_total
            )
            invoice_items.append(invoice_item)

            stock_updates.append((item.item_id, item.quantity))

        invoice = Invoice(
            party_id=invoice_data.party_id,
            shop_id=invoice_data.shop_id,
            invoice_date=invoice_data.invoice_date,
            invoice_number=invoice_number,
            total_amount=total_amount,
            tax_amount=total_cgst + total_sgst,
            net_amount=net_amount,
            total_gst=(total_cgst + total_sgst) / total_amount * 100 if total_amount else 0,
            total_discount=total_discount,
            status=InvoiceStatus.UNPAID,
            items=invoice_items
        )

        for item_id, qty in stock_updates:
            updated = self.item_repository.update_stock(item_id, qty)
            if not updated:
                raise HTTPException(status_code=400, detail=f"Failed to update stock for {item_id}")

        return self.invoice_repository.save(invoice)

    def get_all_invoices(self) -> InvoiceResponse:
        return self.invoice_repository.get_all_invoices()

    def get_invoice(self, invoice_id) -> InvoiceResponse:
        return self.invoice_repository.get_invoice_by_id(invoice_id)

    def get_partially_or_unpaid(self):
        return self.invoice_repository.get_unpaid_invoices()

    def delete_by_id(self, id):
        data = self.invoice_repository.get_invoice_by_id(id)
        if not data:
            raise HTTPException(status_code=400, detail=f"Invoice data not found for this {id}")
        return self.invoice_repository.delete_by_id(id)
