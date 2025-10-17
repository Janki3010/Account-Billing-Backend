from sqlalchemy import func, extract

from app.models.invoice import Invoice
from app.models.party import Party
from app.repositories.base_repository import BaseRepository
from app.utils.db import get_db


class PartyRepository(BaseRepository):
    def __init__(self):
        super().__init__(Party)

    def add_party_data(self, party_request):
        db_data = Party(
            name=party_request.name,
            type=party_request.type,
            phone=party_request.phone,
            email=party_request.email,
            address=party_request.address,
            gst_number=party_request.gst_number
        )
        return self.save(db_data)

    def get_top_customers(self, limit=5):
        with get_db() as db:
            result = (
                db.query(
                    Party.name,
                    func.sum(Invoice.total_amount).label("total_spent")
                )
                .join(Invoice, Invoice.party_id == Party.id)
                .group_by(Party.id)
                .order_by(func.sum(Invoice.total_amount).desc())
                .limit(limit)
                .all()
            )
            return result

    def get_top_customers_by_year(self, year: int, limit: int = 5):
        with get_db() as db:
            result = (
                db.query(
                    Party.name,
                    func.sum(Invoice.total_amount).label("total_spent")
                )
                .join(Invoice, Invoice.party_id == Party.id)
                .filter(extract("year", Invoice.created_at) == year)
                .group_by(Party.id)
                .order_by(func.sum(Invoice.total_amount).desc())
                .limit(limit)
                .all()
            )
            return result