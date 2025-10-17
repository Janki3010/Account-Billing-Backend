import uuid

from app.models.authentication import User
from app.repositories.base_repository import BaseRepository


class AuthenticationRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_user_by_email(self, email: str):
        return self.get_by_filters({"email": email})
    #
    # def get_admin_by_email(self, email: str):
    #     return self.get_by_filters({"email": email}, model=Admin)

    def create_user(self, email: str, hashed_password: str):
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            is_verified=False
        )
        return self.save(new_user)

    def verify_user(self, user_id: uuid.UUID):
        return self.update_by_id(user_id, {"is_verified": True})

    def update_user_password(self, user_id: uuid.UUID, hashed_password: str):
        return self.update_by_id(user_id, {"hashed_password": hashed_password})

    def update_data(self, user_id: uuid.UUID, email: str, hashed_password: str):
        return self.update_by_id(user_id, {"email": email,"hashed_password": hashed_password})



