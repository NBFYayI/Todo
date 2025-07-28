from app.crud.task import get_task, get_tasks_for_user, create_task, update_task, delete_task
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.task import TaskCreate, TaskUpdate
from fastapi import HTTPException

async def list_user_tasks(db: AsyncSession, user_id: int, skip: int, limit: int):
    tasks = await get_tasks_for_user(db, user_id, skip, limit)
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found")
    return tasks

async def get_existing_task(db: AsyncSession, user_id: int, task_id: int):
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    return task

async def make_task(db: AsyncSession, user_id: int, task_in: TaskCreate):
    return await create_task(db, user_id, task_in)

async def change_task(db: AsyncSession, user_id: int, task_id: int, updates: TaskUpdate):
    task = await get_existing_task(db, user_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    return await update_task(db, task, updates)

async def remove_task(db: AsyncSession, user_id: int, task_id: int):
    task = await get_existing_task(db, user_id, task_id)
    await delete_task(db, task)