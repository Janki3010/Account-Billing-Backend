from app.models.invoice import InvoiceItem
from app.repositories.base_repository import BaseRepository


class InvoiceItemRepository(BaseRepository):
    def __init__(self):
        super().__init__(InvoiceItem)

