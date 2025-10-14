# Transaction Management Guide

This guide explains how to handle multiple interdependent operations within a single database transaction in your FastAPI boilerplate application.

## Problem Statement

In complex business scenarios, you often need to perform multiple database operations that are interdependent and must either all succeed or all fail together. For example:

- Creating a user and immediately generating access/refresh tokens
- Updating multiple related entities atomically
- Performing bulk operations that need to be atomic
- Complex business workflows with multiple database interactions

## Solution Overview

The application provides several approaches for handling complex transactions:

1. **Database-level transaction context** - Direct access to transaction management
2. **TransactionService** - High-level service for complex transaction scenarios
3. **Service-level transaction methods** - Business logic with transaction boundaries

## Usage Patterns

### 1. Direct Database Transaction Context

For simple scenarios where you need direct control over the transaction:

```python
from app.infra.persistence.db import Database

# In your service method
async def complex_operation(self, database: Database):
    with database.transaction() as session:
        # Perform multiple operations
        user = UserModel(...)
        session.add(user)
        session.flush()  # Get the ID

        token = RefreshTokenModel(user_id=user.id, ...)
        session.add(token)

        # All operations will be committed together
        # or rolled back if any exception occurs
```

### 2. Using TransactionService

For more complex scenarios with better abstraction:

```python
from app.domain.transactions.services import TransactionService

class MyService:
    def __init__(self, transaction_service: TransactionService):
        self.transaction_service = transaction_service

    async def complex_business_operation(self):
        with self.transaction_service.transaction() as session:
            # Perform multiple operations
            # All will be committed or rolled back together
            pass
```

### 3. Service-Level Transaction Methods

For business logic that needs transaction boundaries while maintaining separation of concerns:

```python
# Example from UserService - PROPER ARCHITECTURE
async def create_user_with_initial_tokens(
    self,
    user: UserCreateEntity,
    user_agent: str
) -> tuple[UserEntity, LoginTokenEntity]:
    """
    Creates a user and immediately generates tokens within a single transaction.
    Uses repository methods to maintain separation of concerns.
    """
    with self.__transaction_service.transaction() as session:
        # 1. Create user using repository
        user_entity = await self.__repo.create_user(user, session=session)

        # 2. Generate access token
        access_token, access_token_iat = await self.__make_access_token(
            user_id=user_entity.id,
            email=user_entity.email,
        )

        # 3. Create refresh token using repository
        refresh_token_entity = await self.__refresh_token_repo.create_refresh_token(
            RefreshTokenCreateEntity(
                user_id=user_entity.id,
                device_info=device_info_text,
                expires_at=datetime.now() + timedelta(seconds=3600),
            ),
            session=session
        )

        # 4. Generate refresh token JWT
        refresh_token, refresh_token_iat = self.__token_util.generate_refresh_token(
            refresh_token_payload,
            expiry_sec=self.__settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        )

        # All operations completed - transaction will commit
        return user_entity, login_token_entity
```

## Proper Architecture Pattern

### ✅ Correct Approach: Service → Repository → Database

```python
# Service layer orchestrates business logic
class UserService:
    async def create_user_with_tokens(self, user_data, user_agent):
        with self.__transaction_service.transaction() as session:
            # Use repository methods, not direct database operations
            user = await self.__repo.create_user(user_data, session=session)
            token = await self.__refresh_token_repo.create_refresh_token(
                token_data, session=session
            )
            return user, token
```

### ❌ Incorrect Approach: Service → Direct Database

```python
# DON'T DO THIS - violates separation of concerns
class UserService:
    async def create_user_with_tokens(self, user_data, user_agent):
        with self.__transaction_service.transaction() as session:
            # Direct database operations in service layer
            user_model = UserModel(**user_data)
            session.add(user_model)
            session.flush()
            # This breaks the architecture!
```

### Repository Pattern with Session Support

```python
# Repository methods support optional session parameter
class UserRepoImpl:
    async def create_user(self, user: UserCreateEntity, session: Optional[Session] = None):
        db_session = self._get_session(session)
        should_close = session is None

        try:
            # Database operations here
            return result
        finally:
            if should_close:
                db_session.close()
```

## Key Concepts

### Transaction Boundaries

- **Automatic Commit**: If no exceptions occur, the transaction is automatically committed
- **Automatic Rollback**: If any exception occurs, the entire transaction is rolled back
- **Session Management**: Sessions are automatically closed after the transaction

### Flush vs Commit

- **`session.flush()`**: Sends pending changes to the database but doesn't commit the transaction
- **`session.commit()`**: Commits the entire transaction (handled automatically by context managers)

Use `flush()` when you need the database to assign IDs or perform other operations before the transaction commits.

### Error Handling

```python
try:
    with self.transaction_service.transaction() as session:
        # Multiple operations
        pass
except SpecificException as e:
    # Handle specific business logic errors
    logger.error(f"Business logic error: {e}")
    raise
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
    raise
```

## Best Practices

### 1. Keep Transactions Short

```python
# Good: Short, focused transaction
with self.transaction_service.transaction() as session:
    user = UserModel(...)
    session.add(user)
    session.flush()

    token = RefreshTokenModel(user_id=user.id, ...)
    session.add(token)
```

```python
# Bad: Long-running transaction with external API calls
with self.transaction_service.transaction() as session:
    user = UserModel(...)
    session.add(user)
    session.flush()

    # Don't do this - external API calls should be outside transactions
    external_api_result = await call_external_api()

    token = RefreshTokenModel(user_id=user.id, ...)
    session.add(token)
```

### 2. Validate Data Before Transactions

```python
# Good: Validate before starting transaction
async def create_user_with_tokens(self, user_data: dict):
    # Validate user data first
    if not user_data.get('email'):
        raise ValueError("Email is required")

    # Check if user already exists
    existing_user = await self.__repo.get_user_by_email(user_data['email'])
    if existing_user:
        raise UserAlreadyExist("User already exists")

    # Now start transaction
    with self.transaction_service.transaction() as session:
        # Create user and tokens
        pass
```

### 3. Use Read-Only Transactions for Complex Queries

```python
# For complex read operations that need consistency
with self.transaction_service.read_only_transaction() as session:
    users = session.query(UserModel).all()
    tokens = session.query(RefreshTokenModel).all()
    # All reads see a consistent snapshot
```

### 4. Handle Partial Failures Gracefully

```python
async def bulk_operations(self, operations: list):
    try:
        with self.transaction_service.transaction() as session:
            results = []
            for operation in operations:
                try:
                    result = await self._execute_operation(session, operation)
                    results.append(result)
                except OperationSpecificError as e:
                    # Log but continue with other operations
                    logger.warning(f"Operation failed: {e}")
                    results.append(None)

            # If any critical operations failed, raise an exception
            if any(r is None for r in results):
                raise BulkOperationError("Some operations failed")

            return results
    except Exception as e:
        logger.error(f"Bulk operation failed: {e}")
        raise
```

## Common Patterns

### Pattern 1: Create with Dependencies

```python
async def create_user_with_profile(self, user_data: dict, profile_data: dict):
    with self.transaction_service.transaction() as session:
        # Create user first
        user = UserModel(**user_data)
        session.add(user)
        session.flush()  # Get user ID

        # Create profile with user ID
        profile = ProfileModel(user_id=user.id, **profile_data)
        session.add(profile)

        return user, profile
```

### Pattern 2: Update Multiple Entities

```python
async def update_user_and_tokens(self, user_id: int, user_data: dict, token_data: dict):
    with self.transaction_service.transaction() as session:
        # Update user
        user = session.query(UserModel).filter_by(id=user_id).one()
        for key, value in user_data.items():
            setattr(user, key, value)

        # Update tokens
        tokens = session.query(RefreshTokenModel).filter_by(user_id=user_id).all()
        for token in tokens:
            for key, value in token_data.items():
                setattr(token, key, value)

        return user, tokens
```

### Pattern 3: Conditional Operations

```python
async def conditional_user_operations(self, user_id: int, should_create_tokens: bool):
    with self.transaction_service.transaction() as session:
        user = session.query(UserModel).filter_by(id=user_id).one()

        if should_create_tokens:
            # Create tokens only if condition is met
            token = RefreshTokenModel(user_id=user.id, ...)
            session.add(token)

        return user
```

## Testing Transactions

```python
import pytest
from app.domain.transactions.services import TransactionService

@pytest.mark.asyncio
async def test_create_user_with_tokens(transaction_service: TransactionService):
    """Test that user creation and token generation are atomic."""
    user_data = {"email": "test@example.com", "password": "password123"}

    # This should succeed completely
    user, tokens = await user_service.create_user_with_initial_tokens(
        user_data, "test-agent"
    )

    assert user.email == "test@example.com"
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None

@pytest.mark.asyncio
async def test_transaction_rollback_on_failure(transaction_service: TransactionService):
    """Test that transaction rolls back on failure."""
    with pytest.raises(SomeException):
        with transaction_service.transaction() as session:
            # Create user
            user = UserModel(email="test@example.com")
            session.add(user)
            session.flush()

            # This will cause the transaction to rollback
            raise SomeException("Simulated failure")

    # Verify that user was not created
    with transaction_service.read_only_transaction() as session:
        user = session.query(UserModel).filter_by(email="test@example.com").first()
        assert user is None
```

## Integration with Dependency Injection

The `TransactionService` is automatically injected into services through the DI container:

```python
# In your service
class MyService:
    def __init__(self, transaction_service: TransactionService):
        self.transaction_service = transaction_service

    async def complex_operation(self):
        with self.transaction_service.transaction() as session:
            # Your complex operations here
            pass
```

## Performance Considerations

1. **Keep transactions short** - Long transactions can cause deadlocks
2. **Avoid external API calls** within transactions
3. **Use read-only transactions** for complex queries
4. **Consider batch operations** for bulk updates
5. **Monitor transaction duration** in production

## Monitoring and Debugging

```python
import time
import logging

logger = logging.getLogger(__name__)

async def monitored_transaction(self):
    start_time = time.time()

    try:
        with self.transaction_service.transaction() as session:
            # Your operations here
            pass

        duration = time.time() - start_time
        logger.info(f"Transaction completed in {duration:.2f}s")

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Transaction failed after {duration:.2f}s: {e}")
        raise
```

This guide provides comprehensive coverage of transaction management in your FastAPI boilerplate. The key is to understand when you need transactions and how to structure your code to take advantage of the atomic nature of database transactions.
