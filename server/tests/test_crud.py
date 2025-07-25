"""
Tests for CRUD operations.
"""
import pytest

from app.crud.user import (
    get_user_by_email,
    create_user,
    authenticate_user,
    get_user_by_id,
    get_all_users
)
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


class TestUserCRUD:
    """Test cases for user CRUD operations."""

    def test_create_user(self, db_session):
        """Test creating a user."""
        user_data = UserCreate(email="test@example.com", password="testpassword")
        user = create_user(db_session, user_data)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.hashed_password != "testpassword"  # Should be hashed
        assert len(user.hashed_password) > 0

    def test_get_user_by_email_exists(self, db_session, created_user):
        """Test getting an existing user by email."""
        user = get_user_by_email(db_session, created_user.email)
        
        assert user is not None
        assert user.email == created_user.email
        assert user.id == created_user.id

    def test_get_user_by_email_not_exists(self, db_session):
        """Test getting a non-existent user by email."""
        user = get_user_by_email(db_session, "nonexistent@example.com")
        assert user is None

    def test_get_user_by_id_exists(self, db_session, created_user):
        """Test getting an existing user by ID."""
        user = get_user_by_id(db_session, created_user.id)
        
        assert user is not None
        assert user.id == created_user.id
        assert user.email == created_user.email

    def test_get_user_by_id_not_exists(self, db_session):
        """Test getting a non-existent user by ID."""
        user = get_user_by_id(db_session, 99999)
        assert user is None

    def test_authenticate_user_valid_credentials(self, db_session, sample_user_data):
        """Test authenticating a user with valid credentials."""
        # Create user
        user_create = UserCreate(**sample_user_data)
        created_user = create_user(db_session, user_create)

        # Authenticate
        user = authenticate_user(
            db_session, 
            sample_user_data["email"], 
            sample_user_data["password"]
        )
        
        assert user is not None
        assert user.email == created_user.email
        assert user.id == created_user.id

    def test_authenticate_user_invalid_password(self, db_session, created_user):
        """Test authenticating a user with invalid password."""
        user = authenticate_user(
            db_session, 
            created_user.email, 
            "wrongpassword"
        )
        assert user is None

    def test_authenticate_user_invalid_email(self, db_session):
        """Test authenticating with non-existent email."""
        user = authenticate_user(
            db_session, 
            "nonexistent@example.com", 
            "anypassword"
        )
        assert user is None

    def test_get_all_users_empty(self, db_session):
        """Test getting all users when database is empty."""
        users = get_all_users(db_session)
        assert users == []

    def test_get_all_users_with_data(self, db_session, multiple_users_data):
        """Test getting all users when users exist."""
        # Create multiple users
        for user_data in multiple_users_data:
            user_create = UserCreate(**user_data)
            create_user(db_session, user_create)

        # Get all users
        users = get_all_users(db_session)
        
        assert len(users) == len(multiple_users_data)
        emails = [user.email for user in users]
        expected_emails = [data["email"] for data in multiple_users_data]
        assert set(emails) == set(expected_emails)

    def test_get_all_users_pagination(self, db_session, multiple_users_data):
        """Test pagination in get_all_users."""
        # Create multiple users
        for user_data in multiple_users_data:
            user_create = UserCreate(**user_data)
            create_user(db_session, user_create)

        # Test skip and limit
        users_page1 = get_all_users(db_session, skip=0, limit=2)
        users_page2 = get_all_users(db_session, skip=2, limit=2)
        
        assert len(users_page1) == 2
        assert len(users_page2) == 1  # Only 3 users total
        
        # Ensure no overlap
        page1_ids = {user.id for user in users_page1}
        page2_ids = {user.id for user in users_page2}
        assert page1_ids.isdisjoint(page2_ids) 