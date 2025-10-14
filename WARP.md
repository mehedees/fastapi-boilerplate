# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a FastAPI boilerplate implementing Clean Architecture/Hexagonal Architecture patterns with Domain-Driven Design (DDD). The project uses dependency injection, JWT authentication with refresh tokens, and follows strict separation of concerns across architectural layers.

## Development Commands

### Environment Setup
```bash
# Copy environment template and configure
cp .env.example .env
# Edit .env with your database credentials and secret keys
```

### Running the Application

#### Using Docker (Recommended for development)
```bash
# Start all services (app + MySQL)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

#### Using uv (Local development)
```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

### Testing
```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/api/test_users_flow.py

# Run unit tests only
uv run pytest tests/unit/

# Run integration tests only
uv run pytest tests/integration/
```

### Code Quality
```bash
# Lint and format code
uv run ruff check --fix
uv run ruff format

# Run pre-commit hooks
uv run pre-commit run --all-files
```

### Database & Admin Tasks
```bash
# Create first admin user (interactive script)
uv run python app/scripts/create_admin_user.py
```

### Building
```bash
# Build Docker image
docker build . --tag fastapi-boilerplate:0.0.1

# Run built image
docker run -p 9000:9000 --name fastapi-boilerplate fastapi-boilerplate:0.0.1
```

## Architecture Overview

### Layered Architecture Structure

```
app/
├── main.py                 # Application entry point
├── core/                   # Infrastructure layer
│   ├── app.py             # FastAPI app factory
│   ├── container.py       # Dependency injection setup
│   ├── settings.py        # Configuration management
│   ├── middlewares/       # Auth & logging middleware
│   └── utils/             # Shared utilities (auth, tokens)
├── api/                   # Presentation layer
│   └── v1/               # API version 1
│       └── users/        # User endpoints (routes, views, schemas)
├── domain/               # Domain layer (business logic)
│   └── users/
│       ├── entities/     # Domain entities/DTOs
│       ├── services.py   # Business logic services
│       ├── repo/         # Repository protocols/interfaces
│       └── exceptions.py # Domain-specific exceptions
├── infra/               # Infrastructure layer
│   └── persistence/     # Data access layer
│       ├── db.py        # Database connection management
│       ├── models/      # SQLAlchemy ORM models
│       └── repo_impl/   # Repository implementations
└── scripts/             # Administrative scripts
```

### Key Architectural Patterns

**Dependency Injection**: Uses `dependency-injector` for IoC container management. All dependencies are wired in `core/container.py` and injected throughout the application.

**Repository Pattern**: Domain defines repository protocols (`domain/users/repo/`) while infrastructure provides implementations (`infra/persistence/repo_impl/`).

**Clean Architecture**:
- Domain layer contains pure business logic with no external dependencies
- Infrastructure layer handles external concerns (database, HTTP)
- API layer orchestrates requests between external world and domain

**Authentication Architecture**:
- JWT access tokens with short expiry (configurable)
- Secure refresh tokens stored in database with device tracking
- Comprehensive security measures including replay attack detection
- Argon2 password hashing

### Domain Services Pattern

Business logic is encapsulated in domain services (e.g., `UserService`). Services:
- Handle complex business operations
- Coordinate between repositories
- Implement authentication flows
- Manage token lifecycle with security considerations

### Configuration Management

Settings are managed through `pydantic-settings` with environment variable support:
- Database connection pooling configuration
- JWT token settings (keys, expiry, algorithms)
- CORS configuration
- Logging levels and application metadata

## Testing Strategy

### Test Structure
- **Unit tests** (`tests/unit/`): Test individual components in isolation
- **Integration tests** (`tests/integration/`): Test component interactions
- **API tests** (`tests/api/`): End-to-end API flow testing

### Testing Patterns
- Uses in-memory repositories for fast unit testing
- Dependency injection overrides for mocking external dependencies
- AsyncClient with ASGITransport for API testing
- Comprehensive authentication flow testing including token refresh

### Key Test Files
- `test_users_flow.py`: Full authentication flow testing (login, refresh, logout)
- `test_user_service.py`: Business logic unit tests
- `test_auth_*.py`: Authentication and token handling tests

## Development Notes

### Adding New Features
1. Define domain entities in `domain/{feature}/entities/`
2. Create repository protocol in `domain/{feature}/repo/`
3. Implement business logic in `domain/{feature}/services.py`
4. Create repository implementation in `infra/persistence/repo_impl/`
5. Add API endpoints in `api/v1/{feature}/`
6. Wire dependencies in `core/container.py`

### Security Considerations
- All passwords are hashed with Argon2
- Refresh tokens include device fingerprinting
- Comprehensive token validation with replay attack detection
- Configurable token expiry and secret rotation
- Authentication middleware with path exclusions

### Database Integration
- Uses SQLAlchemy 2.0+ with async support
- Connection pooling with configurable parameters
- MySQL-specific optimizations (charset, autocommit settings)
- Session management with automatic rollback on exceptions
