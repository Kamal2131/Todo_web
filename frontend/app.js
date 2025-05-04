const API_BASE = 'http://localhost:8000/api';
let isEditing = false, currentEditId = null;

// Helpers
const apiRequest = async (endpoint, method, body) => {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: body && JSON.stringify(body)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Request failed');
    return data;
};

const showNotification = (type, message) => {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), type === 'error' ? 5000 : 3000);
};

// Core Functions
const toggleButtonState = (isLoading) => {
    const btn = document.getElementById('actionButton');
    btn.disabled = isLoading;
    btn.textContent = isLoading ? (isEditing ? 'Updating...' : 'Adding...') : (isEditing ? 'Update Todo' : 'Add Todo');
};

const handleTodoAction = async (action) => {
    const input = document.getElementById('todoInput');
    const text = input.value.trim();
    if (!text) return;

    toggleButtonState(true);
    try {
        if (action === 'add') {
            await apiRequest('/todos/', 'POST', { natural_text: text });
        } else {
            await apiRequest(`/todos/${currentEditId}`, 'PUT', { natural_text: text });
        }
        input.value = '';
        await loadTodos();
    } catch (error) {
        showNotification('error', error.message);
    } finally {
        toggleButtonState(false);
    }
};

// Event Handlers
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('actionButton').addEventListener('click', () => 
        isEditing ? handleTodoAction('update') : handleTodoAction('add'));
    document.getElementById('todoInput').addEventListener('keypress', (e) => 
        e.key === 'Enter' && (isEditing ? handleTodoAction('update') : handleTodoAction('add')));
    loadTodos();
});

const handleEdit = async (todoId) => {
    try {
        const todo = await apiRequest(`/todos/${todoId}`, 'GET');
        const editText = [todo.task, todo.description && `- ${todo.description}`, 
                        `[${todo.category}]`, `[${todo.priority}]`, todo.due_date && `[${todo.due_date}]`]
                        .filter(Boolean).join(' ');
        document.getElementById('todoInput').value = editText;
        isEditing = true;
        currentEditId = todo.id;
    } catch (error) {
        showNotification('error', error.message);
    }
};

const handleDelete = async (todoId) => {
    if (confirm('Delete this todo?')) {
        try {
            await apiRequest(`/todos/${todoId}`, 'DELETE');
            await loadTodos();
        } catch (error) {
            showNotification('error', error.message);
        }
    }
};

// Rendering
function renderTodos(todos) {
    const container = document.getElementById('todoList');
    container.innerHTML = todos.map(todo => `
        <div class="todo-item">
            <div class="todo-header">
                <h3 class="todo-title">${todo.task}</h3>
                <span class="priority ${todo.priority}">
                    ${todo.priority.toUpperCase()}
                </span>
            </div>
            
            ${todo.description ? `
                <div class="todo-description">
                    ${todo.description}
                </div>
            ` : ''}

            <div class="todo-meta">
                <div class="meta-group">
                    <span class="category ${todo.category}">
                        ${todo.category.charAt(0).toUpperCase() + todo.category.slice(1)}
                    </span>
                    ${todo.due_date ? `
                        <span class="due-date">
                            📅 ${new Date(todo.due_date).toLocaleDateString('en-US', {
                                weekday: 'short', 
                                month: 'short', 
                                day: 'numeric'
                            })}
                        </span>
                    ` : ''}
                </div>
                <div class="todo-actions">
                    <button class="edit-btn" onclick="handleEdit(${todo.id})">Edit</button>
                    <button class="delete-btn" onclick="handleDelete(${todo.id})">Delete</button>
                </div>
            </div>
        </div>
    `).join('');
}

const loadTodos = async () => {
    try {
        const todos = await apiRequest('/todos/', 'GET');
        renderTodos(todos);
    } catch (error) {
        showNotification('error', 'Failed to load todos');
    }
};