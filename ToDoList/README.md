# AI-Powered To-Do List Application

A modern, feature-rich to-do list application powered by Google's Gemini AI, built with Flask and featuring a beautiful, responsive dashboard.

## Features

### ✨ Core Functionality
- **CRUD Operations**: Create, Read, Update, and Delete tasks
- **Task Management**: 
  - Mark tasks as complete with strikethrough effect
  - Priority levels (High, Medium, Low)
  - Due dates
  - Task descriptions
- **Real-time Dashboard**: Live statistics and progress tracking
- **Beautiful UI**: Modern, responsive design with Bootstrap

### 🤖 AI-Powered Features
- **AI Chat Assistant**: Talk with Gemini AI about your tasks and productivity
- **Smart Task Suggestions**: AI generates task recommendations based on your input
- **Productivity Insights**: AI analyzes your tasks and provides actionable insights
- **Natural Language Processing**: Communicate with AI in natural language

### 📊 Dashboard Features
- **Progress Tracking**: Visual progress bars and completion rates
- **Task Statistics**: Total, completed, and pending task counts
- **Priority Distribution**: Visual breakdown of task priorities
- **Quick Task Addition**: Fast task entry directly from dashboard
- **Task Filtering**: Filter by status, priority, and more

### 💬 Interactive Chat
- **Contextual AI**: AI understands your current tasks and provides relevant advice
- **Task Analysis**: Get insights into your productivity patterns
- **Goal Setting**: AI helps you set and achieve your goals
- **Productivity Tips**: Personalized recommendations for better task management

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

1. **Clone or Download the Project**
   ```bash
   cd /Users/abhayrajbhatn/Projects/ToDoList
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   The `.env` file is already configured with your Gemini API key. If you need to change it:
   ```
   GOOGLE_API_KEY=your-api-key-here
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-change-this-in-production
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Application**
   Open your web browser and navigate to: `http://localhost:5000`

## Usage Guide

### Getting Started
1. **Add Your First Task**: Use the "Quick Add Task" section on the dashboard
2. **Set Priorities**: Choose from High, Medium, or Low priority levels
3. **Set Due Dates**: Optional due dates help you stay organized
4. **Complete Tasks**: Check the checkbox to mark tasks as completed (they'll get struck through)

### Using the AI Assistant
1. **Chat with AI**: Type questions or requests in the chat section
2. **Get Task Suggestions**: Click "Suggest Tasks" and describe what you need help with
3. **Analyze Your Productivity**: Click "Get Productivity Insights" for AI analysis
4. **Natural Conversation**: Ask about your tasks, productivity tips, or general advice

### Managing Tasks
- **Edit Tasks**: Click the edit (pencil) icon to modify any task
- **Delete Tasks**: Click the trash icon to remove tasks
- **Filter Tasks**: Use the dropdown to filter by status or priority
- **Track Progress**: Monitor your completion rate in real-time

### Dashboard Features
- **Statistics Cards**: See totals at a glance
- **Progress Bar**: Visual representation of your completion rate
- **Priority Breakdown**: See distribution of task priorities
- **Recent Tasks**: Quick view of your latest tasks

## API Endpoints

### Task Management
- `GET /api/todos` - Get all tasks
- `POST /api/todos` - Create a new task
- `PUT /api/todos/<id>` - Update a task
- `DELETE /api/todos/<id>` - Delete a task

### AI Features
- `POST /api/chat` - Chat with AI assistant
- `POST /api/ai-suggestions` - Get AI task suggestions
- `GET /api/productivity-insights` - Get AI productivity analysis

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite (lightweight, file-based database)
- **AI**: Google Gemini API
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Responsive Design**: Mobile-first approach

## File Structure

```
ToDoList/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (API keys)
├── README.md             # This file
├── todos.db              # SQLite database (created automatically)
├── templates/
│   └── dashboard.html    # Main dashboard template
└── static/
    ├── css/
    │   └── style.css     # Custom CSS styles
    └── js/
        └── app.js        # Frontend JavaScript
```

## Features in Detail

### Task Management
- **Smart Completion**: Tasks marked as complete are visually distinguished with strikethrough text
- **Priority System**: Three-tier priority system with color-coded badges
- **Due Date Tracking**: Optional due dates with calendar picker
- **Bulk Operations**: Easy filtering and management of multiple tasks

### AI Integration
- **Context-Aware**: AI knows about your current tasks and provides relevant suggestions
- **Productivity Analysis**: AI analyzes patterns and provides insights
- **Natural Language**: Communicate in plain English with the AI assistant
- **Task Generation**: AI can suggest specific, actionable tasks based on your goals

### User Experience
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Real-time Updates**: Statistics and progress update instantly
- **Keyboard Shortcuts**: Ctrl+Enter to quickly add tasks
- **Visual Feedback**: Smooth animations and transitions
- **Error Handling**: Graceful error handling with user-friendly messages

## Troubleshooting

### Common Issues

1. **AI Not Responding**
   - Check your internet connection
   - Verify the Gemini API key is correct in `.env`
   - Check the console for error messages

2. **Tasks Not Saving**
   - Ensure you have write permissions in the project directory
   - Check if `todos.db` is created successfully

3. **Styling Issues**
   - Clear your browser cache
   - Ensure all CSS and JS files are loading correctly

### Getting Help
If you encounter issues:
1. Check the browser console for JavaScript errors
2. Check the terminal/command prompt for Python errors
3. Verify all dependencies are installed correctly
4. Make sure the Gemini API key is valid and has quota available

## Security Notes

- The API key is stored in the `.env` file - keep this secure
- In production, use a proper secret key for Flask sessions
- Consider implementing user authentication for multi-user scenarios
- The SQLite database file should be backed up regularly

## Future Enhancements

Potential features to add:
- User authentication and multi-user support
- Task categories and tags
- File attachments for tasks
- Recurring tasks
- Task sharing and collaboration
- Export to calendar applications
- Advanced AI features like deadline prediction
- Email notifications
- Mobile app version

Enjoy using your AI-powered to-do list application! 🚀
