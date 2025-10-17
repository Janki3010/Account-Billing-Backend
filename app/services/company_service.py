from fastapi import HTTPException

from app.repositories.comapny_repository import CompanyRepository


class CompanyService:
    def __init__(self):
        self.company_repository = CompanyRepository()

    def add_company(self, name):
        return self.company_repository.create_company(name)

    def get_all(self):
        return self.company_repository.get_all_company()

    def update_name(self, name, com_id):
        return self.company_repository.update_by_id(com_id, {"name": name})

    def delete_by_id(self, id):
        data = self.company_repository.get_by_id(id)
        if not data:
            raise HTTPException(status_code=400, detail=f"Company data not found for this {id}")
        return self.company_repository.delete_by_id(id)