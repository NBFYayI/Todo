from app.crud.task import get_task, get_tasks_for_user, create_task, update_task, delete_task
from sqlalchemy.orm import Session
from app.schemas.task import TaskCreate, TaskUpdate
from fastapi import HTTPException

def list_user_tasks(db: Session, user_id: int, skip: int, limit: int):
    tasks = get_tasks_for_user(db, user_id, skip, limit)
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found")
    return tasks

def get_existing_task(db: Session, user_id: int, task_id: int):
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    return task

def make_task(db: Session, user_id: int, task_in: TaskCreate):
    return create_task(db, user_id, task_in)

def change_task(db: Session, user_id: int, task_id: int, updates: TaskUpdate):
    task = get_existing_task(db, user_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    return update_task(db, task, updates)

def remove_task(db: Session, user_id: int, task_id: int):
    task = get_existing_task(db, user_id, task_id)
    delete_task(db, task)