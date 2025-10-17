from app.models.shopProfile import ShopProfile
from app.repositories.base_repository import BaseRepository


class ShopProfileRepository(BaseRepository):
    def __init__(self):
        super().__init__(ShopProfile)

    def add_shop_profile_data(self, data):
        db_data = ShopProfile(
            shop_name=data.shop_name,
            gstin=data.gstin,
            address=data.address,
            phone=data.phone,
            email=data.email,
            bank_name=data.bank_name,
            account_number=data.account_number,
            ifsc_code=data.ifsc_code,
            qr_code_url=data.qr_code_url,
            authorized_signatory=data.authorized_signatory
        )
        return self.save(db_data)

