import os
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.controllers.authentication_controller import auth_router
from app.controllers.company_controller import company_router
from app.controllers.invoice_controller import invoice_router
from app.controllers.item_controller import item_router
from app.controllers.party_controller import party_router
from app.controllers.payment_controller import payment_router
from app.controllers.report_controller import report_router
from app.controllers.shop_profile_controller import shop_pro_router
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.custom_openapi import CustomOpenAPI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

limiter = Limiter(key_func=get_remote_address, default_limits=["10/seconds"])

app = FastAPI(title="Account-Billing")

app.state.limiter = limiter

app.add_middleware(AuthMiddleware)

# Add SlowAPI middleware
app.add_middleware(SlowAPIMiddleware)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(party_router)
app.include_router(item_router)
app.include_router(company_router)
app.include_router(invoice_router)
app.include_router(payment_router)
app.include_router(shop_pro_router)
app.include_router(report_router)
# Initialize and set custom OpenAPI
custom_openapi = CustomOpenAPI(app)
app.openapi = custom_openapi.generate_openapi


@app.exception_handler(RateLimitExceeded)
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )
