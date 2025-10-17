from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config.settings import settings

from app.utils.token import decode_token


class AuthMiddleware(BaseHTTPMiddleware):
   async def dispatch(self, request: Request, call_next):
        domain_url = settings.DOMAIN_URL
        OPEN_ROUTES = ["/docs", "/redoc", "/openapi.json", "/login", domain_url, "/", "/favicon.ico"]

        # Bypass authentication for all routes under /auth and OPEN_ROUTES list
        if request.url.path.startswith("/auth") or request.url.path in OPEN_ROUTES:
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid token"})

        token = auth_header.split("Bearer ")[1]

        # Decode and verify token
        try:
            user_data = decode_token(token)
            if not user_data:
                raise ValueError("Invalid token or expired")
            request.state.user = user_data  # Store user data
        except:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        # Proceed to next middleware or request handler
        response = await call_next(request)
        return response
