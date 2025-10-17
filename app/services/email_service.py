from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config.settings import settings
import ssl

class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.EMAIL_USERNAME,
            MAIL_PASSWORD=settings.EMAIL_PASSWORD,
            MAIL_FROM=settings.EMAIL_FROM,
            MAIL_PORT=settings.EMAIL_PORT,
            MAIL_SERVER=settings.EMAIL_HOST,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=settings.USE_CREDENTIALS,
            VALIDATE_CERTS=settings.VALIDATE_CERTS
        )
        ssl._create_default_https_context = ssl._create_unverified_context
        self.mail_client = FastMail(self.conf)

    # Make send_email a regular synchronous method
    async def send_email(self, to_email: str, subject: str, body: str):
        message = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=body,
            subtype="html",
        )
        await self.mail_client.send_message(message)

    # Background task method
    def send_email_background(self, background_tasks: BackgroundTasks, to_email: str, subject: str, body: str):
        # Adding the send_email function to be run in the background
        background_tasks.add_task(self.send_email, to_email, subject, body)
