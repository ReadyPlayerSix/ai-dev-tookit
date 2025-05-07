# AI Librarian To-Do List Guide

The AI Librarian To-Do List functionality allows you to maintain a persistent list of tasks across conversations. This guide explains how to use this powerful feature to keep track of ideas, bugs, and tasks that come up during your development work.

## How It Works

The to-do list is stored with your project's AI Librarian data in the `.ai_reference/todos` directory. This means:

- Tasks persist across conversations
- Multiple team members can see and update the same to-do list
- The AI Librarian monitors the list for changes
- Claude can remember, suggest, and update tasks over time

## Available Tools

The To-Do List functionality provides the following tools:

### Adding and Managing Tasks

- `add_todo(project_path, title, description, priority, tags)` - Add a new task
- `list_todos(project_path, status, priority, tag)` - List tasks with optional filtering 
- `update_todo_status(project_path, todo_id, status)` - Mark tasks as active, completed, etc.
- `search_todos(project_path, query)` - Search for tasks by text

### Working with Subtasks

- `add_subtask(project_path, todo_id, title)` - Add a subtask to an existing task

### Intelligent Task Detection

- `infer_todos(project_path, text)` - Automatically detect and add tasks from conversation

## Basic Usage Examples

### Adding a Task

```
add_todo(
    "D:/Projects/my-project", 
    "Implement user authentication", 
    "Add login and registration forms with JWT token support", 
    "high", 
    "security,auth,frontend"
)
```

### Listing Tasks

```
list_todos("D:/Projects/my-project")
```

Or filter by status, priority, or tag:

```
list_todos("D:/Projects/my-project", status="active", priority="high")
```

### Updating Task Status

```
update_todo_status("D:/Projects/my-project", "todo-a1b2c3d4", "completed")
```

### Adding Subtasks

```
add_subtask("D:/Projects/my-project", "todo-a1b2c3d4", "Design login form")
```

### Searching Tasks

```
search_todos("D:/Projects/my-project", "authentication")
```

## Advanced Feature: Automatic Task Detection

The AI Librarian can automatically detect tasks mentioned in conversation. This helps ensure important ideas don't get forgotten.

```
infer_todos("D:/Projects/my-project", "Don't forget to add error handling to the API routes. Later, we should also implement rate limiting.")
```

The system recognizes common phrases like:
- "todo:"
- "don't forget"
- "need to"
- "remember to"
- "later"
- "should"

## Integration with Development Workflow

The to-do list functionality works best when integrated with your development workflow:

1. **During Planning**: Add major tasks and break them down into subtasks
2. **During Coding**: Add tasks for bugs or improvements you discover
3. **During Review**: Update task statuses as work is completed
4. **During Conversations**: Let Claude automatically detect and add tasks

## Best Practices

- Use consistent priority levels (low, medium, high)
- Add meaningful descriptions for complex tasks
- Use tags to categorize tasks (e.g., "bug", "feature", "enhancement")
- Regularly update task statuses
- Use subtasks to break down complex work

## Technical Details

The to-do list is stored as a JSON file in `.ai_reference/todos/todo_list.json`. Each task has:

- A unique ID
- Title and description
- Status and priority
- Tags
- Optional subtasks
- Creation timestamp

You can also directly edit this file if needed, but it's recommended to use the provided tools for most operations.
