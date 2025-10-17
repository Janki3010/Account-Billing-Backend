import json

from fastapi import HTTPException

from app.repositories.party_repository import PartyRepository


class PartyService:
    def __init__(self):
        self.party_repository = PartyRepository()

    def create_party(self, party_request):
        return self.party_repository.add_party_data(party_request)

    def get_party_data(self, party_id: str):
        return self.party_repository.get_by_id(party_id)

    def get_party_datas(self):
        datas = self.party_repository.get_all()
        party_datas = []
        for data in datas:
            party_datas.append(
                {
                    "id": data.id,
                    "name": data.name,
                    "type": data.type,
                    "phone" : data.phone,
                    "email" : data.email,
                    "address" : data.address,
                    "gst_number" : data.gst_number
                }
            )
        return party_datas

    def get_party_data_by_type(self, type: str):
        return self.party_repository.get_by_filters({"type": type})

    def update_party(self, party_id, data):
        return self.party_repository.update_by_id(party_id, data)

    def delete_by_id(self, id):
        data = self.party_repository.get_by_id(id)
        if not data:
            raise HTTPException(status_code=400, detail=f"Party data not found for this {id}")
        return self.party_repository.delete_by_id(id)

        # update_data = {
        #     "name": data.name,
        #     "type": data.type,
        #     "phone": data.phone,
        #     "email": data.email,
        #     "address": data.address,
        #     "gst_number": data.gst_number
        # }