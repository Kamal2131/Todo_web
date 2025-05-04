from sqlalchemy import Column, Integer, String, Date
from .database import Base

class Todo(Base):
    """Represents a TODO item in the database.
    
    Inherits from SQLAlchemy's Base class to define database model structure.
    
    Attributes:
        id (int): Primary key identifier for the TODO item.
        task (str): The main task description (required).
        description (str, optional): Additional details about the task. Can be null.
        category (str): Classification of the task (default: 'general').
        priority (str): Importance level of the task (default: 'medium').
        due_date (date, optional): Target completion date. Can be null.
        
    Table Configuration:
        __tablename__ (str): Name of the database table ('todos').
    """
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String)
    description = Column(String, nullable=True)
    category = Column(String, default="general")
    priority = Column(String, default="medium")
    due_date = Column(Date, nullable=True)