from pydantic import BaseModel, EmailStr, Field, validator

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    confirm_password: str = Field(..., min_length=8, description="Confirm password")

class Login(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="User password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    new_password: str = Field(..., min_length=8, description="User password")
    confirm_password: str = Field(..., min_length=8, description="Confirm password")


