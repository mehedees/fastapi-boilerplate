from core.settings import get_settings
import logging
from contextvars import ContextVar
from typing import Any
from pythonjsonlogger import jsonlogger


settings = get_settings()

# Context variable for request ID
request_id_context: ContextVar[str] = ContextVar("request_id", default="no-request")

# Custom logging adapter to inject request_id
class RequestIdAdapter(logging.LoggerAdapter):
    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        # Inject request_id into extra
        extra = kwargs.get("extra", {})
        extra["request_id"] = self.extra["request_id"]
        kwargs["extra"] = extra
        return msg, kwargs

# Custom filter to exclude sensitive data
class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, 'extra'):
            sensitive_fields = ['password', 'token', 'api_key']
            for field in sensitive_fields:
                if field in record.extra:
                    record.extra[field] = '****'
        return True

# Configure logger
def configure_logger():
    logger = logging.getLogger("fastapi_app")
    logger.handlers = []
    log_level = settings.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(extra)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(console_handler)
    
    # Wrap logger with adapter
    return RequestIdAdapter(logger, {"request_id": request_id_context.get()})

# Initialize logger with adapter
logger = configure_logger()
