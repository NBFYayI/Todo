from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead
from app.services.task import list_user_tasks, get_existing_task, make_task, change_task, remove_task
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/", response_model=List[TaskRead])
async def read_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user= Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tasks = await list_user_tasks(db, current_user.id, skip, limit)
    return tasks

@router.post("/", response_model=TaskRead, status_code=201)
async def create_new_task(
    task_in: TaskCreate,
    current_user= Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    task = await make_task(db, current_user.id, task_in)
    return task

@router.get("/{task_id}", response_model=TaskRead)
async def read_task(
    task_id: int,
    current_user= Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    task = await get_existing_task(db, current_user.id, task_id)
    return task

@router.put("/{task_id}", response_model=TaskRead)
async def update_existing_task(
    task_id: int,
    updates: TaskUpdate,
    current_user= Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    task = await change_task(db, current_user.id, task_id, updates)
    return task

@router.delete("/{task_id}", status_code=204)
async def delete_existing_task(
    task_id: int,
    current_user= Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await remove_task(db, current_user.id, task_id)
    return {"message": "Task deleted successfully"}
