from app.repositories.shop_profile_repository import ShopProfileRepository


class ShopProfileService:
    def __init__(self):
        self.shop_profile_repository = ShopProfileRepository()

    def create_shop_profile(self, data):
        return self.shop_profile_repository.add_shop_profile_data(data)

    def get_all_details(self):
        shop_profiles = []
        shop_data = self.shop_profile_repository.get_all()
        for data in shop_data:
            shop_profiles.append({
                "id": str(data.id),
                "shop_name": data.shop_name,
                "gstin": data.gstin,
                "address": data.address,
                "phone": data.phone,
                "email" : data.email,
                "bank_name" : data.bank_name,
                "account_number" : data.account_number,
                "ifsc_code" : data.ifsc_code,
                "qr_code_url" : data.qr_code_url,
                "authorized_signatory" : data.authorized_signatory
            })
        return shop_profiles

    def get_details_by_id(self, shop_id: str):
        shop_profile = {}
        data =  self.shop_profile_repository.get_by_id(shop_id)
        if data:
            shop_profile = {
                    "id": str(data.id),
                    "shop_name": data.shop_name,
                    "gstin": data.gstin,
                    "address": data.address,
                    "phone": data.phone,
                    "email" : data.email,
                    "bank_name" : data.bank_name,
                    "account_number" : data.account_number,
                    "ifsc_code" : data.ifsc_code,
                    "qr_code_url" : data.qr_code_url,
                    "authorized_signatory" : data.authorized_signatory
                }
        return shop_profile

    def update_shop_profile(self, data):
        update_data = {
            "shop_name": data.shop_name,
            "gstin": data.gstin,
            "address": data.address,
            "phone": data.phone,
            "email": data.email,
            "bank_name": data.bank_name,
            "account_number": data.account_number,
            "ifsc_code": data.ifsc_code,
            "qr_code_url": data.qr_code_url,
            "authorized_signatory": data.authorized_signatory
        }
        return self.shop_profile_repository.update_by_id(data.id, update_data)