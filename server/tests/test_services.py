"""
Tests for service layer.
"""
import pytest
import pytest_asyncio
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

    @pytest.mark.asyncio
    async def test_register_user_success(self, db_session, sample_user_data):
        """Test successful user registration."""
        user_create = UserCreate(**sample_user_data)
        user = await register_user(db_session, user_create)

        assert user.email == sample_user_data["email"]
        assert user.id is not None
        assert user.hashed_password != sample_user_data["password"]

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, db_session, created_user, sample_user_data):
        """Test registering user with duplicate email raises exception."""
        user_create = UserCreate(**sample_user_data)
        
        with pytest.raises(HTTPException) as exc_info:
            await register_user(db_session, user_create)
        
        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_user_success(self, db_session, sample_user_data):
        """Test successful user login."""
        # Register user first
        user_create = UserCreate(**sample_user_data)
        await register_user(db_session, user_create)

        # Login
        token = await login_user(
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

    @pytest.mark.asyncio
    async def test_login_user_invalid_email(self, db_session):
        """Test login with invalid email raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            await login_user(db_session, "invalid@example.com", "password")
        
        assert exc_info.value.status_code == 401
        assert "Incorrect email or password" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_user_invalid_password(self, db_session, created_user):
        """Test login with invalid password raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            await login_user(db_session, created_user.email, "wrongpassword")
        
        assert exc_info.value.status_code == 401
        assert "Incorrect email or password" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_user_from_token_success(self, db_session, created_user):
        """Test getting user from valid token."""
        token = create_access_token(str(created_user.id))
        user = await get_user_from_token(db_session, token)

        assert user.id == created_user.id
        assert user.email == created_user.email

    @pytest.mark.asyncio
    async def test_get_user_from_token_invalid_token(self, db_session):
        """Test getting user from invalid token raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            await get_user_from_token(db_session, "invalid_token")
        
        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_user_from_token_nonexistent_user(self, db_session):
        """Test getting user from token for non-existent user."""
        token = create_access_token("99999")  # Non-existent user ID
        
        with pytest.raises(HTTPException) as exc_info:
            await get_user_from_token(db_session, token)
        
        assert exc_info.value.status_code == 401
        assert "User not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_user_by_id_service_success(self, db_session, created_user):
        """Test getting user by ID through service."""
        user = await get_user_by_id_service(db_session, created_user.id)

        assert user.id == created_user.id
        assert user.email == created_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_id_service_not_found(self, db_session):
        """Test getting non-existent user by ID raises exception."""
        with pytest.raises(HTTPException) as exc_info:
            await get_user_by_id_service(db_session, 99999)
        
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_all_users_service_empty(self, db_session):
        """Test getting all users when database is empty."""
        users = await get_all_users_service(db_session)
        assert users == []

    @pytest.mark.asyncio
    async def test_get_all_users_service_with_data(self, db_session, multiple_users_data):
        """Test getting all users through service."""
        # Create users
        for user_data in multiple_users_data:
            user_create = UserCreate(**user_data)
            await register_user(db_session, user_create)

        # Get all users
        users = await get_all_users_service(db_session)
        
        assert len(users) == len(multiple_users_data)
        emails = [user.email for user in users]
        expected_emails = [data["email"] for data in multiple_users_data]
        assert set(emails) == set(expected_emails)

    @pytest.mark.asyncio
    async def test_get_all_users_service_pagination(self, db_session, multiple_users_data):
        """Test pagination in get_all_users_service."""
        # Create users
        for user_data in multiple_users_data:
            user_create = UserCreate(**user_data)
            await register_user(db_session, user_create)

        # Test pagination
        users_page1 = await get_all_users_service(db_session, skip=0, limit=2)
        users_page2 = await get_all_users_service(db_session, skip=2, limit=2)
        
        assert len(users_page1) == 2
        assert len(users_page2) == 1 


class TestTaskService:
    """Test cases for task service operations."""

    @pytest.mark.asyncio
    async def test_list_user_tasks_success(self, db_session, created_multiple_tasks, created_user):
        """Test successfully listing user tasks."""
        from app.services.task import list_user_tasks
        
        tasks = await list_user_tasks(db_session, created_user.id, skip=0, limit=100)
        
        assert len(tasks) == 3
        assert all(task.user_id == created_user.id for task in tasks)

    @pytest.mark.asyncio
    async def test_list_user_tasks_no_tasks(self, db_session, created_user):
        """Test listing tasks when user has no tasks."""
        from app.services.task import list_user_tasks
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            await list_user_tasks(db_session, created_user.id, skip=0, limit=100)
        
        assert exc_info.value.status_code == 404
        assert "No tasks found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_existing_task_success(self, db_session, created_task, created_user):
        """Test successfully getting an existing task."""
        from app.services.task import get_existing_task
        
        task = await get_existing_task(db_session, created_user.id, created_task.id)
        
        assert task.id == created_task.id
        assert task.user_id == created_user.id

    @pytest.mark.asyncio
    async def test_get_existing_task_not_found(self, db_session, created_user):
        """Test getting a non-existent task."""
        from app.services.task import get_existing_task
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            await get_existing_task(db_session, created_user.id, 99999)
        
        assert exc_info.value.status_code == 404
        assert "Task not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_existing_task_unauthorized(self, db_session, created_task):
        """Test getting a task that belongs to another user."""
        from app.services.task import get_existing_task
        from app.crud.user import create_user
        from app.schemas.user import UserCreate
        from fastapi import HTTPException
        
        # Create another user
        other_user = await create_user(db_session, UserCreate(email="other@test.com", password="password"))
        
        with pytest.raises(HTTPException) as exc_info:
            await get_existing_task(db_session, other_user.id, created_task.id)
        
        assert exc_info.value.status_code == 403
        assert "Unauthorized access" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_make_task_success(self, db_session, created_user, sample_task_data):
        """Test successfully creating a task."""
        from app.services.task import make_task
        from app.schemas.task import TaskCreate
        
        task_data = TaskCreate(**sample_task_data)
        task = await make_task(db_session, created_user.id, task_data)
        
        assert task.id is not None
        assert task.user_id == created_user.id
        assert task.title == sample_task_data["title"]
        assert task.description == sample_task_data["description"]

    @pytest.mark.asyncio
    async def test_change_task_success(self, db_session, created_task, created_user):
        """Test successfully updating a task."""
        from app.services.task import change_task
        from app.schemas.task import TaskUpdate
        
        update_data = TaskUpdate(
            title="Updated Title",
            completed=True
        )
        
        updated_task = await change_task(db_session, created_user.id, created_task.id, update_data)
        
        assert updated_task.title == "Updated Title"
        assert updated_task.completed is True
        assert updated_task.id == created_task.id

    @pytest.mark.asyncio
    async def test_change_task_not_found(self, db_session, created_user):
        """Test updating a non-existent task."""
        from app.services.task import change_task
        from app.schemas.task import TaskUpdate
        from fastapi import HTTPException
        
        update_data = TaskUpdate(title="Updated Title")
        
        with pytest.raises(HTTPException) as exc_info:
            await change_task(db_session, created_user.id, 99999, update_data)
        
        assert exc_info.value.status_code == 404
        assert "Task not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_change_task_unauthorized(self, db_session, created_task):
        """Test updating a task that belongs to another user."""
        from app.services.task import change_task
        from app.crud.user import create_user
        from app.schemas.user import UserCreate
        from app.schemas.task import TaskUpdate
        from fastapi import HTTPException
        
        # Create another user
        other_user = await create_user(db_session, UserCreate(email="other@test.com", password="password"))
        
        update_data = TaskUpdate(title="Hacked Title")
        
        with pytest.raises(HTTPException) as exc_info:
            await change_task(db_session, other_user.id, created_task.id, update_data)
        
        assert exc_info.value.status_code == 403
        assert "Unauthorized access" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_remove_task_success(self, db_session, created_task, created_user):
        """Test successfully removing a task."""
        from app.services.task import remove_task
        from app.crud.task import get_task
        
        task_id = created_task.id
        
        # Remove the task
        await remove_task(db_session, created_user.id, task_id)
        
        # Verify it's deleted
        deleted_task = await get_task(db_session, task_id)
        assert deleted_task is None

    @pytest.mark.asyncio
    async def test_remove_task_not_found(self, db_session, created_user):
        """Test removing a non-existent task."""
        from app.services.task import remove_task
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            await remove_task(db_session, created_user.id, 99999)
        
        assert exc_info.value.status_code == 404
        assert "Task not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_remove_task_unauthorized(self, db_session, created_task):
        """Test removing a task that belongs to another user."""
        from app.services.task import remove_task
        from app.crud.user import create_user
        from app.schemas.user import UserCreate
        from fastapi import HTTPException
        
        # Create another user
        other_user = await create_user(db_session, UserCreate(email="other@test.com", password="password"))
        
        with pytest.raises(HTTPException) as exc_info:
            await remove_task(db_session, other_user.id, created_task.id)
        
        assert exc_info.value.status_code == 403
        assert "Unauthorized access" in str(exc_info.value.detail) 