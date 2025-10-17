from fastapi import APIRouter
from fastapi_restful.cbv import cbv
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from app.schemas.payment import PaymentRequest
from app.services.payment_service import PaymentService

payment_router = APIRouter(prefix="/payment", tags=["payment"])

@cbv(payment_router)
class PaymentController:
    def __init__(self):
        self.payment_service = PaymentService()

    @payment_router.post(
        "/create",
        status_code=HTTP_201_CREATED,
        summary="Create Payment"
    )
    def add_payment(self, payment_request: PaymentRequest):
        return self.payment_service.create_payment(payment_request)

    @payment_router.get(
        "/get-all",
        status_code=HTTP_200_OK,
        summary="Get all payment"
    )
    def get_all_payment(self):
        return self.payment_service.get_payments()

    def delete_payment(self, id: str):
        return self.payment_service.delete_by_id(id)

