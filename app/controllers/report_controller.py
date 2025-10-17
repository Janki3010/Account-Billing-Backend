from datetime import date
from fastapi import APIRouter, Query
from fastapi_restful.cbv import cbv
from app.services.report_service import ReportService

report_router = APIRouter(prefix="/report", tags=["report"])

@cbv(report_router)
class ReportController:
    def __init__(self):
        self.report_service = ReportService()

    @report_router.get("/dashboard")
    def get_dashboard_data(
        self,
        year: int = Query(default=date.today().year),
        month: int = Query(default=date.today().month),
        start_date: date = Query(default=date.today().replace(day=1)),
        end_date: date = Query(default=date.today()),
    ):
        return self.report_service.get_dashboard_data(year, month, start_date, end_date)

