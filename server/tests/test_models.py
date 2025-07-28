"""
Tests for database models.
"""
import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError

from app.models.user import User


class TestUserModel:
    """Test cases for the User model."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session):
        """Test creating a user with valid data."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password_123"

    @pytest.mark.asyncio
    async def test_user_email_unique_constraint(self, db_session):
        """Test that email must be unique."""
        # Create first user
        user1 = User(
            email="duplicate@example.com",
            hashed_password="password1"
        )
        db_session.add(user1)
        await db_session.commit()

        # Try to create second user with same email
        user2 = User(
            email="duplicate@example.com",
            hashed_password="password2"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_user_email_required(self, db_session):
        """Test that email is required."""
        user = User(hashed_password="password123")
        db_session.add(user)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_user_password_required(self, db_session):
        """Test that hashed_password is required."""
        user = User(email="test@example.com")
        db_session.add(user)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_user_representation(self, db_session):
        """Test user model string representation."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Test that the user object has the expected attributes
        assert hasattr(user, 'id')
        assert hasattr(user, 'email')
        assert hasattr(user, 'hashed_password')
        assert user.email == "test@example.com"


class TestTaskModel:
    """Test cases for the Task model."""

    @pytest.mark.asyncio
    async def test_create_task(self, db_session, created_user):
        """Test creating a task with valid data."""
        from app.models.task import Task
        from datetime import datetime
        
        due_date = datetime.now()
        task = Task(
            user_id=created_user.id,
            title="Test Task",
            description="Test description",
            due_date=due_date,
            completed=False
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        assert task.id is not None
        assert task.user_id == created_user.id
        assert task.title == "Test Task"
        assert task.description == "Test description"
        assert task.due_date == due_date
        assert task.completed is False
        assert task.created_at is not None
        assert task.updated_at is not None

    @pytest.mark.asyncio
    async def test_task_title_required(self, db_session, created_user):
        """Test that title is required."""
        from app.models.task import Task
        
        task = Task(
            user_id=created_user.id,
            description="Test description"
        )
        db_session.add(task)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_task_user_id_required(self, db_session):
        """Test that user_id is required."""
        from app.models.task import Task
        
        task = Task(
            title="Test Task",
            description="Test description"
        )
        db_session.add(task)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_task_optional_fields(self, db_session, created_user):
        """Test that description and due_date are optional."""
        from app.models.task import Task
        
        task = Task(
            user_id=created_user.id,
            title="Minimal Task"
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        assert task.id is not None
        assert task.title == "Minimal Task"
        assert task.description is None
        assert task.due_date is None
        assert task.completed is False  # Should default to False

    @pytest.mark.asyncio
    async def test_task_user_relationship(self, db_session, created_user):
        """Test the relationship between Task and User."""
        from app.models.task import Task
        from app.models.user import User
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        
        task = Task(
            user_id=created_user.id,
            title="Relationship Test",
            description="Testing user relationship"
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        # Test task -> user relationship
        assert task.owner is not None
        assert task.owner.id == created_user.id
        assert task.owner.email == created_user.email

        # Test user -> tasks relationship
        # Need to query with selectinload to properly load the relationship in async context
        result = await db_session.execute(
            select(User).options(selectinload(User.tasks)).where(User.id == created_user.id)
        )
        user_with_tasks = result.scalar_one()
        assert len(user_with_tasks.tasks) == 1
        assert user_with_tasks.tasks[0].id == task.id

    @pytest.mark.asyncio
    async def test_task_completed_default(self, db_session, created_user):
        """Test that completed defaults to False."""
        from app.models.task import Task
        
        task = Task(
            user_id=created_user.id,
            title="Default Completed Test"
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        assert task.completed is False

    @pytest.mark.asyncio
    async def test_task_timestamps(self, db_session, created_user):
        """Test that timestamps are set correctly."""
        from app.models.task import Task
        from datetime import datetime, timezone, timedelta
        
        # Capture current time for comparison
        current_time = datetime.now(timezone.utc)
        
        task = Task(
            user_id=created_user.id,
            title="Timestamp Test"
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)

        assert task.created_at is not None
        assert task.updated_at is not None
                
        created_at = task.created_at
        updated_at = task.updated_at
        
        # If the database timestamps are timezone-naive, assume they're in UTC
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
            
        # Test that timestamps are recent (within 5 seconds of current time)
        # This accounts for potential clock differences between Python and database
        time_tolerance = timedelta(seconds=5)
        assert abs(created_at - current_time) <= time_tolerance
        assert abs(updated_at - current_time) <= time_tolerance
        
        # Test that created_at <= updated_at (should be equal for new records)
        assert created_at <= updated_at 