from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_task(db: AsyncSession, task_id: int):
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()

async def get_tasks_for_user(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def create_task(db: AsyncSession, user_id: int, task_in: TaskCreate):
    db_task = Task(**task_in.model_dump(), user_id=user_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def update_task(db: AsyncSession, task: Task, updates: TaskUpdate):
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task

async def delete_task(db: AsyncSession, task: Task):
    await db.delete(task)
    await db.commit()