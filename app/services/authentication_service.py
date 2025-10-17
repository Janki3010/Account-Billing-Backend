from datetime import datetime
from fastapi import HTTPException, BackgroundTasks

from app.config.settings import settings

from app.repositories.authentication_repository import AuthenticationRepository

from app.schemas.authentication import UserCreate, ForgotPasswordRequest, ResetPassword, Login

from app.services.email_service import EmailService

from app.repositories.email_token_repository import EmailTokenRepository

from app.utils.security import hash_password, verify_password
from app.utils.token import generate_verification_token, create_access_token

class AuthenticationService:
    def __init__(self):
        self.auth_repository = AuthenticationRepository()
        self.email_service = EmailService()
        self.email_token_repository = EmailTokenRepository()

    def register(self, user: UserCreate, background_tasks: BackgroundTasks):
        new_user = None
        normalized_email = user.email.lower()
        if user.password != user.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        existing_user = self.auth_repository.get_user_by_email(normalized_email)
        if existing_user and existing_user.is_verified is True:
            raise HTTPException(status_code=400, detail="Registration failed. Please check your details.")

        hashed_pwd = hash_password(user.password)

        if existing_user:
            if not existing_user.is_verified:
                update_user = self.auth_repository.update_data(existing_user.id, normalized_email, hashed_pwd)
                if update_user:
                    new_user = self.auth_repository.get_user_by_email(normalized_email)
                else:
                    raise HTTPException(status_code=500, detail="Failed to update unverified user")
        else:
            new_user = self.auth_repository.create_user(normalized_email, hashed_pwd)

        if not new_user:
            raise HTTPException(status_code=500, detail="User creation failed")

        self.email_token_repository.delete_existing_email_verification_tokens(new_user.id)

        verification_token = generate_verification_token(normalized_email)
        self.email_token_repository.save_token(new_user.id, verification_token, "email_verification")

        verification_link = f"{settings.DOMAIN_URL}/auth/verify-email/{verification_token}"
        subject = "Verify Your Email"

        body = f"""
            <html>
                <body>
                    <p>Click the link below to verify your email:</p>
                    <p><a href="{verification_link}" target="_blank">{verification_link}</a></p>
                </body>
            </html>
        """

        self.email_service.send_email_background(background_tasks, normalized_email, subject, body)

    def login(self, user: Login):
        normalized_email = user.email.lower()
        db_user = self.auth_repository.get_user_by_email(normalized_email)
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid credentials")
        if not db_user.is_verified:
            raise HTTPException(status_code=403, detail="Please verify your email first")
        user_id = str(db_user.id)
        email = str(db_user.email)
        access_token = create_access_token(user_id, email)

        return access_token

    def admin_login(self, admin: Login):
        normalized_email = admin.email.lower()
        db_admin = self.auth_repository.get_admin_by_email(normalized_email)
        if not db_admin or not verify_password(admin.password, db_admin.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        admin_id = str(db_admin.id)
        email = str(db_admin.email)
        access_token = create_access_token(admin_id, email)
        return access_token

    def verify_email(self, token: str):
        db_token = self.email_token_repository.get_token(token, "email_verification")

        if not db_token:
            raise ValueError("Invalid or expired token")

        if db_token.expires_at < datetime.utcnow():
            self.email_token_repository.delete_by_id(db_token.id)
            raise ValueError("Token has expired")

        if not db_token.user:
            raise ValueError("User not found")

        self.email_token_repository.delete_by_id(db_token.id)
        self.auth_repository.verify_user(db_token.user_id)


    def forgot_password(self, request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
        normalized_email = request.email.lower()
        user = self.auth_repository.get_user_by_email(normalized_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        self.email_token_repository.delete_existing_password_reset_tokens(user.id)

        reset_token = generate_verification_token(user.email)
        self.email_token_repository.save_token(user.id, reset_token, "password_reset")

        reset_link = f"{settings.FRONTEND_URL}/reset-password/{reset_token}"
        subject = "Reset Your Password"

        body = f"""
            <html>
                <body>
                    <p>Click the link below to reset your password:</p>
                    <p><a href="{reset_link}" target="_blank">{reset_link}</a></p>
                </body>
            </html>
        """

        self.email_service.send_email_background(background_tasks, user.email, subject, body)

    def reset_password(self, token: str, request: ResetPassword):
        if request.new_password != request.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        db_token = self.email_token_repository.get_token(token, "password_reset")
        if not db_token:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        if db_token.expires_at < datetime.utcnow():
            self.email_token_repository.delete_by_id(db_token.id)
            raise HTTPException(status_code=400, detail="Token has expired")

        if not db_token.user:
            raise HTTPException(status_code=404, detail="User not found")

        hashed_password = hash_password(request.new_password)
        self.auth_repository.update_user_password(db_token.user_id, hashed_password)
        self.email_token_repository.delete_by_id(db_token.id)




