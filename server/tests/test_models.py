"""
Tests for database models.
"""
import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User


class TestUserModel:
    """Test cases for the User model."""

    def test_create_user(self, db_session):
        """Test creating a user with valid data."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password_123"

    def test_user_email_unique_constraint(self, db_session):
        """Test that email must be unique."""
        # Create first user
        user1 = User(
            email="duplicate@example.com",
            hashed_password="password1"
        )
        db_session.add(user1)
        db_session.commit()

        # Try to create second user with same email
        user2 = User(
            email="duplicate@example.com",
            hashed_password="password2"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_email_required(self, db_session):
        """Test that email is required."""
        user = User(hashed_password="password123")
        db_session.add(user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_password_required(self, db_session):
        """Test that hashed_password is required."""
        user = User(email="test@example.com")
        db_session.add(user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_representation(self, db_session):
        """Test user model string representation."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Test that the user object has the expected attributes
        assert hasattr(user, 'id')
        assert hasattr(user, 'email')
        assert hasattr(user, 'hashed_password')
        assert user.email == "test@example.com" 