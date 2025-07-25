from pydantic import BaseModel
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    
class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    completed: bool | None = None

class TaskRead(TaskBase):
    id: int
    user_id: int
    completed: bool
    updated_at: datetime

    class Config:
        orm_mode = True
