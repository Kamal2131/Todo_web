# FastAPI ToDo Application

A modern, high-performance web application for managing your tasks, built with FastAPI, SQLAlchemy, and SQLite.

---

## 🚀 Features
- **FastAPI**: High-performance web framework for building APIs
- **SQLAlchemy**: ORM for database interactions
- **SQLite**: Lightweight database for development and testing
- **Pydantic**: Data validation and settings management using Python type annotations
- **Modular Architecture**: Clean separation of concerns for scalability

---

## 📁 Project Structure
```
fastapi-todo/
├── app/
│   ├── __init__.py
│   ├── main.py          # Application entry point
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # Database session and engine
│   └── routers/
│       └── todos.py     # API route definitions
├── requirements.txt     # Project dependencies
├── todos.db             # SQLite database file
└── README.md            # Project documentation
```

---

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Kamal2131/Todo_web.git
   cd Todo_web
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🧪 Running the Application

1. **Navigate to the app directory:**
   ```bash
   cd app
   ```
2. **Start the FastAPI server:**
   ```bash
   uvicorn main:app --reload
   ```
3. **Access the API documentation:**
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📬 API Endpoints
- `GET /todos/` : Retrieve all ToDo items
- `GET /todos/{id}` : Retrieve a specific ToDo item by ID
- `POST /todos/` : Create a new ToDo item
- `PUT /todos/{id}` : Update an existing ToDo item
- `DELETE /todos/{id}` : Delete a ToDo item

Detailed request and response schemas are available in the Swagger UI.

---

## 🛠️ Technologies Used
- Python 3.9+
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

---

## 🧱 System Architecture
The application follows a modular architecture:
- **API Layer**: Handles HTTP requests and routes them to appropriate handlers
- **Schema Layer**: Defines data models for validation and serialization
- **CRUD Layer**: Implements business logic and database interactions
- **Database Layer**: Manages database connections and sessions

---