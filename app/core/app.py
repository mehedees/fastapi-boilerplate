from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from app.api.v1.users.routes import user_router
from app.core.container import Container, setup_container
from app.core.logging import logger
from app.core.middlewares.auth import AuthMiddleware, JWTAuthBackend
from app.core.middlewares.logging import LoggingMiddleware
from app.core.schemas.base import APIResponse
from app.core.settings import Settings, get_settings


class FastAPIApp(FastAPI):
    container: Container


@asynccontextmanager
async def app_lifespan(app: FastAPIApp):
    logger.info("Starting app")
    app.container.init_resources()
    yield
    app.container.shutdown_resources()
    logger.info("Shutting down app")


def create_fastapi_app() -> FastAPIApp:
    settings: Settings = get_settings()
    container: Container = setup_container(settings)

    app = FastAPIApp(
        title=settings.APP_NAME,
        description=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=app_lifespan,
        exception_handlers={StarletteHTTPException: handle_api_exceptions},
        responses={
            401: {"description": "Not authenticated"},
            404: {"description": "Not found"},
        },
    )
    app.container = container
    register_middleware(app, settings)
    register_routers(app, settings)
    return app


async def handle_api_exceptions(request, exc):
    headers = getattr(exc, "headers", None)
    return JSONResponse(
        APIResponse(
            success=False,
            message=exc.detail,
        ).model_dump(),
        status_code=exc.status_code,
        headers=headers,
    )


def register_middleware(app: FastAPIApp, settings: Settings):
    app.add_middleware(
        AuthMiddleware,
        backend=JWTAuthBackend(
            secret_key=settings.SECRET_KEY,
            algorithm=settings.AUTH_TOKEN_ALGORITHM,
        ),
        exclude_paths=settings.AUTH_EXCLUDE_PATHS,
    )
    app.add_middleware(LoggingMiddleware)


def register_routers(app: FastAPIApp, settings: Settings):
    api_v1_router = APIRouter(prefix="/api/v1")
    api_v1_router.include_router(user_router)

    app.include_router(api_v1_router)

    app.add_api_route(
        settings.HEALTHCHECK_ENDPOINT, endpoint=healthcheck, methods=["GET"]
    )


async def healthcheck():
    return APIResponse()
