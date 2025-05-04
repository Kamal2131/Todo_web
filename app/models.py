from sqlalchemy import Column, Integer, String, Date
from .database import Base

class Todo(Base):
    """Database model for TODO items"""
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String)
    description = Column(String, nullable=True)  # New field
    category = Column(String, default="general")
    priority = Column(String, default="medium")
    due_date = Column(Date, nullable=True)