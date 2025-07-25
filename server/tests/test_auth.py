"""
Tests for authentication and security functionality.
"""
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from app.core.config import settings


class TestPasswordSecurity:
    """Test cases for password hashing and verification."""

    def test_password_hashing(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        # Hash should be non-empty string
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        # Hash should be deterministic but salted (different each time)
        hashed2 = get_password_hash(password)
        assert hashed != hashed2

    def test_password_verification_success(self):
        """Test successful password verification."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Test failed password verification."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_empty_password_handling(self):
        """Test handling of empty passwords."""
        # Test empty password hashing
        empty_hash = get_password_hash("")
        assert isinstance(empty_hash, str)
        assert len(empty_hash) > 0
        
        # Test verification with empty password
        assert verify_password("", empty_hash) is True
        assert verify_password("not_empty", empty_hash) is False


class TestJWTTokens:
    """Test cases for JWT token creation and validation."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        user_id = "123"
        token = create_access_token(user_id)
        
        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Token should be valid JWT
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert payload["sub"] == user_id
        assert "exp" in payload

    def test_decode_access_token_success(self):
        """Test successful token decoding."""
        user_id = "123"
        token = create_access_token(user_id)
        
        decoded_user_id = decode_access_token(token)
        assert decoded_user_id == user_id

    def test_decode_access_token_invalid_token(self):
        """Test decoding invalid token."""
        with pytest.raises(JWTError):
            decode_access_token("invalid_token")

    def test_decode_access_token_expired_token(self):
        """Test decoding expired token."""
        user_id = "123"
        # Create token that expires immediately
        expire = datetime.utcnow() - timedelta(minutes=1)  # Already expired
        to_encode = {"exp": expire, "sub": user_id}
        expired_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        
        with pytest.raises(JWTError):
            decode_access_token(expired_token)

    def test_decode_access_token_no_subject(self):
        """Test decoding token without subject."""
        # Create token without 'sub' field
        expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode = {"exp": expire}  # Missing 'sub'
        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        
        with pytest.raises(JWTError):
            decode_access_token(token)

    def test_decode_access_token_wrong_secret(self):
        """Test decoding token with wrong secret."""
        user_id = "123"
        # Create token with different secret
        expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode = {"exp": expire, "sub": user_id}
        token = jwt.encode(to_encode, "wrong_secret", algorithm="HS256")
        
        with pytest.raises(JWTError):
            decode_access_token(token)

    def test_token_expiration_time(self):
        """Test that token has correct expiration time."""
        user_id = "123"
        before_creation = datetime.now(timezone.utc)
        token = create_access_token(user_id)
        after_creation = datetime.now(timezone.utc)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        token_exp = datetime.fromtimestamp(payload["exp"], timezone.utc)  # Use UTC timestamp conversion
        
        # Token should expire within the configured time range
        expected_min = before_creation + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expected_max = after_creation + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        assert expected_min <= token_exp <= expected_max

    def test_different_tokens_for_same_user(self):
        """Test that different tokens are generated for the same user."""
        user_id = "123"
        token1 = create_access_token(user_id)
        token2 = create_access_token(user_id)
        
        # Tokens should be different (due to different timestamps)
        assert token1 != token2
        
        # But both should decode to the same user
        assert decode_access_token(token1) == user_id
        assert decode_access_token(token2) == user_id 