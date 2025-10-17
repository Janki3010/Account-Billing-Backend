from fastapi import APIRouter
from fastapi_restful.cbv import cbv

from app.services.company_service import CompanyService

company_router = APIRouter(prefix="/company", tags=["company"])

@cbv(company_router)
class CompanyController:
    def __init__(self):
        self.company_service = CompanyService()

    @company_router.post("/create")
    def create_company(self, name: str):
        return self.company_service.add_company(name)

    @company_router.get("/get-all")
    def get_companies(self):
        return self.company_service.get_all()

    @company_router.patch("/update")
    def update_company_name(self, name: str, com_id: str):
        return self.company_service.update_name(name, com_id)

    @company_router.delete("/delete")
    def delete_company_name(self, id: str):
        return self.company_service.delete_by_id(id)
