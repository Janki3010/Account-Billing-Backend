from fastapi import APIRouter, HTTPException
from fastapi_restful.cbv import cbv
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from app.schemas.item import ItemRequest, UpdateRequest
from app.services.item_service import ItemService

item_router = APIRouter(prefix="/item", tags=['Item'])

@cbv(item_router)
class ItemController:
    def __init__(self):
        self.item_service = ItemService()

    @item_router.post("/create", status_code=HTTP_201_CREATED, summary="Create Item")
    def save_item(self, item_request: ItemRequest):
        return self.item_service.create_item(item_request)

    @item_router.get("/get", status_code=HTTP_200_OK, summary="Get Item")
    def get_item(self, item_id: str):
        if item_id:
            return self.item_service.get_item_data(item_id)
        return HTTPException(status_code=400, detail="Need item Id")

    @item_router.get("/get-by-company", status_code=HTTP_200_OK, summary="Get all items by category filter")
    def get_item_by_company(self, company_name: str):
        if company_name=="all":
            return self.item_service.get_item_datas()
        return self.item_service.get_item_data_by_company_name(company_name)

    @item_router.get("/get-all", status_code=HTTP_200_OK, summary="Get all items datas")
    def get_all_items(self):
        return self.item_service.get_item_datas()

    @item_router.put("/update")
    def update_item(self, update_request: UpdateRequest):
        item_update = self.item_service.update_item(update_request)
        if item_update:
            return {"message": "Item Data Updated Successfully!!"}, 200
        return {"message": "Getting error at a time of update Item details"}, 400

    @item_router.delete("/delete")
    def delete_item(self, id: str):
        return self.item_service.delete_by_id(id)