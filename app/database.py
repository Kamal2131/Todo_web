from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

""" Database engine instance - maintains a pool of connections to the SQLite database"""
engine = create_engine(
    "sqlite:///./todos.db",
    connect_args={"check_same_thread": False}  # Required for SQLite thread safety
)

""" Session factory - generates new database sessions """
SessionLocal = sessionmaker(
    autocommit=False,  # Disable automatic commit behavior
    autoflush=False,   # Disable automatic flush behavior
    bind=engine        # Bind to the database engine
)

""" Base class for declarative model definitions """
Base = declarative_base()

def get_db():
    """Dependency that provides a database session and ensures proper cleanup.
    
    Yields:
        Session: A SQLAlchemy database session instance
    
    Usage:
        FastAPI will use this to manage database sessions for request lifecycle
        Example: router function parameter `db: Session = Depends(get_db)`
    
    Note:
        Always uses the session in a context manager or dependency to ensure
        proper closing of connections even if exceptions occur.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()