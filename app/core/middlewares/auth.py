from enum import Enum

import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
)
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.utils.token import TokenTypeEnum, TokenUtils


class AuthUser(BaseUser):
    """User class that holds JWT payload information"""

    def __init__(self, payload: dict):
        self.payload = payload
        self.user_id = payload.get("user_id")
        self.email = payload.get("email")
        self.token_type = payload.get("token_type")
        self.issued_at = payload.get("iat")
        self.expires_at = payload.get("exp")

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.email

    @property
    def identity(self) -> str:
        return str(self.user_id)


class AuthErrorType(str, Enum):
    """Enum for different authentication error types"""

    NOT_AUTHENTICATED = "not_authenticated"
    INVALID_AUTHENTICATION_CREDENTIALS = "invalid_authentication_credentials"
    TOKEN_EXPIRED = "token_expired"

    INVALID_SIGNATURE = "invalid_signature"
    MALFORMED_TOKEN = "malformed_token"
    INVALID_TOKEN = "invalid_token"
    AUTHENTICATION_FAILED = "authentication_failed"


class AuthError(AuthenticationError):
    """Custom authentication error"""

    def __init__(self, status_code: int, err_type: AuthErrorType, detail: str):
        self.status_code = status_code
        self.detail = detail
        self.err_type = err_type
        super().__init__(detail)


class JWTAuthBackend(AuthenticationBackend):
    """JWT Authentication Backend"""

    def __init__(self, secret_key: str, algorithm: str):
        self.__token_util = TokenUtils(secret_key=secret_key, algorithm=algorithm)
        self.__http_bearer = HTTPBearer()

    async def authenticate(
        self, request: Request
    ) -> tuple[AuthCredentials, BaseUser] | None:
        """Authenticate request using JWT token"""

        # Use FastAPI's HTTPBearer to extract token
        try:
            credentials: HTTPAuthorizationCredentials | None = await self.__http_bearer(
                request
            )
        except HTTPException as exc:
            if exc.detail.lower().replace(" ", "_") == AuthErrorType.NOT_AUTHENTICATED:
                raise AuthError(
                    status_code=exc.status_code,
                    err_type=AuthErrorType.NOT_AUTHENTICATED,
                    detail=exc.detail,
                ) from None
            elif (
                exc.detail.lower().replace(" ", "_")
                == AuthErrorType.INVALID_AUTHENTICATION_CREDENTIALS
            ):
                raise AuthError(
                    status_code=exc.status_code,
                    err_type=AuthErrorType.INVALID_AUTHENTICATION_CREDENTIALS,
                    detail=exc.detail,
                ) from None
            else:
                raise AuthError(
                    status_code=exc.status_code,
                    err_type=AuthErrorType.AUTHENTICATION_FAILED,
                    detail=exc.detail,
                ) from None

        token = credentials.credentials

        try:
            # Decode JWT token
            payload = self.__token_util.decode_token(token)

        except jwt.ExpiredSignatureError:
            raise AuthError(
                status_code=401,
                err_type=AuthErrorType.TOKEN_EXPIRED,
                detail="Token has expired",
            ) from None
        except jwt.InvalidSignatureError:
            raise AuthError(
                status_code=401,
                err_type=AuthErrorType.INVALID_SIGNATURE,
                detail="Invalid token signature",
            ) from None
        except jwt.DecodeError:
            raise AuthError(
                status_code=401,
                err_type=AuthErrorType.MALFORMED_TOKEN,
                detail="Malformed token",
            ) from None
        except jwt.InvalidTokenError:
            raise AuthError(
                status_code=401,
                err_type=AuthErrorType.INVALID_TOKEN,
                detail="Invalid token",
            ) from None
        except Exception as e:  # Catch any unexpected errors
            raise AuthError(
                status_code=401,
                err_type=AuthErrorType.AUTHENTICATION_FAILED,
                detail=f"Authentication failed: {str(e)}",
            ) from None

        # Validate required claims
        if ("user_id" not in payload) or ("email" not in payload):
            raise AuthError(
                status_code=401,
                err_type=AuthErrorType.INVALID_TOKEN,
                detail="Required claims missing",
            )

        if payload.get("token_type") != TokenTypeEnum.ACCESS:
            raise AuthError(
                status_code=401,
                err_type=AuthErrorType.INVALID_TOKEN,
                detail="Invalid token type",
            )

        # Create user with payload
        user = AuthUser(payload)
        return AuthCredentials(["authenticated"]), user


class AuthMiddleware(AuthenticationMiddleware):
    """Custom JWT Authentication Middleware with path exclusions"""

    def __init__(
        self,
        app,
        backend: JWTAuthBackend,
        prefixes: list[str],
        exclude_paths: list[str],
    ):
        super().__init__(app, backend=backend)
        self.__exclude_paths = exclude_paths or []
        self.__prefixes = prefixes or []

    async def __call__(self, scope, receive, send):
        """Process request (non-lifespan scope types) with path exclusion"""

        if scope["type"] != "lifespan":
            path = scope.get("path", "")
            for prefix in self.__prefixes:
                if path.startswith(prefix):
                    path = path.removeprefix(prefix)
                    break

            if path in self.__exclude_paths:
                await self.app(scope, receive, send)
                return

        # Apply authentication for non-excluded paths
        await super().__call__(scope, receive, send)

    @staticmethod
    def default_on_error(request: Request, exc: AuthError) -> JSONResponse:
        """Default error handler for authentication failures"""

        error_message = str(exc)

        return JSONResponse(
            {"error": exc.err_type.value, "message": error_message},
            status_code=401,
            headers={
                "WWW-Authenticate": f'Bearer realm="api" error="{exc.err_type.value}" error_description="{exc.detail}"'
            },
        )


__all__ = ["AuthMiddleware", "JWTAuthBackend", "AuthUser"]
