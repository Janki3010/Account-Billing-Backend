from fastapi import APIRouter, HTTPException
from fastapi_restful.cbv import cbv
from starlette.responses import StreamingResponse
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from app.schemas.invoice import InvoiceCreate
from app.services.invoice_pdf_service import InvoicePDFService
from app.services.invoice_service import InvoiceService

invoice_router = APIRouter(prefix="/invoice", tags=["invoice"])

@cbv(invoice_router)
class InvoiceController:
    def __init__(self):
        self.invoice_service = InvoiceService()
        self.invoice_pdf_service = InvoicePDFService()

    @invoice_router.post(
        "/create",
        status_code=HTTP_201_CREATED,
        summary="Create Invoice"
    )
    def create_invoice(self, invoice_request: InvoiceCreate):
        return self.invoice_service.add_invoice(invoice_request)

    @invoice_router.get(
        "/get-all",
        status_code=HTTP_200_OK,
        summary="Get Invoice"
    )
    def get_invoices(self):
        return self.invoice_service.get_all_invoices()

    @invoice_router.get(
        "/get",
        status_code=HTTP_200_OK,
        summary="Get Invoice By Invoice Id"
    )
    def get_invoice_by_id(self, invoice_id):
        return self.invoice_service.get_invoice(invoice_id)

    @invoice_router.get(
        "/get-all-unpaid",
        status_code=HTTP_200_OK,
        summary="Get only unpaid & partially paid invoices"
    )
    def get_unpaid_invoice(self):
        return self.invoice_service.get_partially_or_unpaid()

    @invoice_router.delete(
        "/delete"
    )
    def delete_invoice(self, id: str):
        return self.invoice_service.delete_by_id(id)

    @invoice_router.get(
        "/get-invoice-pdf"
    )
    def get_invoice_pdf(self, invoice_id: str):
        invoice_data = self.invoice_service.get_invoice(invoice_id)
        if not invoice_data:
            raise HTTPException(status_code=404, detail="Invoice not found")

        pdf_buffer = self.invoice_pdf_service.generate_invoice_pdf(invoice_data)
        pdf_buffer.seek(0)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=Invoice_{invoice_data.invoice_number}.pdf"},
        )

