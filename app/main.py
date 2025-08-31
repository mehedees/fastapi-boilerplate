from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from sqlalchemy import Engine

from app.core.db import get_engine, init_db
from app.core.logging import logger
from app.core.schemas.base import APIResponse
from app.core.settings import get_settings
from app.domain.users.models import User

settings = get_settings()


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    logger.info("Starting app")
    db_engine: Engine = get_engine()
    init_db()
    yield
    logger.info("Shutting down app")
    db_engine.dispose()


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
