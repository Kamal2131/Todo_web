from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional
from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import Todo

router = APIRouter()

class TodoCreate(BaseModel):
    """Pydantic model for creating a new TODO item.
    
    Attributes:
        task (str): Main task description (required)
        description (str | None): Additional details about the task
        category (str): Task category from predefined options
        priority (str): Priority level from predefined options
        due_date (date | None): Optional target completion date
    """
    task: str
    description: str | None = None
    category: str
    priority: str
    due_date: date | None = None

    @field_validator('category')
    def validate_category(cls, value):
        """Validate that category is one of: work, personal, shopping, other"""
        valid_categories = ['work', 'personal', 'shopping', 'other']
        if value not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of {valid_categories}")
        return value

    @field_validator('priority')
    def validate_priority(cls, value):
        """Validate that priority is one of: low, medium, high"""
        valid_priorities = ['low', 'medium', 'high']
        if value not in valid_priorities:
            raise ValueError(f"Invalid priority. Must be one of {valid_priorities}")
        return value

class TodoResponse(TodoCreate):
    """Response model for TODO items including database ID"""
    id: int

    class Config:
        """Enable ORM mode for SQLAlchemy compatibility"""
        from_attributes = True

class TodoUpdate(BaseModel):
    """Pydantic model for updating TODO items with optional fields
    
    Attributes:
        natural_text (str | None): Optional field for natural language processing
    """
    task: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    natural_text: Optional[str] = None

    @field_validator('category')
    def validate_category(cls, value):
        """Validate category if provided (same options as TodoCreate)"""
        if value is not None:
            valid_categories = ['work', 'personal', 'shopping', 'other']
            if value not in valid_categories:
                raise ValueError(f"Invalid category. Must be one of {valid_categories}")
        return value

    @field_validator('priority')
    def validate_priority(cls, value):
        """Validate priority if provided (same options as TodoCreate)"""
        if value is not None:
            valid_priorities = ['low', 'medium', 'high']
            if value not in valid_priorities:
                raise ValueError(f"Invalid priority. Must be one of {valid_priorities}")
        return value

@router.get("/todos/{todo_id}", response_model=TodoResponse)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific TODO item by its ID
    
    Args:
        todo_id (int): ID of the TODO item to retrieve
        db (Session): Database session dependency
        
    Returns:
        TodoResponse: The requested TODO item
        
    Raises:
        HTTPException: 404 if TODO item is not found
    """
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo