"""
Test configuration and fixtures for the Todo API.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import create_app
from app.models.user import User

# Test database URL - using SQLite in memory for fast testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123"  # 8+ characters, meets validation
    }


@pytest.fixture
def created_user(db_session, sample_user_data):
    """Create a user in the database for testing."""
    from app.crud.user import create_user
    from app.schemas.user import UserCreate
    
    user_create = UserCreate(**sample_user_data)
    user = create_user(db_session, user_create)
    return user


@pytest.fixture
def auth_headers(client, sample_user_data):
    """Get authentication headers for a logged-in user."""
    # Register user
    response = client.post("/user/register", json=sample_user_data)
    assert response.status_code == 201
    
    # Login user
    login_data = {
        "username": sample_user_data["email"],
        "password": sample_user_data["password"]
    }
    response = client.post("/user/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def multiple_users_data():
    """Sample data for multiple users."""
    return [
        {"email": "user1@example.com", "password": "password1"},
        {"email": "user2@example.com", "password": "password2"},
        {"email": "user3@example.com", "password": "password3"},
    ] 