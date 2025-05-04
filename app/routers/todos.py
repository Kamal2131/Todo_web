from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Todo
# Change this import in your routers/todos.py
from ..schemas import TodoCreate, TodoResponse, TodoUpdate  # Add TodoUpdate
from ..utils.groq_processor import parse_todo, GroqProcessingError

router = APIRouter()

@router.post("/todos/", response_model=TodoResponse)
async def create_todo(
    todo_request: dict = Body(...),
    db: Session = Depends(get_db)
):
    try:
        natural_text = todo_request.get("natural_text")
        if not natural_text:
            raise HTTPException(status_code=400, detail="natural_text field required")

        # Parse first to get structured data
        todo_data = parse_todo(natural_text)
        
        # Check for existing todo with same details
        existing = db.query(Todo).filter(
            Todo.task == todo_data.task,
            Todo.due_date == todo_data.due_date
        ).first()
        
        # if existing:
        #     raise HTTPException(
        #         status_code=400,
        #         detail=f"Similar todo already exists (ID: {existing.id})"
        #     )

        db_todo = Todo(**todo_data.dict())
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo
        
    except GroqProcessingError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/todos/", response_model=list[TodoResponse])
def read_todos(db: Session = Depends(get_db)):
    return db.query(Todo).all()

# In your routers/todos.py
@router.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(
    todo_id: int, 
    db: Session = Depends(get_db)
):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return db_todo

# app/routers/todos.py
# @router.put("/todos/{todo_id}", response_model=TodoResponse)
# def update_todo(
#     todo_id: int,
#     todo_update: TodoCreate,
#     db: Session = Depends(get_db)
# ):
#     db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
#     if not db_todo:
#         raise HTTPException(status_code=404, detail="Todo not found")
    
#     for key, value in todo_update.dict().items():
#         setattr(db_todo, key, value)
    
#     db.commit()
#     db.refresh(db_todo)
#     return db_todo
@router.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Session = Depends(get_db)
):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    try:
        update_data = todo_update.model_dump(exclude_unset=True)
        
        # Handle natural language updates
        if 'natural_text' in update_data:
            parsed_data = parse_todo(update_data.pop('natural_text'))
            update_data.update(parsed_data.dict())

        # Validate and update
        for key, value in update_data.items():
            if hasattr(db_todo, key):
                setattr(db_todo, key, value)
        
        db.commit()
        db.refresh(db_todo)
        return db_todo

    except GroqProcessingError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
      
@router.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}