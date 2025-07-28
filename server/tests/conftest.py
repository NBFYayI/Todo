"""
Test configuration and fixtures for the Todo API.
"""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import create_app
from app.models.user import User

# Test database URL - using SQLite in memory for fast testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a fresh database session for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency."""
    async def override_get_db():
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


@pytest_asyncio.fixture
async def created_user(db_session, sample_user_data):
    """Create a user in the database for testing."""
    from app.crud.user import create_user
    from app.schemas.user import UserCreate
    
    user_create = UserCreate(**sample_user_data)
    user = await create_user(db_session, user_create)
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


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    from datetime import datetime, timedelta
    
    return {
        "title": "Test Task",
        "description": "This is a test task description",
        "due_date": (datetime.now() + timedelta(days=7)).isoformat()
    }


@pytest_asyncio.fixture
async def created_task(db_session, created_user, sample_task_data):
    """Create a task in the database for testing."""
    from app.crud.task import create_task
    from app.schemas.task import TaskCreate
    
    task_create = TaskCreate(**sample_task_data)
    task = await create_task(db_session, created_user.id, task_create)
    return task


@pytest.fixture
def multiple_tasks_data():
    """Sample data for multiple tasks."""
    from datetime import datetime, timedelta
    
    return [
        {
            "title": "Task 1",
            "description": "First test task",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat()
        },
        {
            "title": "Task 2", 
            "description": "Second test task",
            "due_date": (datetime.now() + timedelta(days=3)).isoformat()
        },
        {
            "title": "Task 3",
            "description": "Third test task",
            "due_date": None  # No due date
        }
    ]


@pytest_asyncio.fixture 
async def created_multiple_tasks(db_session, created_user, multiple_tasks_data):
    """Create multiple tasks in the database for testing."""
    from app.crud.task import create_task
    from app.schemas.task import TaskCreate
    
    tasks = []
    for task_data in multiple_tasks_data:
        task_create = TaskCreate(**task_data)
        task = await create_task(db_session, created_user.id, task_create)
        tasks.append(task)
    return tasks 