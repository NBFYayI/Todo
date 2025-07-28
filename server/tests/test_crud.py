"""
Tests for CRUD operations.
"""
import pytest
import pytest_asyncio

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

    @pytest.mark.asyncio
    async def test_create_user(self, db_session):
        """Test creating a user."""
        user_data = UserCreate(email="test@example.com", password="testpassword")
        user = await create_user(db_session, user_data)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.hashed_password != "testpassword"  # Should be hashed
        assert len(user.hashed_password) > 0

    @pytest.mark.asyncio
    async def test_get_user_by_email_exists(self, db_session, created_user):
        """Test getting an existing user by email."""
        user = await get_user_by_email(db_session, created_user.email)
        
        assert user is not None
        assert user.email == created_user.email
        assert user.id == created_user.id

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_exists(self, db_session):
        """Test getting a non-existent user by email."""
        user = await get_user_by_email(db_session, "nonexistent@example.com")
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_exists(self, db_session, created_user):
        """Test getting an existing user by ID."""
        user = await get_user_by_id(db_session, created_user.id)
        
        assert user is not None
        assert user.id == created_user.id
        assert user.email == created_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_exists(self, db_session):
        """Test getting a non-existent user by ID."""
        user = await get_user_by_id(db_session, 99999)
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_valid_credentials(self, db_session, sample_user_data):
        """Test authenticating a user with valid credentials."""
        # Create user
        user_create = UserCreate(**sample_user_data)
        created_user = await create_user(db_session, user_create)

        # Authenticate
        user = await authenticate_user(
            db_session, 
            sample_user_data["email"], 
            sample_user_data["password"]
        )
        
        assert user is not None
        assert user.email == created_user.email
        assert user.id == created_user.id

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self, db_session, created_user):
        """Test authenticating a user with invalid password."""
        user = await authenticate_user(
            db_session, 
            created_user.email, 
            "wrongpassword"
        )
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_email(self, db_session):
        """Test authenticating with non-existent email."""
        user = await authenticate_user(
            db_session, 
            "nonexistent@example.com", 
            "anypassword"
        )
        assert user is None

    @pytest.mark.asyncio
    async def test_get_all_users_empty(self, db_session):
        """Test getting all users when database is empty."""
        users = await get_all_users(db_session)
        assert users == []

    @pytest.mark.asyncio
    async def test_get_all_users_with_data(self, db_session, multiple_users_data):
        """Test getting all users when users exist."""
        # Create multiple users
        for user_data in multiple_users_data:
            user_create = UserCreate(**user_data)
            await create_user(db_session, user_create)

        # Get all users
        users = await get_all_users(db_session)
        
        assert len(users) == len(multiple_users_data)
        emails = [user.email for user in users]
        expected_emails = [data["email"] for data in multiple_users_data]
        assert set(emails) == set(expected_emails)

    @pytest.mark.asyncio
    async def test_get_all_users_pagination(self, db_session, multiple_users_data):
        """Test pagination in get_all_users."""
        # Create multiple users
        for user_data in multiple_users_data:
            user_create = UserCreate(**user_data)
            await create_user(db_session, user_create)

        # Test skip and limit
        users_page1 = await get_all_users(db_session, skip=0, limit=2)
        users_page2 = await get_all_users(db_session, skip=2, limit=2)
        
        assert len(users_page1) == 2
        assert len(users_page2) == 1  # Only 3 users total
        
        # Ensure no overlap
        page1_ids = {user.id for user in users_page1}
        page2_ids = {user.id for user in users_page2}
        assert page1_ids.isdisjoint(page2_ids) 


class TestTaskCRUD:
    """Test cases for task CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_task(self, db_session, created_user, sample_task_data):
        """Test creating a task."""
        from app.crud.task import create_task
        from app.schemas.task import TaskCreate
        
        task_data = TaskCreate(**sample_task_data)
        task = await create_task(db_session, created_user.id, task_data)

        assert task.id is not None
        assert task.user_id == created_user.id
        assert task.title == sample_task_data["title"]
        assert task.description == sample_task_data["description"]
        assert task.completed is False

    @pytest.mark.asyncio
    async def test_get_task_exists(self, db_session, created_task):
        """Test getting an existing task by ID."""
        from app.crud.task import get_task
        
        task = await get_task(db_session, created_task.id)
        
        assert task is not None
        assert task.id == created_task.id
        assert task.title == created_task.title

    @pytest.mark.asyncio
    async def test_get_task_not_exists(self, db_session):
        """Test getting a non-existent task by ID."""
        from app.crud.task import get_task
        
        task = await get_task(db_session, 99999)
        assert task is None

    @pytest.mark.asyncio
    async def test_get_tasks_for_user(self, db_session, created_multiple_tasks, created_user):
        """Test getting all tasks for a user."""
        from app.crud.task import get_tasks_for_user
        
        tasks = await get_tasks_for_user(db_session, created_user.id)
        
        assert len(tasks) == 3
        assert all(task.user_id == created_user.id for task in tasks)

    @pytest.mark.asyncio
    async def test_get_tasks_for_user_with_pagination(self, db_session, created_multiple_tasks, created_user):
        """Test getting tasks with pagination."""
        from app.crud.task import get_tasks_for_user
        
        # Get first 2 tasks
        tasks = await get_tasks_for_user(db_session, created_user.id, skip=0, limit=2)
        assert len(tasks) == 2
        
        # Get next task (skip first 2)
        tasks = await get_tasks_for_user(db_session, created_user.id, skip=2, limit=2)
        assert len(tasks) == 1

    @pytest.mark.asyncio
    async def test_get_tasks_for_user_empty(self, db_session, created_user):
        """Test getting tasks for user with no tasks."""
        from app.crud.task import get_tasks_for_user
        
        tasks = await get_tasks_for_user(db_session, created_user.id)
        assert len(tasks) == 0

    @pytest.mark.asyncio
    async def test_update_task(self, db_session, created_task):
        """Test updating a task."""
        from app.crud.task import update_task
        from app.schemas.task import TaskUpdate
        
        update_data = TaskUpdate(
            title="Updated Title",
            description="Updated description",
            completed=True
        )
        
        updated_task = await update_task(db_session, created_task, update_data)
        
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Updated description"
        assert updated_task.completed is True
        assert updated_task.id == created_task.id  # ID should remain the same

    @pytest.mark.asyncio
    async def test_update_task_partial(self, db_session, created_task):
        """Test partially updating a task."""
        from app.crud.task import update_task
        from app.schemas.task import TaskUpdate
        
        original_title = created_task.title
        original_description = created_task.description
        
        # Only update completed status
        update_data = TaskUpdate(completed=True)
        updated_task = await update_task(db_session, created_task, update_data)
        
        assert updated_task.completed is True
        assert updated_task.title == original_title  # Should remain unchanged
        assert updated_task.description == original_description  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_delete_task(self, db_session, created_task):
        """Test deleting a task."""
        from app.crud.task import delete_task, get_task
        
        task_id = created_task.id
        
        # Delete the task
        await delete_task(db_session, created_task)
        
        # Verify it's deleted
        deleted_task = await get_task(db_session, task_id)
        assert deleted_task is None

    @pytest.mark.asyncio
    async def test_create_task_with_null_optional_fields(self, db_session, created_user):
        """Test creating a task with null optional fields."""
        from app.crud.task import create_task
        from app.schemas.task import TaskCreate
        
        task_data = TaskCreate(
            title="Minimal Task",
            description=None,
            due_date=None
        )
        task = await create_task(db_session, created_user.id, task_data)

        assert task.id is not None
        assert task.title == "Minimal Task"
        assert task.description is None
        assert task.due_date is None
        assert task.completed is False

    @pytest.mark.asyncio
    async def test_tasks_isolated_by_user(self, db_session):
        """Test that tasks are properly isolated by user."""
        from app.crud.task import create_task, get_tasks_for_user
        from app.crud.user import create_user
        from app.schemas.task import TaskCreate
        from app.schemas.user import UserCreate
        
        # Create two users
        user1 = await create_user(db_session, UserCreate(email="user1@test.com", password="password"))
        user2 = await create_user(db_session, UserCreate(email="user2@test.com", password="password"))
        
        # Create tasks for each user
        task1 = await create_task(db_session, user1.id, TaskCreate(title="User 1 Task"))
        task2 = await create_task(db_session, user2.id, TaskCreate(title="User 2 Task"))
        
        # Verify isolation
        user1_tasks = await get_tasks_for_user(db_session, user1.id)
        user2_tasks = await get_tasks_for_user(db_session, user2.id)
        
        assert len(user1_tasks) == 1
        assert len(user2_tasks) == 1
        assert user1_tasks[0].title == "User 1 Task"
        assert user2_tasks[0].title == "User 2 Task" 