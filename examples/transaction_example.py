"""
Example demonstrating proper transaction usage with separation of concerns.

This example shows how to handle multiple interdependent operations
within a single transaction while maintaining clean architecture.
"""

from app.domain.transactions.services import TransactionService
from app.domain.users.entities.refresh_token_entities import (
    RefreshTokenCreateEntity,
)
from app.domain.users.entities.user_entities import UserCreateEntity


class ExampleUserService:
    """
    Example service demonstrating proper transaction usage.

    This service shows how to handle complex business operations
    that require multiple database operations within a single transaction.
    """

    def __init__(
        self,
        user_repo,
        refresh_token_repo,
        transaction_service: TransactionService,
        hash_manager,
        token_util,
        user_agent_util,
        settings,
    ):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        self.transaction_service = transaction_service
        self.hash_manager = hash_manager
        self.token_util = token_util
        self.user_agent_util = user_agent_util
        self.settings = settings

    async def create_user_with_initial_setup(
        self, user_data: dict, user_agent: str
    ) -> dict:
        """
        Example: Create user with initial setup in a single transaction.

        This method demonstrates:
        1. Proper separation of concerns (service calls repositories)
        2. Transaction management (all operations succeed or fail together)
        3. Business logic orchestration
        """
        # Validate input data (outside transaction for early validation)
        if not user_data.get("email"):
            raise ValueError("Email is required")

        # Hash password
        user_data["password"] = self.hash_manager.hash_password_argon2(
            user_data["password"]
        )

        # Parse device info
        device_info = self.user_agent_util.parse_user_agent(user_agent)
        device_info_text = self._make_device_info_str(device_info)

        # Perform all operations within a single transaction
        with self.transaction_service.transaction() as session:
            # 1. Create user using repository
            user_entity = UserCreateEntity(**user_data)
            created_user = await self.user_repo.create_user(
                user_entity, session=session
            )

            # 2. Create refresh token using repository
            refresh_token_entity = RefreshTokenCreateEntity(
                user_id=created_user.id,
                device_info=device_info_text,
                expires_at=self._get_token_expiry(),
            )
            created_token = (
                await self.refresh_token_repo.create_refresh_token(
                    refresh_token_entity, session=session
                )
            )

            # 3. Generate JWT tokens (business logic, not database operations)
            access_token = self._generate_access_token(created_user)
            refresh_token = self._generate_refresh_token(
                created_user, created_token
            )

            # All operations completed successfully - transaction will commit
            return {
                "user": created_user,
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

    async def bulk_user_operations(
        self, operations: list[dict]
    ) -> list:
        """
        Example: Bulk operations within a single transaction.

        This demonstrates how to handle multiple related operations
        that must all succeed or all fail together.
        """
        results = []

        with self.transaction_service.transaction() as session:
            for operation in operations:
                op_type = operation.get("type")
                data = operation.get("data", {})

                if op_type == "create_user":
                    # Use repository method
                    user_entity = UserCreateEntity(**data)
                    result = await self.user_repo.create_user(
                        user_entity, session=session
                    )
                    results.append(result)

                elif op_type == "create_token":
                    # Use repository method
                    token_entity = RefreshTokenCreateEntity(**data)
                    result = await self.refresh_token_repo.create_refresh_token(
                        token_entity, session=session
                    )
                    results.append(result)

                elif op_type == "delete_tokens":
                    # Use repository method
                    user_id = data.get("user_id")
                    deleted_count = await self.refresh_token_repo.delete_refresh_token_by_user_id(
                        user_id
                    )
                    results.append({"deleted_count": deleted_count})

                else:
                    raise ValueError(
                        f"Unknown operation type: {op_type}"
                    )

            # All operations completed successfully - transaction will commit
            return results

    def _make_device_info_str(self, device_info: dict) -> str:
        """Helper method for device info formatting."""
        # Implementation would format device info
        return str(device_info)

    def _get_token_expiry(self):
        """Helper method for token expiry calculation."""
        from datetime import datetime, timedelta

        return datetime.now() + timedelta(seconds=3600)

    def _generate_access_token(self, user):
        """Helper method for access token generation."""
        # Implementation would generate JWT
        return f"access_token_for_{user.id}"

    def _generate_refresh_token(self, user, token_entity):
        """Helper method for refresh token generation."""
        # Implementation would generate JWT
        return f"refresh_token_for_{user.id}_{token_entity.id}"


# Usage example
async def example_usage():
    """
    Example of how to use the service with proper transaction handling.
    """
    # This would be injected via DI container in real application
    # service = container.user_service()

    # Example 1: Create user with initial setup
    print("Example usage structure:")
    print("1. Inject service via DI container")
    print("2. Call service methods with transaction support")
    print("3. Handle exceptions for automatic rollback")

    # Example 2: Bulk operations
    print("Bulk operations structure:")
    print("1. Define operations list")
    print("2. Call bulk_user_operations method")
    print("3. All operations succeed or all fail together")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
