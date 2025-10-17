from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import io
from num2words import num2words
from fastapi import HTTPException

from app.repositories.item_repository import ItemRepository
from app.services.invoice_service import InvoiceService
from app.services.party_service import PartyService
from app.services.shop_profile_service import ShopProfileService


class InvoicePDFService:
    def __init__(self):
        self.invoice_service = InvoiceService()
        self.party_service = PartyService()
        self.shop_service = ShopProfileService()
        self.item_repository = ItemRepository()

    def generate_invoice_pdf(self, invoice_data):
        party = self.party_service.get_party_data(invoice_data.party_id)
        if not party:
            raise HTTPException(status_code=404, detail="Party not found")
        shop = self.shop_service.get_details_by_id(invoice_data.shop_id)
        if not shop:
            raise HTTPException(status_code=404, detail="Shop not found")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=25, bottomMargin=25)
        styles = getSampleStyleSheet()
        normal = styles["Normal"]
        bold = ParagraphStyle(name="Bold", parent=normal, fontName="Helvetica-Bold", fontSize=10)
        small = ParagraphStyle(name="Small", parent=normal, fontSize=8)

        elements = []

        # === HEADER ===
        elements.append(Paragraph(f"<b>{shop.get("shop_name").upper()}</b>", ParagraphStyle(name="Title", fontSize=14, alignment=1)))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(shop.get("address") or "", normal))
        elements.append(Paragraph(f"Tel: {shop.get("phone")} | Email: {shop.get("email")}", normal))
        elements.append(Paragraph(f"GSTIN: {shop.get("gstin")}", normal))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("<b>TAX INVOICE</b>", ParagraphStyle(name="Center", alignment=1)))
        elements.append(Spacer(1, 8))

        # === INVOICE INFO ===
        info_data = [
            ["Invoice No.", invoice_data.invoice_number, "Date", invoice_data.invoice_date.strftime("%d-%m-%Y")],
            ["Place of Supply", "Uttar Pradesh (09)", "Reverse Charge", "N"]
        ]
        info_table = Table(info_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch])
        info_table.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.black)]))
        elements.append(info_table)
        elements.append(Spacer(1, 10))

        # === BILL TO / SHIP TO ===
        bill_ship = [
            [
                Paragraph(f"<b>Billed To:</b><br/>{party.name}<br/>{party.address}<br/>Phone: {party.phone}", small),
                Paragraph(f"<b>Shipped To:</b><br/>{party.name}<br/>{party.address}<br/>Phone: {party.phone}", small)
            ]
        ]
        bt_table = Table(bill_ship, colWidths=[3.8*inch, 3.8*inch])
        bt_table.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.black)]))
        elements.append(bt_table)
        elements.append(Spacer(1, 10))

        # === ITEM TABLE ===
        item_header_style = ParagraphStyle(name="TableHeader", fontName="Helvetica-Bold", fontSize=8, alignment=1)
        item_cell_style = ParagraphStyle(name="TableCell", fontSize=8, alignment=1)
        item_desc_style = ParagraphStyle(name="TableDesc", fontSize=8, alignment=0)

        items_header = [
            Paragraph("S/N", item_header_style),
            Paragraph("Description<br/>of Goods", item_header_style),
            Paragraph("HSN/SAC<br/>Code", item_header_style),
            Paragraph("Qty", item_header_style),
            Paragraph("Unit", item_header_style),
            Paragraph("Price<br/>", item_header_style),
            Paragraph("CGST<br/>Rate", item_header_style),
            Paragraph("CGST<br/>Amt", item_header_style),
            Paragraph("SGST<br/>Rate", item_header_style),
            Paragraph("SGST<br/>Amt", item_header_style),
            Paragraph("Amount<br/>", item_header_style),
        ]
        table_data = [items_header]

        for idx, item in enumerate(invoice_data.items, 1):
            item_data = self.item_repository.get_item_by_id(str(item.item_id))
            row = [
                Paragraph(str(idx), item_cell_style),
                Paragraph(item_data.name, item_desc_style),
                Paragraph(item_data.hsn_code or "-", item_cell_style),
                Paragraph(str(item.quantity), item_cell_style),
                Paragraph("Pcs", item_cell_style),
                Paragraph(f"{item.rate:.2f}", item_cell_style),
                Paragraph(f"{item.cgst_rate:.2f}%", item_cell_style),
                Paragraph(f"{item.cgst_amount:.2f}", item_cell_style),
                Paragraph(f"{item.sgst_rate:.2f}%", item_cell_style),
                Paragraph(f"{item.sgst_amount:.2f}", item_cell_style),
                Paragraph(f"{item.amount:.2f}", item_cell_style),
            ]
            table_data.append(row)

        item_table = Table(
            table_data,
            repeatRows=1,
            colWidths=[
                0.4 * inch,  # S/N
                1.7 * inch,  # Description
                0.7 * inch,  # HSN/SAC
                0.5 * inch,  # Qty
                0.5 * inch,  # Unit
                0.8 * inch,  # Price
                0.6 * inch,  # CGST Rate
                0.6 * inch,  # CGST Amt
                0.6 * inch,  # SGST Rate
                0.6 * inch,  # SGST Amt
                0.9 * inch,  # Amount
            ],
        )
        item_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))

        elements.append(item_table)
        elements.append(Spacer(1, 10))

        # === TOTALS ===
        total_data = [
            ["Taxable Amt", f"{invoice_data.total_amount:.2f}"],
            ["Total CGST", f"{invoice_data.tax_amount/2:.2f}"],
            ["Total SGST", f"{invoice_data.tax_amount/2:.2f}"],
            ["Grand Total", f"{invoice_data.net_amount:.2f}"],
        ]
        total_table = Table(total_data, colWidths=[6.4*inch, 1.4*inch])
        total_table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.25, colors.black),
            ("FONTNAME", (-2,-1), (-1,-1), "Helvetica-Bold"),
            ("ALIGN", (-1,0), (-1,-1), "RIGHT")
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 10))

        elements.append(Paragraph(f"<b>Rupees {num2words(invoice_data.net_amount, lang='en').title()} Only</b>", normal))
        elements.append(Spacer(1, 15))

        # === BANK DETAILS / TERMS ===
        footer = [
            [
                Paragraph("<b>Bank Details</b><br/>"
                          f"Bank: {shop.get("bank_name")}<br/>"
                          f"A/C: {shop.get("account_number")}<br/>"
                          f"IFSC: {shop.get("ifsc_code")}", small),
                Paragraph("<b>Terms & Conditions</b><br/>1. Goods once sold will not be taken back.<br/>"
                          "2. Customer must go to service center for service.<br/>"
                          "3. Subject to local jurisdiction only.", small),
                Paragraph(f"For {shop.get("shop_name")}<br/><br/><br/>Authorised Signatory", small),
            ]
        ]
        footer_table = Table(footer, colWidths=[2.6*inch, 3.2*inch, 2.4*inch])
        footer_table.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.25, colors.black)]))
        elements.append(footer_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer
