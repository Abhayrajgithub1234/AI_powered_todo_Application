// AI To-Do App JavaScript
let currentTasks = [];
let currentFilter = 'all';

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadTasks();
    
    // Add event listeners
    document.getElementById('quickAddForm').addEventListener('submit', handleQuickAdd);
    document.getElementById('chatInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
});

function initializeApp() {
    console.log('AI To-Do App initialized');
    
    // Add welcome message to chat
    addChatMessage('AI', 'Hello! I\'m your AI assistant. I can help you manage your tasks using natural language! Try commands like:\n\n• "Create a new task: Buy groceries"\n• "Add task: Call dentist with high priority"\n• "Mark shopping as completed"\n• "Delete task about meeting"\n\nI can also provide productivity insights and chat about your goals. How can I help you today?', true);
}

async function loadTasks() {
    try {
        const response = await fetch('/api/todos');
        const tasks = await response.json();
        currentTasks = tasks;
        renderTasks(tasks);
        updateStats();
    } catch (error) {
        console.error('Error loading tasks:', error);
        showNotification('Error loading tasks', 'error');
    }
}

function renderTasks(tasks) {
    const tasksList = document.getElementById('tasksList');
    
    if (!tasks || tasks.length === 0) {
        tasksList.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No tasks found</h5>
                <p class="text-muted">Add your first task above or ask the AI assistant for suggestions.</p>
            </div>
        `;
        return;
    }

    tasksList.innerHTML = tasks.map(task => `
        <div class="task-item mb-3 p-3 border rounded ${task.status === 'completed' ? 'completed' : ''}" data-task-id="${task.id}">
            <div class="row align-items-center">
                <div class="col-md-1">
                    <div class="form-check">
                        <input class="form-check-input task-checkbox" type="checkbox" 
                               ${task.status === 'completed' ? 'checked' : ''}
                               onchange="toggleTaskStatus(${task.id}, this.checked)">
                    </div>
                </div>
                <div class="col-md-5">
                    <h6 class="task-title ${task.status === 'completed' ? 'text-decoration-line-through text-muted' : ''}">
                        ${escapeHtml(task.title)}
                    </h6>
                    ${task.description ? `<p class="task-description text-muted small mb-0">${escapeHtml(task.description)}</p>` : ''}
                </div>
                <div class="col-md-2">
                    <span class="badge priority-${task.priority}">
                        ${task.priority.charAt(0).toUpperCase() + task.priority.slice(1)} Priority
                    </span>
                </div>
                <div class="col-md-2">
                    ${task.due_date ? `<small class="text-muted"><i class="fas fa-calendar"></i> ${task.due_date}</small>` : ''}
                </div>
                <div class="col-md-2">
                    <div class="btn-group" role="group">
                        <button type="button" class="btn btn-sm btn-outline-primary" 
                                onclick="editTask(${task.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-danger" 
                                onclick="deleteTask(${task.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function updateStats() {
    const totalTasks = currentTasks.length;
    const completedTasks = currentTasks.filter(t => t.status === 'completed').length;
    const pendingTasks = totalTasks - completedTasks;
    const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    
    console.log(`Stats: Total: ${totalTasks}, Completed: ${completedTasks}, Rate: ${completionRate}%`);
    
    // Update stats cards with more specific selectors
    const statElements = document.querySelectorAll('.h5.mb-0.font-weight-bold');
    if (statElements.length >= 4) {
        statElements[0].textContent = totalTasks;
        statElements[1].textContent = completedTasks;
        statElements[2].textContent = pendingTasks;
        statElements[3].textContent = completionRate + '%';
    }
    
    // Update progress bar
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        progressBar.style.width = completionRate + '%';
        progressBar.textContent = completionRate + '% Complete';
    }
    
    // Also update the progress bar in the progress section
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        bar.style.width = completionRate + '%';
        if (bar.textContent.includes('%') || bar.textContent.includes('Complete')) {
            bar.textContent = completionRate + '% Complete';
        }
    });
}

// Force refresh stats from server
async function forceRefreshStats() {
    try {
        const response = await fetch('/api/todos');
        const tasks = await response.json();
        
        const totalTasks = tasks.length;
        const completedTasks = tasks.filter(t => t.status === 'completed').length;
        const pendingTasks = totalTasks - completedTasks;
        const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
        
        console.log('Force refresh stats:', { totalTasks, completedTasks, pendingTasks, completionRate });
        
        // Update the global currentTasks and call updateStats
        currentTasks = tasks;
        updateStats();
        
        return { totalTasks, completedTasks, pendingTasks, completionRate };
    } catch (error) {
        console.error('Error force refreshing stats:', error);
    }
}

async function handleQuickAdd(e) {
    e.preventDefault();
    
    const title = document.getElementById('quickTaskTitle').value.trim();
    const priority = document.getElementById('quickTaskPriority').value;
    const dueDate = document.getElementById('quickTaskDue').value;
    
    if (!title) {
        showNotification('Please enter a task title', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/todos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                priority: priority,
                due_date: dueDate || null
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('quickAddForm').reset();
            showNotification('Task added successfully!', 'success');
            loadTasks();
        } else {
            showNotification('Error adding task', 'error');
        }
    } catch (error) {
        console.error('Error adding task:', error);
        showNotification('Error adding task', 'error');
    }
}

async function toggleTaskStatus(taskId, isCompleted) {
    const task = currentTasks.find(t => t.id === taskId);
    if (!task) return;
    
    const newStatus = isCompleted ? 'completed' : 'pending';
    
    try {
        const response = await fetch(`/api/todos/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...task,
                status: newStatus
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(isCompleted ? 'Task completed!' : 'Task reopened!', 'success');
            loadTasks();
        } else {
            showNotification('Error updating task', 'error');
        }
    } catch (error) {
        console.error('Error updating task:', error);
        showNotification('Error updating task', 'error');
    }
}

function editTask(taskId) {
    const task = currentTasks.find(t => t.id === taskId);
    if (!task) return;
    
    // Populate the edit modal
    document.getElementById('editTaskId').value = task.id;
    document.getElementById('editTaskTitle').value = task.title;
    document.getElementById('editTaskDescription').value = task.description || '';
    document.getElementById('editTaskPriority').value = task.priority;
    document.getElementById('editTaskDue').value = task.due_date || '';
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('editTaskModal'));
    modal.show();
}

async function saveTaskEdit() {
    const taskId = document.getElementById('editTaskId').value;
    const title = document.getElementById('editTaskTitle').value.trim();
    const description = document.getElementById('editTaskDescription').value.trim();
    const priority = document.getElementById('editTaskPriority').value;
    const dueDate = document.getElementById('editTaskDue').value;
    
    if (!title) {
        showNotification('Please enter a task title', 'warning');
        return;
    }
    
    const task = currentTasks.find(t => t.id == taskId);
    if (!task) return;
    
    try {
        const response = await fetch(`/api/todos/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                description: description,
                priority: priority,
                status: task.status,
                due_date: dueDate || null
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Task updated successfully!', 'success');
            loadTasks();
            
            // Hide the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editTaskModal'));
            modal.hide();
        } else {
            showNotification('Error updating task', 'error');
        }
    } catch (error) {
        console.error('Error updating task:', error);
        showNotification('Error updating task', 'error');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/todos/${taskId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Task deleted successfully!', 'success');
            loadTasks();
        } else {
            showNotification('Error deleting task', 'error');
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showNotification('Error deleting task', 'error');
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage('You', message, false);
    input.value = '';
    
    // Show loading
    addChatMessage('AI', 'Thinking...', true, true);
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        const result = await response.json();
        
        // Remove loading message
        removeLoadingMessage();
        
        if (result.success) {
            addChatMessage('AI', result.response, true);
            
            // If an action was performed, refresh the task list
            if (result.action_performed) {
                setTimeout(() => {
                    loadTasks();
                    updateStats();
                }, 500); // Small delay to ensure UI updates smoothly
                
                // Add action feedback
                if (result.action_type === 'create_task') {
                    showNotification('New task created via AI!', 'success');
                } else if (result.action_type === 'complete_task') {
                    showNotification('Task marked as completed via AI!', 'success');
                } else if (result.action_type === 'delete_task') {
                    showNotification('Task deleted via AI!', 'success');
                }
            }
        } else {
            addChatMessage('AI', 'Sorry, I encountered an error. Please try again.', true);
        }
    } catch (error) {
        console.error('Error sending chat message:', error);
        removeLoadingMessage();
        addChatMessage('AI', 'Sorry, I\'m having trouble connecting right now. Please try again.', true);
    }
}

async function getAIInsights() {
    addChatMessage('AI', 'Let me analyze your tasks and provide some insights...', true, true);
    
    try {
        const response = await fetch('/api/productivity-insights');
        const result = await response.json();
        
        removeLoadingMessage();
        
        if (result.success) {
            addChatMessage('AI', result.insights, true);
        } else {
            addChatMessage('AI', 'Sorry, I couldn\'t generate insights right now. Please try again.', true);
        }
    } catch (error) {
        console.error('Error getting AI insights:', error);
        removeLoadingMessage();
        addChatMessage('AI', 'Sorry, I\'m having trouble analyzing your tasks right now.', true);
    }
}

async function askForSuggestions() {
    const userInput = prompt('What would you like help with? (e.g., "I need to organize my work week" or "I want to be more productive")');
    
    if (!userInput) return;
    
    addChatMessage('You', `Can you suggest some tasks for: ${userInput}`, false);
    addChatMessage('AI', 'Let me suggest some tasks for you...', true, true);
    
    try {
        const response = await fetch('/api/ai-suggestions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                input: userInput
            })
        });
        
        const result = await response.json();
        
        removeLoadingMessage();
        
        if (result.success && result.suggestions) {
            let suggestionText = 'Here are some task suggestions:\n\n';
            result.suggestions.forEach((suggestion, index) => {
                suggestionText += `${index + 1}. ${suggestion.task} (${suggestion.priority} priority)\n`;
            });
            suggestionText += '\nWould you like me to add any of these tasks to your list?';
            
            addChatMessage('AI', suggestionText, true);
        } else {
            addChatMessage('AI', 'Here are some general suggestions:\n\n1. Break down large tasks into smaller steps\n2. Set specific deadlines for your goals\n3. Prioritize tasks based on urgency and importance\n4. Review and adjust your task list regularly', true);
        }
    } catch (error) {
        console.error('Error getting AI suggestions:', error);
        removeLoadingMessage();
        addChatMessage('AI', 'Sorry, I couldn\'t generate suggestions right now. Please try again.', true);
    }
}

function addChatMessage(sender, message, isAI, isLoading = false) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = isAI ? 'ai-message' : 'user-message';
    
    if (isLoading) {
        messageDiv.classList.add('loading-message');
        messageDiv.innerHTML = `<strong>${sender}:</strong> <i class="fas fa-spinner fa-spin"></i> ${message}`;
    } else {
        messageDiv.innerHTML = `<strong>${sender}:</strong> ${escapeHtml(message).replace(/\n/g, '<br>')}`;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeLoadingMessage() {
    const loadingMessage = document.querySelector('.loading-message');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

function filterTasks(filter) {
    currentFilter = filter;
    let filteredTasks = currentTasks;
    
    switch(filter) {
        case 'pending':
            filteredTasks = currentTasks.filter(t => t.status === 'pending');
            break;
        case 'completed':
            filteredTasks = currentTasks.filter(t => t.status === 'completed');
            break;
        case 'high':
            filteredTasks = currentTasks.filter(t => t.priority === 'high');
            break;
        case 'all':
        default:
            filteredTasks = currentTasks;
            break;
    }
    
    renderTasks(filteredTasks);
}

function refreshData() {
    showNotification('Refreshing data...', 'info');
    loadTasks();
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification && notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to add task quickly
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const quickTaskInput = document.getElementById('quickTaskTitle');
        if (quickTaskInput && quickTaskInput.value.trim()) {
            document.getElementById('quickAddForm').dispatchEvent(new Event('submit'));
        }
    }
    
    // Escape to clear chat input
    if (e.key === 'Escape') {
        const chatInput = document.getElementById('chatInput');
        if (chatInput && document.activeElement === chatInput) {
            chatInput.value = '';
            chatInput.blur();
        }
    }
});
