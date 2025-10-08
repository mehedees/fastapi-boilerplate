import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import logger, request_id_context


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log incoming requests and their responses.
    Logs method, URL, status code, response time, and client IP address.
    Also assigns a unique request ID to each request for better traceability.
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Set request_id for this request
        request_id = str(uuid.uuid4())
        request_id_context.set(request_id)

        # Update logger adapter with new request_id
        logger.extra["request_id"] = request_id

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        extra = {
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "response_time_ms": round(duration * 1000, 2),
            "client_ip": request.client.host if request.client else "unknown",
        }

        logger.info("HTTP Request", extra=extra)
        return response
