# This Dockerfile uses `uv` to build a FastAPI application in a multi-stage build.
# The first stage builds the application, and the second stage creates a minimal
# runtime image.

# First, build the application in the `/app` directory.

# Build stage
FROM ghcr.io/astral-sh/uv:0.8.13-python3.13-trixie-slim AS builder

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
COPY . /app

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


# Then, use a final image without uv
FROM python:3.13-slim-trixie AS production

# Add metadata labels
LABEL maintainer="Mehedee Siddique <mehedees@live.com>" \
      version="1.0" \
      description="FastAPI application"

# Set production environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory in the final image
WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Copy the application from the builder
COPY --from=builder --chown=appuser:appuser /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER appuser

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9000/health || exit 1

# Expose the application port
EXPOSE 9000

# Run the FastAPI application by default
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000", "--workers", "${WORKERS:-1}", "--log-level", "info", "--reload"]
