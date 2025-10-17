from datetime import datetime
import io
from datetime import datetime
from fastapi import HTTPException
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
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

    #
    # def add_invoice(self, invoice_data: InvoiceCreate):
    #     invoice_number = self.generate_invoice_number()
    #
    #     total_amount = 0
    #     tax_amount = 0
    #     net_amount = 0
    #     total_gst = 0
    #     total_discount = 0
    #     invoice_items = []
    #     stock_updates = []
    #
    #     for item in invoice_data.items:
    #         product = self.item_repository.get_item_by_id(item.item_id)
    #         if not product:
    #             return {"message": f"Item not found"}, 404
    #
    #         if product.stock_quantity < item.quantity:
    #             return {"message": f"Not enough stock for {product.name}"}, 400
    #
    #         discount_cal = product.sale_price * item.quantity * ( item.discount / 100 ) if item.discount else 0
    #         line_total = (item.quantity * product.sale_price) - discount_cal
    #         tax = line_total * (product.gst_rate / 100) if product.gst_rate else 0
    #         amount = line_total + tax
    #
    #         total_amount += line_total
    #         tax_amount += tax
    #         net_amount += amount
    #         total_gst += product.gst_rate
    #         total_discount += item.discount
    #
    #         invoice_item = InvoiceItem(
    #             item_id=item.item_id,
    #             quantity=item.quantity,
    #             rate=product.sale_price,
    #             discount=item.discount,
    #             amount=amount
    #         )
    #         invoice_items.append(invoice_item)
    #
    #         stock_updates.append((item.item_id, item.quantity))  # save for later
    #
    #
    #     invoice = Invoice(
    #         party_id=invoice_data.party_id,
    #         invoice_date=invoice_data.invoice_date,
    #         invoice_number=invoice_number,
    #         total_amount=total_amount,
    #         tax_amount=tax_amount,
    #         net_amount=net_amount,
    #         total_gst=total_gst,
    #         total_discount=total_discount,
    #         status="unpaid",
    #         items=invoice_items
    #     )
    #
    #     for item_id, qty in stock_updates:
    #         updated = self.item_repository.update_stock(item_id, qty)
    #         if not updated:
    #             raise HTTPException(status_code=400, detail=f"Failed to update stock for {item_id}")
    #
    #     return self.invoice_repository.save(invoice)
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

    #
    # def generate_invoice_pdf(self, invoice_data):
    #     party_data = self.party_service.get_party_data(invoice_data.party_id)
    #     if not party_data:
    #         raise HTTPException(status_code=404, detail="Party not found")
    #
    #     buffer = io.BytesIO()
    #     doc = SimpleDocTemplate(
    #         buffer,
    #         pagesize=A4,
    #         rightMargin=30,
    #         leftMargin=30,
    #         topMargin=30,
    #         bottomMargin=30,
    #     )
    #
    #     styles = getSampleStyleSheet()
    #     normal = styles["Normal"]
    #     bold = ParagraphStyle(name="Bold", parent=normal, fontName="Helvetica-Bold")
    #
    #     elements = []
    #
    #     # === Header ===
    #     elements.append(Paragraph("<b>KUMAR MOBILE SHOP & REPAIRING CENTER</b>", styles["Title"]))
    #     elements.append(Paragraph("BRAHMA DARWAZA, NEAR PT. EENDYAL PARK, BB. NAGAR", normal))
    #     elements.append(Paragraph("Phone: 9634564658, 800618086 | Email:rahulkumar100499@gmailc.com", normal))
    #     elements.append(Paragraph("GSTIN: 09FKXPK6006E1ZS", normal))
    #     elements.append(Spacer(1, 10))
    #
    #     # === Invoice Header Row ===
    #     inv_info = [
    #         [
    #             Paragraph("<b>Tax Invoice</b>", bold),
    #             Paragraph(
    #                 f"<b>Invoice No:</b> {invoice_data.invoice_number}<br/><b>Dated:</b> {invoice_data.invoice_date}<br/><b>Place of Supply:</b> Uttar Pradesh (09)",
    #                 normal),
    #         ]
    #     ]
    #     table = Table(inv_info, colWidths=[3.5 * inch, 3.5 * inch])
    #     table.setStyle(TableStyle([
    #         ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    #         ("VALIGN", (0, 0), (-1, -1), "TOP"),
    #     ]))
    #     elements.append(table)
    #     elements.append(Spacer(1, 10))
    #
    #     # === Bill To / Ship To ===
    #     party_address = party_data.address if party_data.address else ""
    #     party_gst_no = party_data.gst_number if party_data.gst_number else ""
    #
    #     billing_table = Table(
    #         [
    #             [
    #                 Paragraph(
    #                     f"<b>Bill To:</b><br/>{party_data.name}<br/>{party_data.address}<br/>GSTIN: {party_data.gst_number}",
    #                     normal),
    #                 Paragraph(
    #                     f"<b>Ship To:</b><br/>{party_data.name}<br/>{party_address}<br/>Party Mobile No : {party_data.phone}<br/>GSTIN: {party_gst_no}",
    #                     normal),
    #             ]
    #         ],
    #         colWidths=[3.5 * inch, 3.5 * inch],
    #     )
    #     billing_table.setStyle(TableStyle([
    #         ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    #         ("VALIGN", (0, 0), (-1, -1), "TOP"),
    #     ]))
    #     elements.append(billing_table)
    #     elements.append(Spacer(1, 15))
    #
    #     # === Item Table ===
    #     table_data = [
    #         ["No", "Particulars", "HSN", "Qty", "Unit", "List Price", "Discount", "CGST", "SGST", "Amount ₹"]
    #     ]
    #
    #     for idx, item in enumerate(invoice_data.items, start=1):
    #         item_data = self.item_repository.get_item_by_id(str(item.item_id))
    #         table_data.append([
    #             str(idx),
    #             item_data.name,
    #             item_data.hsn_code or "-",
    #             str(item.quantity),
    #             "Pcs",
    #             f"{item.rate:.2f}",
    #             f"{item.discount:.2f}",
    #             f"{item_data.gst_rate / 2:.2f}%",
    #             f"{item_data.gst_rate / 2:.2f}%",
    #             f"{item.amount:.2f}",
    #         ])
    #
    #     item_table = Table(table_data, repeatRows=1)
    #     item_table.setStyle(TableStyle([
    #         ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    #         ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    #         ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    #         ("ALIGN", (3, 1), (-1, -1), "CENTER"),
    #         ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    #     ]))
    #     elements.append(item_table)
    #     elements.append(Spacer(1, 12))
    #
    #     # === Totals Section ===
    #     totals = [
    #         ["", "", "", "", "", "", "Total:", f"{invoice_data.total_amount:.2f}"],
    #         ["", "", "", "", "", "", "Discount:", f"{getattr(invoice_data, 'total_discount', 0):.2f}"],
    #         ["", "", "", "", "", "", "GST:", f"{getattr(invoice_data, 'total_gst', 0):.2f}"],
    #         ["", "", "", "", "", "", "Grand Total:", f"{invoice_data.net_amount:.2f}"],
    #     ]
    #     total_table = Table(totals, colWidths=[0.8 * inch] * 6 + [1.2 * inch, 1.2 * inch])
    #     total_table.setStyle(TableStyle([
    #         ("ALIGN", (-2, 0), (-1, -1), "RIGHT"),
    #         ("FONTNAME", (-2, -1), (-1, -1), "Helvetica-Bold"),
    #     ]))
    #     elements.append(total_table)
    #     elements.append(Spacer(1, 12))
    #
    #     elements.append(Paragraph(
    #         f"<b>Amount (In Words):</b> {self._number_to_words(invoice_data.net_amount)} only.",
    #         normal
    #     ))
    #     elements.append(Spacer(1, 15))
    #
    #     # === Terms, Bank Details, Signature ===
    #     footer_data = [
    #         [
    #             Paragraph("<b>Terms & Conditions</b><br/>1. Goods once sold will not be taken back.<br/>"
    #                       "2. Interest @18% p.a. will be charged if payment is not made on time.<br/>"
    #                       "3. Subject to Uttar Pradesh Jurisdiction only.", normal),
    #             Paragraph("<b>Bank Details</b><br/>Account No: 1234567890<br/>IFSC: ABCD0123456", normal),
    #             Paragraph("<b>For BusyApp Demo</b><br/><br/>Authorised Signatory", normal),
    #         ]
    #     ]
    #     footer_table = Table(footer_data, colWidths=[2.8 * inch, 2.2 * inch, 2.2 * inch])
    #     footer_table.setStyle(TableStyle([
    #         ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    #         ("VALIGN", (0, 0), (-1, -1), "TOP"),
    #     ]))
    #     elements.append(footer_table)
    #     elements.append(Spacer(1, 10))
    #     elements.append(Paragraph("Receiver’s Signature: ____________________", normal))
    #
    #     doc.build(elements)
    #     buffer.seek(0)
    #     return buffer
    #
    # def _number_to_words(self, amount):
    #     """Simple helper to convert numbers to words"""
    #     import num2words
    #     return num2words.num2words(amount, lang='en').capitalize()

    # def generate_invoice_pdf(self, invoice_data):
    #     party_data = self.party_service.get_party_data(invoice_data.party_id)
    #     if not party_data:
    #         raise HTTPException(status_code=404, detail="Party not found")
    #
    #     buffer = io.BytesIO()
    #     doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    #     elements = []
    #     styles = getSampleStyleSheet()
    #
    #     # Header
    #     elements.append(Paragraph("<b>shop name</b>", styles["Title"]))
    #     elements.append(Paragraph("shop address", styles["Normal"]))
    #     elements.append(Paragraph("Phone: 9899999999 | Email: shop@example.in", styles["Normal"]))
    #     elements.append(Paragraph("GSTIN: 09AAFCP0535R003", styles["Normal"]))
    #     elements.append(Spacer(1, 12))
    #
    #     # Invoice Info
    #     elements.append(Paragraph(f"<b>Tax Invoice</b>", styles["Heading2"]))
    #     elements.append(Paragraph(f"Invoice No.: {invoice_data.invoice_number}", styles["Normal"]))
    #     elements.append(
    #         Paragraph(f"Dated: {str(invoice_data.invoice_date)}",
    #                   styles["Normal"]))
    #     elements.append(Spacer(1, 8))
    #
    #     # Party Info
    #     elements.append(Paragraph(f"<b>Bill To:</b> {party_data.name}", styles["Normal"]))
    #     elements.append(Paragraph(party_data.address, styles["Normal"]))
    #     elements.append(Paragraph(f"Phone: {party_data.phone}", styles["Normal"]))
    #     elements.append(Paragraph(f"GSTIN: {party_data.gst_number}", styles["Normal"]))
    #     elements.append(Spacer(1, 10))
    #
    #     # Table Data
    #     table_data = [["No", "Particulars", "HSN", "IMEI_number" ,"Qty", "Rate", "Discount", "GST", "Amount"]]
    #
    #     for idx, item in enumerate(invoice_data.items, start=1):
    #         item_data = self.item_repository.get_item_by_id(str(item.item_id))
    #         table_data.append([
    #             str(idx),
    #             item_data.name,
    #             item_data.hsn_code,
    #             item_data.IMEI_number,
    #             str(item.quantity),
    #             item.rate,
    #             item.discount,
    #             item_data.gst_rate,
    #             item.amount,
    #         ])
    #
    #     table = Table(table_data, repeatRows=1)
    #     table.setStyle(TableStyle([
    #         ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    #         ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    #         ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    #         ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    #     ]))
    #     elements.append(table)
    #
    #     # Totals
    #     elements.append(Spacer(1, 12))
    #     elements.append(Paragraph(f"<b>Total:</b> ₹{invoice_data.total_amount}", styles["Normal"]))
    #     elements.append(Paragraph(f"<b>Discount:</b> ₹{invoice_data.total_discount}", styles["Normal"]))
    #     elements.append(Paragraph(f"<b>GST:</b> ₹{invoice_data.total_gst}", styles["Normal"]))
    #     elements.append(Paragraph(f"<b>Net Total:</b> ₹{invoice_data.net_amount}", styles["Normal"]))
    #     elements.append(Spacer(1, 12))
    #     # elements.append(
    #     #     Paragraph(f"<b>Amount (In Words):</b> {invoice_data.get('amount_in_words', '')}", styles["Normal"]))
    #
    #     # Footer
    #     elements.append(Spacer(1, 25))
    #     elements.append(Paragraph("Terms & Conditions:", styles["Heading4"]))
    #     elements.append(Paragraph("1. Goods once sold will not be taken back.", styles["Normal"]))
    #     elements.append(
    #         Paragraph("2. Interest @18% p.a. will be charged if payment is not made within stipulated time.",
    #                   styles["Normal"]))
    #     elements.append(Paragraph("3. Subject to Uttar Pradesh Jurisdiction only.", styles["Normal"]))
    #     elements.append(Spacer(1, 25))
    #     elements.append(Paragraph("Authorised Signatory", styles["Normal"]))
    #
    #     doc.build(elements)
    #     buffer.seek(0)
    #     return buffer

