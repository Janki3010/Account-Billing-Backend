from dataclasses import dataclass

@dataclass
class InvoiceStatus:
    PAID: str = "PAID"
    UNPAID: str = "UNPAID"
    CANCELLED: str = "CANCELLED"
    PARTIALLY_PAID: str = "PARTIALLY PAID"