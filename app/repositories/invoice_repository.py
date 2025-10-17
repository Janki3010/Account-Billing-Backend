from sqlalchemy import func, cast, Date, extract
from sqlalchemy.orm import joinedload

from app.config.constants import InvoiceStatus
from app.models.invoice import Invoice
from app.repositories.base_repository import BaseRepository
from app.utils.db import get_db


class InvoiceRepository(BaseRepository):
    def __init__(self):
        super().__init__(Invoice)

    def get_last_invoice(self):
        last_invoice = 0
        invoice = self.get_all(order_by=Invoice.created_at.desc())
        if invoice:
            last_invoice = invoice[0].invoice_number
        return last_invoice

    def get_all_invoices(self):
        return self.get_all()

    def get_invoice_by_id(self, invoice_id):
        with get_db() as db:
            invoice = (
                db.query(self.__model__)
                .options(joinedload(self.__model__.items))
                .filter(self.__model__.id == invoice_id)
                .first()
            )
            return invoice

    def get_unpaid_invoices(self):
        invoices = self.get_all()
        unpaid_invoices = []
        for i in invoices:
            if i.status != InvoiceStatus.PAID:
                unpaid_invoices.append({
                    "id": i.id,
                    "party_id": i.party_id,
                    "invoice_date": i.invoice_date,
                    "invoice_number": i.invoice_number,
                    "total_amount": i.total_amount,
                    "tax_amount": i.tax_amount,
                    "net_amount": i.net_amount,
                    "status": i.status,
                })
        return unpaid_invoices


    def get_daily_sales(self, date):
        with get_db() as db:
            result = (
                db.query(func.sum(Invoice.total_amount).label("total_sales"))
                .filter(func.date(Invoice.created_at) == date)
                .scalar()
            )
            return result or 0

    def get_monthly_sales(self, year, month):
        with get_db() as db:
            result = (
                db.query(func.sum(Invoice.total_amount).label("total_sales"))
                .filter(func.extract("year", Invoice.created_at) == year)
                .filter(func.extract("month", Invoice.created_at) == month)
                .scalar()
            )
            return result or 0

    def get_yearly_sales(self, year):
        with get_db() as db:
            result = (
                db.query(func.sum(Invoice.total_amount).label("total_sales"))
                .filter(func.extract("year", Invoice.created_at) == year)
                .scalar()
            )
            return result or 0

    def get_sales_trend(self, start_date, end_date):
        with get_db() as db:
            result = (
                db.query(
                    cast(Invoice.created_at, Date).label("day"),
                    func.sum(Invoice.total_amount).label("total_sales")
                )
                .filter(Invoice.created_at >= start_date)
                .filter(Invoice.created_at <= end_date)
                .group_by("day")
                .order_by("day")
                .all()
            )
            return result

    def get_yearly_sales_summary(self):
        with get_db() as db:
            results = (
                db.query(
                    extract("year", Invoice.created_at).label("year"),
                    func.sum(Invoice.total_amount).label("total_sales"),
                )
                .group_by(extract("year", Invoice.created_at))
                .order_by(extract("year", Invoice.created_at))
                .all()
            )
            return [{"year": int(r[0]), "total_sales": float(r[1])} for r in results]