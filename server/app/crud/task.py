from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import Task
from app.database import get_db
from sqlalchemy.orm import Session

def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def get_tasks_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Task).filter(Task.user_id == user_id).offset(skip).limit(limit).all()

def create_task(db: Session, user_id: int, task_in:TaskCreate):
    db_task = Task(**task_in.model_dump(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task:Task, updates: TaskUpdate):
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task:Task):
    db.delete(task)
    db.commit()