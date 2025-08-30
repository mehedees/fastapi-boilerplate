# Build stage
FROM ghcr.io/astral-sh/uv:0.8.13-python3.13-trixie-slim as builder

# Set build-time environment variables
ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images.
ENV UV_PYTHON_DOWNLOADS=0

# Set work directory
WORKDIR /app

# Install dependencies system-wide
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy application code
COPY --link ./app ./app
COPY pyproject.toml uv.lock ./

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Production stage
FROM python:3.13-slim-trixie as production

# Add metadata labels
LABEL maintainer="Your Name <your.email@example.com>" \
      version="1.0" \
      description="FastAPI application"

# Set production environment variables
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Copy installed packages from builder stage
COPY --link --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --link --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser ./app ./app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER appuser

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

# Expose port
EXPOSE 9000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT:-9000}", "--workers", "${WORKERS:-4}", "--log-level", "${LOG_LEVEL:-info}"]
