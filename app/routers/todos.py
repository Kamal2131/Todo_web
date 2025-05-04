from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Todo
from ..schemas import TodoCreate, TodoResponse, TodoUpdate
from ..utils.groq_processor import parse_todo, GroqProcessingError

router = APIRouter()

def get_todo_or_404(todo_id: int, db: Session) -> Todo:
    """Retrieve a Todo item by ID or raise 404 error if not found.
    
    Args:
        todo_id: ID of the todo item to retrieve
        db: SQLAlchemy database session
    
    Returns:
        Todo: The requested Todo item
    
    Raises:
        HTTPException: 404 error if todo not found
    """
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

def handle_todo_update(db_todo: Todo, update_data: dict) -> Todo:
    """Process and apply updates to a Todo item.
    
    Args:
        db_todo: The Todo item to update
        update_data: Dictionary of update fields
    
    Returns:
        Todo: The updated Todo item
    
    Raises:
        GroqProcessingError: If natural language parsing fails
    """
    if 'natural_text' in update_data:
        parsed_data = parse_todo(update_data.pop('natural_text')).dict()
        update_data.update(parsed_data)
    
    for key, value in update_data.items():
        if hasattr(db_todo, key):
            setattr(db_todo, key, value)
    return db_todo

@router.post("/todos/", response_model=TodoResponse)
async def create_todo(
    todo_request: dict = Body(...), 
    db: Session = Depends(get_db)
) -> Todo:
    """Create a new Todo item from natural language input.
    
    Args:
        todo_request: Request body containing 'natural_text' field
        db: SQLAlchemy database session
    
    Returns:
        Todo: The newly created Todo item
    
    Raises:
        HTTPException: 400 error if input validation fails
        HTTPException: 400 error if duplicate todo detected
    """
    try:
        if not (natural_text := todo_request.get("natural_text")):
            raise HTTPException(status_code=400, detail="natural_text field required")
        
        todo_data = parse_todo(natural_text)
        db_todo = Todo(**todo_data.dict())
        
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo
        
    except GroqProcessingError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/todos/", response_model=list[TodoResponse])
def read_todos(db: Session = Depends(get_db)) -> list[Todo]:
    """Retrieve all Todo items from the database.
    
    Args:
        db: SQLAlchemy database session
    
    Returns:
        list[Todo]: List of all Todo items
    """
    return db.query(Todo).all()

@router.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)) -> Todo:
    """Get a single Todo item by its ID.
    
    Args:
        todo_id: ID of the todo item to retrieve
        db: SQLAlchemy database session
    
    Returns:
        Todo: The requested Todo item
    """
    return get_todo_or_404(todo_id, db)

@router.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int, 
    todo_update: TodoUpdate, 
    db: Session = Depends(get_db)
) -> Todo:
    """Update an existing Todo item.
    
    Supports both structured field updates and natural language processing.
    
    Args:
        todo_id: ID of the todo item to update
        todo_update: Update data containing fields to modify
        db: SQLAlchemy database session
    
    Returns:
        Todo: The updated Todo item
    
    Raises:
        HTTPException: 400 error if input validation fails
    """
    try:
        db_todo = get_todo_or_404(todo_id, db)
        update_data = todo_update.model_dump(exclude_unset=True)
        
        handle_todo_update(db_todo, update_data)
        db.commit()
        db.refresh(db_todo)
        return db_todo
        
    except GroqProcessingError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)) -> dict:
    """Delete a Todo item by its ID.
    
    Args:
        todo_id: ID of the todo item to delete
        db: SQLAlchemy database session
    
    Returns:
        dict: Success message
    
    Example Response:
        {"message": "Todo deleted successfully"}
    """
    db_todo = get_todo_or_404(todo_id, db)
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}