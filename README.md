# FastAPI Boilerplate

A clean, opinionated starter template for building production-ready APIs with FastAPI, SQLAlchemy, and MySQL. It includes Docker/Docker Compose, environment-based configuration, health checks, testing setup, linting/formatting with Ruff, and a modular project structure to help you start fast and scale safely.

Current local date/time: 2025-10-08 15:50

## Features
- FastAPI app factory pattern (modular, testable)
- MySQL database via Docker Compose
- SQLAlchemy ORM and repository pattern
- JWT-based auth utilities
- Typed schemas with Pydantic
- Centralized settings via pydantic-settings and .env
- Health check endpoint and automatic container healthchecks
- Uvicorn server with reload (dev) and configurable workers (prod)
- Tests with pytest and pytest-asyncio; coverage enabled by default
- Code quality: Ruff (lint + format)

## Quick Start

Pick one of the options below.

### 1) Run everything with Docker Compose (recommended)
Prerequisites: Docker Desktop or Docker Engine + Compose plugin

1. Copy the example env file and adjust values as needed:
   cp .env.example .env
2. Start the stack (API + MySQL):
   docker compose up --build
3. Open the API docs:
   - Swagger UI: http://localhost:9000/docs
   - ReDoc: http://localhost:9000/redoc
   - Health: http://localhost:9000/health

Notes
- The service port is mapped from ${PORT:-9000} to 9000 inside the container. By default, you'll use 9000 on your host.
- MySQL credentials and database name are controlled by .env values (see .env.example for all keys).

### 2) Run the API container only (requires an external MySQL)
If you already have a reachable MySQL database (local or remote), you can run just the API container:

1. Ensure .env is configured to point to your MySQL host (DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD).
2. Build and run:
   docker build -t fastapi-boilerplate:0.1.0 .
   docker run --env-file .env -p 9000:9000 --name fastapi-boilerplate fastapi-boilerplate:0.1.0
3. Visit http://localhost:9000/docs

### 3) Run locally with Python (uv) + optional MySQL via Docker
Prerequisites: Python 3.13 and uv (recommended) or pip

- Install uv (one-time): https://docs.astral.sh/uv/getting-started/installation/

Steps
1. Copy env and adjust:
   cp .env.example .env
2. (Optional) Start only MySQL via Compose (runs DB in Docker while you run API locally):
   docker compose up -d mysql
3. Install dependencies with uv:
   uv sync
4. Run the API with reload on port 9000:
   uv run uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
5. Open http://localhost:9000/docs

If you prefer pip instead of uv
- Create a virtualenv and install: pip install -e .
- Run: uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

## Configuration
All runtime configuration is handled via environment variables. See .env.example for all options.

Important keys
- APP_NAME, APP_VERSION, ENVIRONMENT, DEBUG, LOG_LEVEL
- HOST, PORT (host map for Compose defaults to 9000; .env example shows 8000 — you can align them as you wish)
- DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD
- SECRET_KEY, ACCESS_TOKEN_SECRET_KEY, REFRESH_TOKEN_SECRET_KEY, AUTH_TOKEN_ALGORITHM
- ACCESS_TOKEN_EXPIRE_SECONDS, REFRESH_TOKEN_EXPIRE_SECONDS
- CORS settings: ALLOWED_ORIGINS, ALLOWED_METHODS, ALLOWED_HEADERS

Security notes
- For production, generate strong secrets:
  python -c "import secrets; print(secrets.token_urlsafe(32))"
- Never commit real secrets; use secret managers or deployment-level env vars.

## API Endpoints
- /docs — Swagger UI
- /redoc — ReDoc
- /health — Simple liveness check used by Docker healthcheck

## Project Structure (high level)
- app/
  - api/ (versioned API routers)
  - core/ (app factory, settings, middlewares, schemas, utils)
  - domain/ (business logic, services, entities, repos)
  - infra/ (persistence models, repo implementations, external integrations)
  - scripts/ (helper scripts)
- tests/ (unit, api, integration)
- docker-compose.yaml, Dockerfile
- pyproject.toml (dependencies, ruff, pytest settings)

## Development
- Lint: uv run ruff check .
- Format: uv run ruff format .
- Tests: uv run pytest
- Test coverage is enabled via pyproject (term-missing report).

## License
This project is licensed under the MIT License.

Copyright (c) 2025 Mehedee Siddique

See the LICENSE file for the full text.
