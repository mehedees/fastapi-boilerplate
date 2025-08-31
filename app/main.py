from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from app.core.db import initialize_db, shutdown_db
from app.core.logging import logger
from app.core.schemas.base import APIResponse
from app.core.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    logger.info("Starting app")
    settings = get_settings()
    initialize_db(settings)
    yield
    logger.info("Shutting down app")
    shutdown_db()


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=app_lifespan,
)


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=APIResponse,
)
async def healthcheck():
    return APIResponse()
