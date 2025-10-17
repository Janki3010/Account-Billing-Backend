from fastapi.openapi.utils import get_openapi

class CustomOpenAPI:
    def __init__(self, app, title="Account-Billing", version="1.0.0", description="API with JWT Authentication"):
        self.app = app
        self.title = title
        self.version = version
        self.description = description

    def generate_openapi(self):
        if self.app.openapi_schema:
            return self.app.openapi_schema
        openapi_schema = get_openapi(
            title=self.title,
            version=self.version,
            description=self.description,
            routes=self.app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
        openapi_schema["security"] = [{"BearerAuth": []}]
        self.app.openapi_schema = openapi_schema
        return openapi_schema
