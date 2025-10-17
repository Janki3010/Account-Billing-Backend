from datetime import date, timedelta

from app.repositories.invoice_item_repositor import InvoiceItemRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.party_repository import PartyRepository


class ReportService:
    def __init__(self):
        self.invoice_repo = InvoiceRepository()
        self.invoice_item_repo = InvoiceItemRepository()
        self.party_repository = PartyRepository()
        self.item_repository = ItemRepository()

    def get_dashboard_data(self, year: int, month: int, start_date: date, end_date: date):
        daily_sales = self.invoice_repo.get_daily_sales(date.today())
        monthly_sales = self.invoice_repo.get_monthly_sales(year, month)
        yearly_sales = self.invoice_repo.get_yearly_sales(year)
        top_customers = self.party_repository.get_top_customers(limit=5)
        top_products = self.item_repository.get_top_products(limit=5)
        low_stock = self.item_repository.get_low_stock_products()
        sales_trend = self.invoice_repo.get_sales_trend(date.today() - timedelta(days=30), date.today())

        yearly_summary = self.invoice_repo.get_yearly_sales_summary()

        return {
            "daily_sales": daily_sales,
            "monthly_sales": monthly_sales,
            "yearly_sales": yearly_sales,
            "top_customers": [
                {"name": c[0], "total_spent": float(c[1])} for c in top_customers
            ],
            "top_products": [
                {"name": p[0], "total_sold": int(p[1])} for p in top_products
            ],
            "low_stock": [{"name": p.name, "stock": p.stock_quantity} for p in low_stock],
            "sales_trend": [
                {"date": str(row[0]), "total": float(row[1])} for row in sales_trend
            ],
            "yearly_summary": yearly_summary,
        }


