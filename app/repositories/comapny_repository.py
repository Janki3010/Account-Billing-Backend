from fastapi import HTTPException

from app.models.company import Company
from app.repositories.base_repository import BaseRepository


class CompanyRepository(BaseRepository):
    def __init__(self):
        super().__init__(Company)

    def get_company_id(self, company_name):
        company = self.get_by_filters({"name": company_name})
        if not company:
            raise HTTPException(status_code=400, detail="Company name not found")

        return company.id

    def get_company_name(self, company_id):
        company = self.get_by_id(company_id)
        if not company:
            raise HTTPException(status_code=400, detail="Company not found")

        return company.name

    def create_company(self, name):
        return self.save(Company(name=name))

    def get_all_company(self):
        return self.get_all()