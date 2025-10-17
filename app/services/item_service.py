from fastapi import HTTPException
from app.repositories.comapny_repository import CompanyRepository
from app.repositories.item_repository import ItemRepository


class ItemService:
    def __init__(self):
        self.item_repository = ItemRepository()
        self.company_repository = CompanyRepository()

    def create_item(self, item_request):
        return self.item_repository.add_party_data(item_request)
        # company_id = self.company_repository.get_company_id(item_request.company_name)
        # return self.item_repository.add_party_data(item_request, company_id)

    def get_item_data(self, item_id: str):
        return self.item_repository.get_by_id(item_id)

    def get_item_datas(self):
        datas = self.item_repository.get_all_items()
        item_datas = []
        for data in datas:
            item_datas.append(
                {
                    "item_id": data.id,
                    "name": data.name,
                    "description": data.description,
                    "hsn_code": data.hsn_code,
                    "IMEI_number": data.IMEI_number,
                    "unit": data.unit,
                    "purchase_price": data.purchase_price,
                    "sale_price": data.sale_price,
                    "stock_quantity": data.stock_quantity,
                    "gst_rate": data.gst_rate,
                    "company_id": data.company_id,
                    "company_name": self.company_repository.get_company_name(data.company_id)
                }
            )
        return item_datas

    def get_item_data_by_company_name(self, company_name: str):
        company_id = self.company_repository.get_company_id(company_name)
        return self.item_repository.get_all(filters={"company_id": company_id})

    def update_item(self, data):
        update_data = {
            "name": data.name,
            "description": data.description,
            "hsn_code": data.hsn_code,
            "unit": data.unit,
            "purchase_price": data.purchase_price,
            "sale_price": data.sale_price,
            "stock_quantity": data.stock_quantity,
            "gst_rate": data.gst_rate,
            "company_id": data.company_id
        }
        return self.item_repository.update_by_id(data.id, update_data)

    def delete_by_id(self, id):
        data = self.item_repository.get_item_by_id(id)
        if not data:
            raise HTTPException(status_code=400, detail=f"Item data not found for this {id}")
        return self.item_repository.delete_by_id(id)
