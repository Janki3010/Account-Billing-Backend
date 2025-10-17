from app.models.payment import Payment
from app.repositories.base_repository import BaseRepository
from app.schemas.payment import PaymentRequest


class PaymentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Payment)

    def add_payment_data(self, payment_req: PaymentRequest):
        db_data = Payment(
            party_id = payment_req.party_id,
            invoice_id = payment_req.invoice_id,
            payment_mode = payment_req.payment_mode,
            amount = payment_req.amount,
            transaction_date = payment_req.transaction_date
        )

        return self.save(db_data)