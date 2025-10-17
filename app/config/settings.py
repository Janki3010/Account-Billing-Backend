import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    DOMAIN_URL: str = os.getenv("DOMAIN_URL", "http://localhost")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL")
    PORT: int = int(os.getenv("PORT"))

    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT"))
    POSTGRES_USERNAME: str = os.getenv("POSTGRES_USERNAME")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DATABASE_NAME: str = os.getenv("POSTGRES_DATABASE_NAME")
    PG_CONN_STR: str = os.getenv("PG_CONN_STR")

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME")
    EMAIL_HOST: str = os.getenv("EMAIL_HOST")
    EMAIL_PORT: int = os.getenv("EMAIL_PORT")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM")
    MAIL_STARTTLS: bool = os.getenv("EMAIL_STARTTLS")
    MAIL_SSL_TLS: bool = os.getenv("EMAIL_SSL_TLS")
    USE_CREDENTIALS: bool = os.getenv("USE_CREDENTIALS")
    VALIDATE_CERTS: bool = os.getenv("VALIDATE_CERTS")

settings = Settings()