"""
Main FastAPI application configuration and setup.
Handles database initialization, CORS, routing, and static file serving.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .database import engine
from .models import Base
from .routers import todos

""" initialize database tables """
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Todo Manager",
    description="API backend for AI-enhanced todo management system",
    version="1.0.0"
)

""" Static Files Configuration """
app.mount(
    "/static", 
    StaticFiles(directory="frontend"), 
    name="static"
)
"""Mount static files directory to serve frontend assets
- Serves files from '/frontend' directory at '/static' path
- Accessible via URLs like '/static/js/app.js'
"""

# CORS Security Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permissive setting for development
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]  # Expose all headers
)
"""Cross-Origin Resource Sharing (CORS) middleware configuration
Warning: These settings are permissive for development purposes.
For production, restrict origins, methods, and headers.
"""

# API Routing Configuration
app.include_router(
    todos.router,
    prefix="/api",
    tags=["todos"]
)
"""Register todo-related API endpoints
- Routes prefixed with '/api'
- Grouped under 'todos' tag in documentation
"""

@app.get("/", include_in_schema=False)
async def serve_frontend() -> FileResponse:
    """Serve the frontend application's main entry point
    
    Returns:
        FileResponse: HTML file for the frontend interface
    
    Notes:
        - Excluded from OpenAPI schema documentation
        - Serves 'frontend/index.html' for root path requests
    """
    return FileResponse("frontend/index.html")