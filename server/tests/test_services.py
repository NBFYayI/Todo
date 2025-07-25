"""
Tests for service layer.
"""
import pytest
from fastapi import HTTPException
from jose import jwt

from app.services.user import (
    register_user,
    login_user,
    get_user_from_token,
    get_user_by_id_service,
    get_all_users_service
)
from app.schemas.user import UserCreate
from app.core.config import settings
from app.core.security import create_access_token


class TestUserServices:
    """Test cases for user services."""

    def test_register_user_success(self, db_session, sample_user_data):
        """Test successful user registration."""
        user_create = UserCreate(**sample_user_data)
        user = register_user(db_session, user_create)

        assert user.email == sample_user_data["email"]
        assert user.id is not None
        assert user.hashed_password != sample_user_data["password"]

    def test_register_user_duplicate_email(self, db_session, created_user, sample_user_data):
        """Test registering user with duplicate email raises exception."""
        user_create = UserCreate(**sample_user_data)
        
        with pytest.raises(HTTPException) as exc_info:
            register_user(db_session, user_create)
        
        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)

    def test_login_user_success(self, db_session, sample_user_data):
        """Test successful user login."""
        # Register user first
        user_create = UserCreate(**sample_user_data)
        register_user(db_session, user_create)

        # Login
        token = login_user(
            db_session, 
            sample_user_data["email"], 
            sample_user_data["password"]
        )

        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert "sub" in payload
        assert "exp" in payload

    def test_login_user_invalid_email(self, db_session):
        """Test login with invalid email raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            login_user(db_session, "invalid@example.com", "password")
        
        assert exc_info.value.status_code == 401
        assert "Incorrect email or password" in str(exc_info.value.detail)

    def test_login_user_invalid_password(self, db_session, created_user):
        """Test login with invalid password raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            login_user(db_session, created_user.email, "wrongpassword")
        
        assert exc_info.value.status_code == 401
        assert "Incorrect email or password" in str(exc_info.value.detail)

    def test_get_user_from_token_success(self, db_session, created_user):
        """Test getting user from valid token."""
        token = create_access_token(str(created_user.id))
        user = get_user_from_token(db_session, token)

        assert user.id == created_user.id
        assert user.email == created_user.email

    def test_get_user_from_token_invalid_token(self, db_session):
        """Test getting user from invalid token raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            get_user_from_token(db_session, "invalid_token")
        
        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in str(exc_info.value.detail)

    def test_get_user_from_token_nonexistent_user(self, db_session):
        """Test getting user from token for non-existent user."""
        token = create_access_token("99999")  # Non-existent user ID
        
        with pytest.raises(HTTPException) as exc_info:
            get_user_from_token(db_session, token)
        
        assert exc_info.value.status_code == 401
        assert "User not found" in str(exc_info.value.detail)

    def test_get_user_by_id_service_success(self, db_session, created_user):
        """Test getting user by ID through service."""
        user = get_user_by_id_service(db_session, created_user.id)

        assert user.id == created_user.id
        assert user.email == created_user.email

    def test_get_user_by_id_service_not_found(self, db_session):
        """Test getting non-existent user by ID raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            get_user_by_id_service(db_session, 99999)
        
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

    def test_get_all_users_service_empty(self, db_session):
        """Test getting all users when database is empty."""
        users = get_all_users_service(db_session)
        assert users == []

    def test_get_all_users_service_with_data(self, db_session, multiple_users_data):
        """Test getting all users through service."""
        # Create users
        for user_data in multiple_users_data:
            user_create = UserCreate(**user_data)
            register_user(db_session, user_create)

        # Get all users
        users = get_all_users_service(db_session)
        
        assert len(users) == len(multiple_users_data)
        emails = [user.email for user in users]
        expected_emails = [data["email"] for data in multiple_users_data]
        assert set(emails) == set(expected_emails)

    def test_get_all_users_service_pagination(self, db_session, multiple_users_data):
        """Test pagination in get_all_users_service."""
        # Create users
        for user_data in multiple_users_data:
            user_create = UserCreate(**user_data)
            register_user(db_session, user_create)

        # Test pagination
        users_page1 = get_all_users_service(db_session, skip=0, limit=2)
        users_page2 = get_all_users_service(db_session, skip=2, limit=2)
        
        assert len(users_page1) == 2
        assert len(users_page2) == 1 