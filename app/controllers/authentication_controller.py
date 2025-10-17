from fastapi import Depends, APIRouter
from fastapi_restful.cbv import cbv
from fastapi import BackgroundTasks
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from app.config.settings import settings

from app.schemas.authentication import (
    UserCreate,
    Login,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPassword
)

from app.services.authentication_service import AuthenticationService

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@cbv(auth_router)
class AuthenticationController:
    def __init__(self, auth_service: AuthenticationService = Depends()):
        self.auth_service = auth_service

    @auth_router.post("/register", status_code=HTTP_201_CREATED, summary="Register a new user")
    def register(
            self,
            background_tasks: BackgroundTasks,
            user: UserCreate,
    ):
        self.auth_service.register(user, background_tasks)
        return {"message": "User created! Please check your email to verify your account."}

    @auth_router.post("/login", response_model=TokenResponse, status_code=HTTP_200_OK, summary="Login user")
    def login(
        self,
        user: Login,
    ):
        access_token = self.auth_service.login(user)
        return {"access_token": access_token, "token_type": "bearer"}

    @auth_router.get("/verify-email/{token}", summary="Verify email with token", include_in_schema=False)
    def verify_email(self, token: str):
        self.auth_service.verify_email(token)
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login", status_code=303)

    @auth_router.post("/forgot-password", summary="Request password reset")
    def forgot_password(
        self,
        background_tasks: BackgroundTasks,
        request: ForgotPasswordRequest
    ):
        self.auth_service.forgot_password(request, background_tasks)
        return {"message": "Password reset email sent."}

    @auth_router.post("/reset-password/{token}", summary="Reset password")
    def reset_password(
        self,
        token: str,
        request: ResetPassword
    ):
         self.auth_service.reset_password(token, request)
         return {"message": "Password reset successfully"}
