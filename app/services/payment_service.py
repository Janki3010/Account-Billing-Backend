from typing import Any

from fastapi import HTTPException

from app.config.constants import InvoiceStatus
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payment import PaymentRequest


class PaymentService:
    def __init__(self):
        self.payment_repository = PaymentRepository()
        self.invoice_repository = InvoiceRepository()

    def create_payment(self, payment_request: PaymentRequest):
        is_partial_payment = 0
        payment_data = self.payment_repository.get_all(filters={"invoice_id": payment_request.invoice_id})
        for payment in payment_data:
            is_partial_payment += payment.amount

        payment = self.payment_repository.add_payment_data(payment_request)

        if payment:
           invoice = self.invoice_repository.get_invoice_by_id(payment_request.invoice_id)
           total_amount = invoice.net_amount
           paid_amount = payment_request.amount

           if is_partial_payment:
               if is_partial_payment + payment_request.amount >= total_amount:
                   self.invoice_repository.update_by_id(payment.invoice_id, {"status": InvoiceStatus.PAID})
               else:
                  self.invoice_repository.update_by_id(payment.invoice_id, {"status": InvoiceStatus.PARTIALLY_PAID})
           elif paid_amount >= total_amount:
               self.invoice_repository.update_by_id(payment.invoice_id, {"status": InvoiceStatus.PAID})
           else:
               self.invoice_repository.update_by_id(payment.invoice_id, {"status": InvoiceStatus.PARTIALLY_PAID})
        return payment

    def get_payments(self) -> list[Any]:
        payment_datas = self.payment_repository.get_all()
        payments = []
        for payment in payment_datas:
            payments.append({
                "payment_id": payment.id,
                "invoice_id": payment.invoice_id,
                "payment_mode": payment.payment_mode,
                "amount": payment.amount,
                "transaction_date": payment.transaction_date
            })

        return payments

    def delete_by_id(self, id):
        data = self.payment_repository.get_by_id(id)
        if not data:
            raise HTTPException(status_code=400, detail=f"Payment data not found for this {id}")
        return self.payment_repository.delete_by_id(id)
