from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
import google.generativeai as genai
from datetime import datetime
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Database initialization
def init_db():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date DATE,
            completed_at TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('todos.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    conn = get_db_connection()
    todos = conn.execute('SELECT * FROM todos ORDER BY created_at DESC').fetchall()
    
    # Calculate statistics
    total_tasks = len(todos)
    completed_tasks = len([t for t in todos if t['status'] == 'completed'])
    pending_tasks = total_tasks - completed_tasks
    
    # Priority distribution
    high_priority = len([t for t in todos if t['priority'] == 'high'])
    medium_priority = len([t for t in todos if t['priority'] == 'medium'])
    low_priority = len([t for t in todos if t['priority'] == 'low'])
    
    conn.close()
    
    stats = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority
    }
    
    return render_template('dashboard.html', todos=todos, stats=stats)

@app.route('/api/todos', methods=['GET'])
def get_todos():
    conn = get_db_connection()
    todos = conn.execute('SELECT * FROM todos ORDER BY created_at DESC').fetchall()
    conn.close()
    
    return jsonify([dict(todo) for todo in todos])

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO todos (title, description, priority, due_date)
        VALUES (?, ?, ?, ?)
    ''', (data['title'], data.get('description', ''), data.get('priority', 'medium'), data.get('due_date')))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Todo created successfully'})

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    
    conn = get_db_connection()
    
    # If marking as completed, add completion timestamp
    if data.get('status') == 'completed':
        conn.execute('''
            UPDATE todos 
            SET title=?, description=?, priority=?, status=?, due_date=?, 
                completed_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (data['title'], data.get('description', ''), data['priority'], 
              data['status'], data.get('due_date'), todo_id))
    else:
        conn.execute('''
            UPDATE todos 
            SET title=?, description=?, priority=?, status=?, due_date=?, 
                completed_at=NULL, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (data['title'], data.get('description', ''), data['priority'], 
              data['status'], data.get('due_date'), todo_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Todo updated successfully'})

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM todos WHERE id=?', (todo_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Todo deleted successfully'})

def process_task_command(user_message, todos, conn):
    """Process natural language commands for task management"""
    message_lower = user_message.lower().strip()
    
    # Create task commands
    create_patterns = [
        r'create (?:a )?(?:new )?task:?\s*(.+)',
        r'add (?:a )?(?:new )?task:?\s*(.+)',
        r'new task:?\s*(.+)',
        r'make (?:a )?(?:new )?task:?\s*(.+)',
        r'i need to\s+(.+)',
        r'add:?\s*(.+)',
        r'create:?\s*(.+)',
    ]
    
    for pattern in create_patterns:
        match = re.search(pattern, message_lower)
        if match:
            task_description = match.group(1).strip()
            
            # Extract priority if mentioned
            priority = 'medium'  # default
            if any(word in task_description for word in ['high priority', 'urgent', 'important', 'critical']):
                priority = 'high'
                task_description = re.sub(r'\s*(?:with\s+)?(?:high\s+priority|urgent|important|critical)\s*', ' ', task_description).strip()
            elif any(word in task_description for word in ['low priority', 'minor']):
                priority = 'low'
                task_description = re.sub(r'\s*(?:with\s+)?(?:low\s+priority|minor)\s*', ' ', task_description).strip()
            elif 'medium priority' in task_description:
                task_description = re.sub(r'\s*(?:with\s+)?medium\s+priority\s*', ' ', task_description).strip()
            
            # Clean up the task description
            task_description = re.sub(r'\s+', ' ', task_description).strip()
            
            if task_description and len(task_description) > 2:
                # Create the task
                conn.execute('''
                    INSERT INTO todos (title, description, priority, due_date)
                    VALUES (?, ?, ?, ?)
                ''', (task_description, '', priority, None))
                
                return {
                    'message': f'✅ Created new task: "{task_description}" with {priority} priority!',
                    'action_type': 'create_task'
                }
    
    # Complete/Mark as done commands
    complete_patterns = [
        r'(?:mark|set)\s+(?:the\s+)?task\s+(?:about\s+|titled\s+|called\s+)?["\']?([^"\']+)["\']?\s+as\s+(?:completed|done|finished)',
        r'complete\s+(?:the\s+)?task\s+(?:about\s+|titled\s+|called\s+)?["\']?([^"\']+)["\']?',
        r'(?:mark|set)\s+["\']?([^"\']+)["\']?\s+as\s+(?:completed|done|finished)',
        r'finish\s+(?:the\s+)?task\s+(?:about\s+|titled\s+|called\s+)?["\']?([^"\']+)["\']?',
        r'done\s+with\s+["\']?([^"\']+)["\']?',
        r'completed?\s+["\']?([^"\']+)["\']?',
        r'["\']?([^"\']+)["\']?\s+is\s+(?:completed|done|finished)',
    ]
    
    for pattern in complete_patterns:
        match = re.search(pattern, message_lower)
        if match:
            task_search = match.group(1).strip()
            
            # Find matching task
            matching_task = None
            best_score = 0
            
            for todo in todos:
                if todo['status'] == 'completed':
                    continue  # Skip already completed tasks
                    
                # Calculate match score
                title_lower = todo['title'].lower()
                desc_lower = (todo['description'] or '').lower()
                
                if task_search in title_lower or task_search in desc_lower:
                    # Exact substring match gets highest score
                    score = len(task_search) / max(len(title_lower), 1)
                    if score > best_score:
                        best_score = score
                        matching_task = todo
                elif any(word in title_lower for word in task_search.split()):
                    # Word match gets lower score
                    words_matched = sum(1 for word in task_search.split() if word in title_lower)
                    score = words_matched / len(task_search.split()) * 0.7
                    if score > best_score:
                        best_score = score
                        matching_task = todo
            
            if matching_task and best_score > 0.3:
                # Mark as completed
                conn.execute('''
                    UPDATE todos 
                    SET status=?, completed_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                ''', ('completed', matching_task['id']))
                
                return {
                    'message': f'✅ Marked task "{matching_task["title"]}" as completed!',
                    'action_type': 'complete_task'
                }
            else:
                return {
                    'message': f'❌ Could not find a task matching "{task_search}". Please be more specific or check your task list.',
                    'action_type': 'task_not_found'
                }
    
    # Delete task commands
    delete_patterns = [
        r'delete\s+(?:the\s+)?task\s+(?:about\s+|titled\s+|called\s+)?["\']?([^"\']+)["\']?',
        r'remove\s+(?:the\s+)?task\s+(?:about\s+|titled\s+|called\s+)?["\']?([^"\']+)["\']?',
        r'get\s+rid\s+of\s+(?:the\s+)?task\s+(?:about\s+|titled\s+|called\s+)?["\']?([^"\']+)["\']?',
    ]
    
    for pattern in delete_patterns:
        match = re.search(pattern, message_lower)
        if match:
            task_search = match.group(1).strip()
            
            # Find matching task
            matching_task = None
            for todo in todos:
                if (task_search.lower() in todo['title'].lower() or 
                    (todo['description'] and task_search.lower() in todo['description'].lower())):
                    matching_task = todo
                    break
            
            if matching_task:
                # Delete the task
                conn.execute('DELETE FROM todos WHERE id=?', (matching_task['id'],))
                
                return {
                    'message': f'🗑️ Deleted task: "{matching_task["title"]}"',
                    'action_type': 'delete_task'
                }
            else:
                return {
                    'message': f'❌ Could not find a task matching "{task_search}". Please be more specific.',
                    'action_type': 'task_not_found'
                }
    
    return None

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    conn = None
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message.strip():
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        # Get current todos for context
        conn = get_db_connection()
        todos = conn.execute('SELECT * FROM todos').fetchall()
        
        # Check if user wants to perform task actions
        action_result = process_task_command(user_message, todos, conn)
        
        if action_result:
            # Task action was performed
            conn.commit()
            conn.close()
            return jsonify({
                'success': True,
                'response': action_result['message'],
                'action_performed': True,
                'action_type': action_result['action_type']
            })
        
        # Prepare context for AI
        todos_context = []
        for todo in todos:
            todos_context.append({
                'title': todo['title'],
                'description': todo['description'],
                'priority': todo['priority'],
                'status': todo['status'],
                'created_at': todo['created_at']
            })
        
        # Create prompt for Gemini
        if todos_context:
            context_str = json.dumps(todos_context, indent=2)
            prompt = f"""You are a helpful AI assistant for a to-do list application. The user has the following tasks:

{context_str}

User message: {user_message}

Please provide a helpful response. If the user is asking about their tasks, provide insights.
If they want to add tasks, suggest how to do it. If they want productivity tips, provide them.
Keep responses concise and actionable."""
        else:
            prompt = f"""You are a helpful AI assistant for a to-do list application. The user doesn't have any tasks yet.

User message: {user_message}

Please provide a helpful response. Encourage them to add tasks and provide productivity tips.
Keep responses concise and actionable."""
        
        # Generate AI response with safety settings
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                )
            )
            
            if response.text:
                ai_response = response.text.strip()
            else:
                ai_response = "I'm sorry, I couldn't generate a response right now. Please try again."
                
        except Exception as ai_error:
            print(f"AI Generation Error: {str(ai_error)}")
            ai_response = "I'm having trouble connecting to my AI service right now. Please try again in a moment."
        
        # Save chat to database
        conn.execute('''
            INSERT INTO chat_messages (user_message, ai_response)
            VALUES (?, ?)
        ''', (user_message, ai_response))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'response': ai_response
        })
        
    except Exception as e:
        print(f"Chat API Error: {str(e)}")
        if conn:
            conn.close()
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your message. Please try again.'
        }), 500

@app.route('/api/ai-suggestions', methods=['POST'])
def get_ai_suggestions():
    try:
        data = request.get_json()
        user_input = data.get('input', '')
        
        if not user_input.strip():
            return jsonify({
                'success': False,
                'error': 'Input cannot be empty'
            }), 400
        
        prompt = f"""The user said: "{user_input}"

Based on this input, suggest 3-5 specific, actionable to-do tasks. 
For each task, also suggest an appropriate priority level (high, medium, low).

Format your response as a JSON array like this:
[
    {{"task": "Task description", "priority": "high"}},
    {{"task": "Another task", "priority": "medium"}}
]

Only return the JSON array, no other text."""
        
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=800,
                )
            )
            
            if response.text:
                # Clean the response text
                response_text = response.text.strip()
                
                # Remove any markdown formatting if present
                if response_text.startswith('```json'):
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                
                # Try to parse the JSON response
                suggestions = json.loads(response_text)
                
                # Validate the suggestions format
                if isinstance(suggestions, list) and all(isinstance(s, dict) and 'task' in s and 'priority' in s for s in suggestions):
                    return jsonify({
                        'success': True,
                        'suggestions': suggestions
                    })
                else:
                    raise ValueError("Invalid suggestions format")
                    
            else:
                raise ValueError("No response from AI")
                
        except (json.JSONDecodeError, ValueError) as parse_error:
            print(f"AI Response Parse Error: {str(parse_error)}")
            # Fallback if AI doesn't return valid JSON
            return jsonify({
                'success': True,
                'suggestions': [
                    {'task': 'Break down your goal into smaller, manageable steps', 'priority': 'medium'},
                    {'task': 'Set a specific deadline for completion', 'priority': 'high'},
                    {'task': 'Gather necessary resources and materials', 'priority': 'medium'},
                    {'task': 'Create a detailed action plan', 'priority': 'high'},
                    {'task': 'Schedule regular progress reviews', 'priority': 'low'}
                ]
            })
        
    except Exception as e:
        print(f"AI Suggestions Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while generating suggestions. Please try again.'
        }), 500

@app.route('/api/productivity-insights', methods=['GET'])
def get_productivity_insights():
    conn = None
    try:
        conn = get_db_connection()
        todos = conn.execute('SELECT * FROM todos').fetchall()
        conn.close()
        
        if not todos:
            return jsonify({
                'success': True,
                'insights': "You don't have any tasks yet. Start by adding some tasks to get productivity insights!"
            })
        
        # Prepare data for AI analysis
        todos_data = []
        for todo in todos:
            todos_data.append({
                'title': todo['title'],
                'priority': todo['priority'],
                'status': todo['status'],
                'created_at': todo['created_at'],
                'completed_at': todo['completed_at']
            })
        
        prompt = f"""Analyze the following to-do list data and provide productivity insights:

{json.dumps(todos_data, indent=2)}

Please provide:
1. Overall productivity patterns
2. Priority distribution analysis
3. Completion trends
4. Actionable recommendations for improvement

Keep the response concise and helpful (max 200 words)."""
        
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                )
            )
            
            if response.text:
                insights = response.text.strip()
            else:
                insights = "I wasn't able to analyze your tasks right now. Please try again later."
                
        except Exception as ai_error:
            print(f"AI Insights Error: {str(ai_error)}")
            insights = "I'm having trouble analyzing your tasks right now. Based on what I can see, try to focus on completing high-priority tasks first and maintain a good balance between different priority levels."
        
        return jsonify({
            'success': True,
            'insights': insights
        })
        
    except Exception as e:
        print(f"Productivity Insights Error: {str(e)}")
        if conn:
            conn.close()
        return jsonify({
            'success': False,
            'error': 'An error occurred while generating insights. Please try again.'
        }), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5004)
