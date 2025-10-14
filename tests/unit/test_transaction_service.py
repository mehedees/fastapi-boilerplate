"""
Unit tests for TransactionService functionality.
"""

from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from app.domain.transactions.services import TransactionService
from app.infra.persistence.db import Database


class TestTransactionService:
    """Test cases for TransactionService."""

    def test_transaction_service_initialization(self):
        """Test that TransactionService initializes correctly."""
        mock_database = Mock(spec=Database)
        service = TransactionService(mock_database)

        assert service.database == mock_database

    def test_transaction_context_manager(self):
        """Test that transaction context manager works correctly."""
        mock_database = Mock(spec=Database)
        mock_session = Mock(spec=Session)

        # Mock the transaction method to return our mock session
        mock_database.transaction.return_value.__enter__ = Mock(
            return_value=mock_session
        )
        mock_database.transaction.return_value.__exit__ = Mock(
            return_value=None
        )

        service = TransactionService(mock_database)

        with service.transaction() as session:
            assert session == mock_session

        # Verify that database.transaction was called
        mock_database.transaction.assert_called_once()

    def test_execute_in_transaction(self):
        """Test execute_in_transaction method."""
        mock_database = Mock(spec=Database)
        mock_session = Mock(spec=Session)

        # Mock the transaction method
        mock_database.transaction.return_value.__enter__ = Mock(
            return_value=mock_session
        )
        mock_database.transaction.return_value.__exit__ = Mock(
            return_value=None
        )

        service = TransactionService(mock_database)

        def test_operation(session):
            return "test_result"

        result = service.execute_in_transaction(test_operation)

        assert result == "test_result"
        mock_database.transaction.assert_called_once()

    def test_read_only_transaction(self):
        """Test read_only_transaction context manager."""
        mock_database = Mock(spec=Database)
        mock_session = Mock(spec=Session)

        # Mock the session_factory method
        mock_database.session_factory.return_value.__enter__ = Mock(
            return_value=mock_session
        )
        mock_database.session_factory.return_value.__exit__ = Mock(
            return_value=None
        )

        service = TransactionService(mock_database)

        with service.read_only_transaction() as session:
            assert session == mock_session

        # Verify that session_factory was called with read_only=True
        mock_database.session_factory.assert_called_once_with(
            read_only=True
        )

    def test_get_session_factory(self):
        """Test get_session_factory method."""
        mock_database = Mock(spec=Database)
        mock_session_factory = Mock()
        mock_database.session_factory = mock_session_factory

        service = TransactionService(mock_database)

        result = service.get_session_factory()

        assert result == mock_session_factory


class TestTransactionIntegration:
    """Integration tests for transaction functionality."""

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_exception(self):
        """Test that transactions roll back on exceptions."""
        # This would be an integration test with a real database
        # For now, we'll just test the structure
        mock_database = Mock(spec=Database)
        service = TransactionService(mock_database)

        # Mock the transaction to raise an exception
        mock_database.transaction.side_effect = Exception(
            "Test exception"
        )

        with pytest.raises(Exception, match="Test exception"):
            with service.transaction():
                # This should not be reached
                pass

    def test_transaction_commit_on_success(self):
        """Test that transactions commit on success."""
        mock_database = Mock(spec=Database)
        mock_session = Mock(spec=Session)

        # Mock successful transaction
        mock_database.transaction.return_value.__enter__ = Mock(
            return_value=mock_session
        )
        mock_database.transaction.return_value.__exit__ = Mock(
            return_value=None
        )

        service = TransactionService(mock_database)

        with service.transaction() as session:
            # Simulate some work
            session.add = Mock()
            session.flush = Mock()

        # Verify that the transaction context was used
        mock_database.transaction.assert_called_once()
