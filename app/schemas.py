from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional
from fastapi import HTTPException

# Unified TodoCreate schema
class TodoCreate(BaseModel):
    task: str
    description: str | None = None
    category: str
    priority: str
    due_date: date | None = None

    @field_validator('category')
    def validate_category(cls, value):
        valid_categories = ['work', 'personal', 'shopping', 'other']
        if value not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of {valid_categories}")
        return value

    @field_validator('priority')
    def validate_priority(cls, value):
        valid_priorities = ['low', 'medium', 'high']
        if value not in valid_priorities:
            raise ValueError(f"Invalid priority. Must be one of {valid_priorities}")
        return value

class TodoResponse(TodoCreate):
    id: int

    class Config:
        from_attributes = True

# Proper TodoUpdate schema with optional fields
class TodoUpdate(BaseModel):
    task: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    natural_text: Optional[str] = None

    @field_validator('category')
    def validate_category(cls, value):
        if value is not None:
            valid_categories = ['work', 'personal', 'shopping', 'other']
            if value not in valid_categories:
                raise ValueError(f"Invalid category. Must be one of {valid_categories}")
        return value

    @field_validator('priority')
    def validate_priority(cls, value):
        if value is not None:
            valid_priorities = ['low', 'medium', 'high']
            if value not in valid_priorities:
                raise ValueError(f"Invalid priority. Must be one of {valid_priorities}")
        return value

# Add this to your routers/todos.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import Todo

router = APIRouter()

@router.get("/todos/{todo_id}", response_model=TodoResponse)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

