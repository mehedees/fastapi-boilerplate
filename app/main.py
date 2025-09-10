from contextlib import asynccontextmanager

from fastapi import FastAPI, status

from app.core.container import Container, setup_container
from app.core.logging import logger
from app.core.schemas.base import APIResponse
from app.core.settings import Settings, get_settings

settings = get_settings()


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    logger.info("Starting app")
    app.container.init_resources()  # type: ignore
    yield
    app.container.shutdown_resources()  # type: ignore
    logger.info("Shutting down app")


def create_fastapi_app() -> FastAPI:
    settings: Settings = get_settings()
    container: Container = setup_container(settings)

    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=app_lifespan,
    )
    app.container = container  # type: ignore
    return app


app = create_fastapi_app()


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=APIResponse,
)
async def healthcheck():
    return APIResponse()
