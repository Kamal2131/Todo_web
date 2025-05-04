const API_BASE = 'http://localhost:8000/api';
// Make sure this is defined at the top of your app.js
// const API_BASE = 'http://localhost:8000/api';  // Include /api prefix
let isEditing = false;
let currentEditId = null;

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    loadTodos();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('todoInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            if (isEditing) updateTodo(currentEditId);
            else addTodo();
        }
    });

    document.getElementById('actionButton').addEventListener('click', () => {
        if (isEditing) updateTodo(currentEditId);
        else addTodo();
    });
}

// app.js
async function addTodo() {
    const input = document.getElementById('todoInput');
    const btn = document.getElementById('actionButton');
    
    if (btn.disabled) return;
    
    const text = input.value.trim();
    if (!text) return;

    btn.disabled = true;
    btn.textContent = 'Adding...';
    
    try {
        const response = await fetch(`${API_BASE}/todos/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ natural_text: text })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            if (response.status === 400 && data.detail.includes('already exists')) {
                showError(`Duplicate todo: ${data.detail}`);
                return;
            }
            throw new Error(data.detail || 'Failed to create todo');
        }
        
        input.value = '';
        await loadTodos();
    } catch (error) {
        showError(error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Add Todo';
    }
}

async function updateTodo(todoId) {
    const input = document.getElementById('todoInput');
    const text = input.value.trim();
    
    try {
        const response = await fetch(`${API_BASE}/todos/${todoId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                natural_text: text // Send as natural language update
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Update failed');
        }

        resetEditState();
        await loadTodos();
    } catch (error) {
        showError(error.message);
    }
}

async function handleDelete(todoId) {
    if (!confirm('Are you sure you want to delete this todo?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/todos/${todoId}`, {
            method: 'DELETE'
        });
        
        handleResponse(response, 'Todo deleted successfully!');
        loadTodos();
    } catch (error) {
        showError(error.message);
    }
}

async function handleEdit(todoId) {
    try {
        const response = await fetch(`${API_BASE}/todos/${todoId}`);
        if (!response.ok) throw new Error('Failed to fetch todo');
        const todo = await response.json();
        
        // Populate input with structured format
        const editText = [
            todo.task,
            todo.description ? `- ${todo.description}` : '',
            `[${todo.category}]`,
            `[${todo.priority}]`,
            todo.due_date ? `[${todo.due_date}]` : ''
        ].filter(Boolean).join(' ');

        document.getElementById('todoInput').value = editText;
        enterEditMode(todo);
    } catch (error) {
        showError(error.message);
    }
}


function enterEditMode(todo) {
    isEditing = true;
    currentEditId = todo.id;
    
    const input = document.getElementById('todoInput');
    const button = document.getElementById('actionButton');
    
    input.value = `${todo.task} [${todo.category}] [${todo.priority}] ${todo.due_date ? `[${todo.due_date}]` : ''}`;
    button.textContent = 'Update Todo';
    input.focus();
}

function resetEditState() {
    isEditing = false;
    currentEditId = null;
    const input = document.getElementById('todoInput');
    const button = document.getElementById('actionButton');
    input.value = '';
    button.textContent = 'Add Todo';
}

async function loadTodos() {
    try {
        const response = await fetch(`${API_BASE}/todos/`);
        const todos = await response.json();
        renderTodos(todos);
    } catch (error) {
        showError('Failed to load todos');
    }
}

function renderTodos(todos) {
    const container = document.getElementById('todoList');
    container.innerHTML = todos.map(todo => `
        <div class="todo-item" data-todo-id="${todo.id}">
            <div class="todo-header">
                <h3 class="todo-title">${todo.task}</h3>
                <span class="priority-badge ${todo.priority}">
                    ${todo.priority.toUpperCase()}
                </span>
            </div>
            
            ${todo.description ? `
                <div class="todo-description">
                    <div class="description-icon">📝</div>
                    <p>${todo.description}</p>
                </div>
            ` : ''}

            <div class="todo-meta">
                <div class="meta-group">
                    <span class="meta-item category ${todo.category}">
                        <span class="meta-icon">🏷️</span>
                        ${todo.category.charAt(0).toUpperCase() + todo.category.slice(1)}
                    </span>
                    
                    ${todo.due_date ? `
                        <span class="meta-item due-date">
                            <span class="meta-icon">📅</span>
                            ${new Date(todo.due_date).toLocaleDateString('en-US', {
                                weekday: 'short', 
                                month: 'short', 
                                day: 'numeric'
                            })}
                        </span>
                    ` : ''}
                </div>
                
                <div class="todo-actions">
                    <button class="icon-btn edit-btn" onclick="handleEdit(${todo.id})" title="Edit">
                        <span class="action-icon">✏️</span>
                    </button>
                    <button class="icon-btn delete-btn" onclick="handleDelete(${todo.id})" title="Delete">
                        <span class="action-icon">🗑️</span>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}


async function handleResponse(response, successMessage) {
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'Request failed');
    }
    showSuccess(successMessage);
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'notification error';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'notification success';
    successDiv.textContent = message;
    document.body.appendChild(successDiv);
    setTimeout(() => successDiv.remove(), 3000);
}

function resetForm() {
    document.getElementById('todoInput').value = '';
}