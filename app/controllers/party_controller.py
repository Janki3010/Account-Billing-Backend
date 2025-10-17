from typing import Dict

from fastapi import APIRouter, Request, HTTPException
from fastapi_restful.cbv import cbv
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from app.schemas.party import PartyReq, PartyType
from app.services.party_service import PartyService

party_router = APIRouter(prefix="/party", tags=['party'])

@cbv(party_router)
class PartyController:
    def __init__(self):
        self.party_service = PartyService()

    @party_router.post("/create", status_code=HTTP_201_CREATED, summary="Create Party")
    def add_party(self, party_request: PartyReq):
        return self.party_service.create_party(party_request)

    @party_router.get("/get", status_code=HTTP_200_OK, summary="Get Party")
    def get_party(self, party_id: None|str):
        if party_id:
            return self.party_service.get_party_data(party_id)
        return HTTPException(status_code=400, detail="Need party Id")

    @party_router.get("/get-by-type", status_code=HTTP_200_OK, summary="Get all party by type filter")
    def get_party_by_type(self, type: PartyType):
        if type==PartyType.BOTH:
            return self.party_service.get_party_datas()
        return self.party_service.get_party_data_by_type(type)

    @party_router.get("/get-all", status_code=HTTP_200_OK, summary="Get all party datas")
    def get_all_party(self):
        return self.party_service.get_party_datas()

    @party_router.patch("/update")
    def update_party(self, party_id, update_request: Dict):
        party_update = self.party_service.update_party(party_id, update_request)
        if party_update:
            return {"message": "Party Data Updated Successfully!!"}, 200
        return {"message": "Getting error at a time of update party details"}, 400


    @party_router.delete("/delete")
    def delete_party(self, id: str):
        return self.party_service.delete_by_id(id)