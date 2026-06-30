from fastapi.openapi.utils import get_openapi

from backend.api.app import create_app

app = create_app()
try:
    schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    print("Paths in openapi schema:", schema.get("paths", {}).keys())
except Exception as e:
    print(f"Error: {e}")
