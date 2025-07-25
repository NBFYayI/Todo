from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead
from app.services.task import list_user_tasks, get_existing_task, make_task, change_task, remove_task
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/", response_model=List[TaskRead])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user= Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tasks = list_user_tasks(db, current_user.id, skip, limit)
    return tasks

@router.post("/", response_model=TaskRead, status_code=201)
def create_new_task(
    task_in: TaskCreate,
    current_user= Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = make_task(db, current_user.id, task_in)
    return task

@router.get("/{task_id}", response_model=TaskRead)
def read_task(
    task_id: int,
    current_user= Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = get_existing_task(db, current_user.id, task_id)
    return task

@router.put("/{task_id}", response_model=TaskRead)
def update_existing_task(
    task_id: int,
    updates: TaskUpdate,
    current_user= Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = change_task(db, current_user.id, task_id, updates)
    return task

@router.delete("/{task_id}", status_code=204)
def delete_existing_task(
    task_id: int,
    current_user= Depends(get_current_user),
    db: Session = Depends(get_db)
):
    remove_task(db, current_user.id, task_id)
    return {"message": "Task deleted successfully"}
