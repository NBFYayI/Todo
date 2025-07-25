"""
Tests for API endpoints (controllers).
"""
import pytest


class TestUserEndpoints:
    """Test cases for user API endpoints."""

    def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration."""
        response = client.post("/user/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert "id" in data
        assert "hashed_password" not in data  # Password should not be returned

    def test_register_user_duplicate_email(self, client, sample_user_data):
        """Test registering user with duplicate email."""
        # Register user first time
        response = client.post("/user/register", json=sample_user_data)
        assert response.status_code == 201

        # Try to register again with same email
        response = client.post("/user/register", json=sample_user_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_user_invalid_email(self, client):
        """Test registering user with invalid email."""
        invalid_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        response = client.post("/user/register", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_register_user_missing_password(self, client):
        """Test registering user without password."""
        invalid_data = {
            "email": "test@example.com"
        }
        response = client.post("/user/register", json=invalid_data)
        assert response.status_code == 422

    def test_register_user_short_password(self, client):
        """Test registering user with password too short."""
        invalid_data = {
            "email": "test@example.com",
            "password": "short"  # Less than 8 characters
        }
        response = client.post("/user/register", json=invalid_data)
        assert response.status_code == 422

    def test_login_user_success(self, client, sample_user_data):
        """Test successful user login."""
        # Register user first
        register_response = client.post("/user/register", json=sample_user_data)
        assert register_response.status_code == 201

        # Login
        login_data = {
            "username": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = client.post("/user/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_user_invalid_credentials(self, client, sample_user_data):
        """Test login with invalid credentials."""
        # Register user first
        client.post("/user/register", json=sample_user_data)

        # Try login with wrong password
        login_data = {
            "username": sample_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/user/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_user_nonexistent_email(self, client):
        """Test login with non-existent email."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        response = client.post("/user/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_get_all_users_empty(self, client):
        """Test getting all users when database is empty."""
        response = client.get("/user/users")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_users_with_data(self, client, multiple_users_data):
        """Test getting all users when users exist."""
        # Register multiple users
        for user_data in multiple_users_data:
            response = client.post("/user/register", json=user_data)
            assert response.status_code == 201

        # Get all users
        response = client.get("/user/users")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(multiple_users_data)
        
        emails = [user["email"] for user in data]
        expected_emails = [user_data["email"] for user_data in multiple_users_data]
        assert set(emails) == set(expected_emails)

    def test_get_all_users_pagination(self, client, multiple_users_data):
        """Test pagination in get all users."""
        # Register multiple users
        for user_data in multiple_users_data:
            client.post("/user/register", json=user_data)

        # Test pagination
        response1 = client.get("/user/users?skip=0&limit=2")
        response2 = client.get("/user/users?skip=2&limit=2")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        assert len(data1) == 2
        assert len(data2) == 1  # Only 3 users total
        
        # Ensure no overlap
        ids1 = {user["id"] for user in data1}
        ids2 = {user["id"] for user in data2}
        assert ids1.isdisjoint(ids2)

    def test_get_user_by_id_success(self, client, sample_user_data):
        """Test getting user by ID."""
        # Register user
        register_response = client.post("/user/register", json=sample_user_data)
        user_id = register_response.json()["id"]

        # Get user by ID
        response = client.get(f"/user/users/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == sample_user_data["email"]

    def test_get_user_by_id_not_found(self, client):
        """Test getting non-existent user by ID."""
        response = client.get("/user/users/99999")
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_get_user_by_id_invalid_id(self, client):
        """Test getting user with invalid ID format."""
        response = client.get("/user/users/invalid")
        
        assert response.status_code == 422  # Validation error

    def test_get_current_user_success(self, client, auth_headers):
        """Test getting current user with valid token."""
        # This requires a protected endpoint that uses get_current_user
        # For now, we'll test that the auth_headers fixture works
        assert "Authorization" in auth_headers
        assert auth_headers["Authorization"].startswith("Bearer ")

    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token."""
        # Since get_current_user is a dependency, let's test it indirectly
        # by checking that endpoints requiring auth return 401 without token
        # This is a placeholder test - you'd implement this when you have protected endpoints
        pass

    def test_protected_endpoint_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        # This would test against a protected endpoint when you have one
        # For now, it's a placeholder
        pass


class TestRootEndpoints:
    """Test cases for root endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        # This depends on your root endpoint implementation
        # Adjust based on what your root endpoint returns
        assert response.status_code == 200 