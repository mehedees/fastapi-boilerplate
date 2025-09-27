from fastapi import status

from app.core.app import create_fastapi_app
from app.core.schemas.base import APIResponse

app = create_fastapi_app()


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=APIResponse,
)
async def healthcheck():
    return APIResponse()
