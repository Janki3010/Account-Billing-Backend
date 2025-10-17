from fastapi import APIRouter
from fastapi_restful.cbv import cbv
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.schemas.shop_profile import ShopProfileReq, ShopProfile
from app.services.shop_profile_service import ShopProfileService

shop_pro_router = APIRouter(prefix="/shop-profile", tags=["shop-profile"])

@cbv(shop_pro_router)
class ShopProfileController:
    def __init__(self):
        self.shop_profile_service = ShopProfileService()

    @shop_pro_router.post(
        "/create",
        status_code=HTTP_201_CREATED,
        summary="Create Shop Profile"
    )
    def add_shop_profile(self, data: ShopProfileReq):
        return self.shop_profile_service.create_shop_profile(data)

    @shop_pro_router.get(
        "/get-all",
        summary="Get all details of shop profiles",
        status_code=HTTP_200_OK
    )
    def get_shop_profile_details(self):
        return self.shop_profile_service.get_all_details()

    @shop_pro_router.get(
        "/get-by-id",
        summary="Get shop details by id",
        status_code=HTTP_200_OK
    )
    def get_shop_profile_by_id(self, shop_id: str):
        return self.shop_profile_service.get_details_by_id(shop_id)

    @shop_pro_router.patch(
        "/update",
        summary="Update shop profile",
        status_code=HTTP_200_OK
    )
    def update_shop_details(self, update_request: ShopProfile):
        return self.shop_profile_service.update_shop_profile(update_request)