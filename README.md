# AI Dev Toolkit

A comprehensive toolkit that enhances Claude's capabilities with persistent context, filesystem access, development tools, and AI-powered task management.

## 🌟 Overview

AI Dev Toolkit integrates with Claude Desktop to provide AI-assisted development capabilities beyond what's available out of the box. The toolkit creates a bridge between your projects and Claude, allowing it to understand your codebase, assist with development tasks, and maintain context across conversations.

## 🚀 Features

### AI Librarian (Stable)
- **Code Understanding**: Maintains a comprehensive index of your codebase
- **Persistent Context**: Remembers code structure across conversations
- **Component Tracking**: Identifies functions, classes, and modules
- **Smart Search**: Find implementations and references quickly
- **Real-time Updates**: Monitors project changes automatically

### Unified MCP Server (Stable)
- **Integrated Experience**: Combined AI Librarian and File System functionality in a single server
- **Simplified Setup**: Easier configuration and installation
- **Improved Performance**: Optimized for faster response times
- **MCP Protocol Support**: Full compliance with Model Context Protocol standards

### File System Tools (Stable)
- **Secure File Access**: Controlled access to your project files
- **Directory Management**: List, search, and navigate directories
- **File Operations**: Read from and write to files with proper encoding detection
- **Directory Visualization**: Generate tree views of project structure
- **File Analysis**: Detailed information about files and their contents

### Enhanced Code Analysis (Stable)
- **Reference Finding**: Locate all references to components across the codebase
- **File Overview**: Get comprehensive analysis of file structure and metrics
- **Component Details**: Enhanced component querying with examples and docstrings
- **Related Files**: Find files related to a specific file based on imports and references

### Task Management (Stable)
- **Task Tracking**: Create and manage AI tasks for your projects
- **Status Updates**: Track progress and update task status
- **Subtasks**: Break down complex tasks into manageable parts
- **Inference**: Automatically extract tasks from conversations

### TaskBoard System (Beta - Coming Soon)
- **AI Mini-Librarians**: Specialized components that process specific tasks for Claude
- **Asynchronous Processing**: Offload complex information gathering to background processes
- **Persistent Communication**: Maintain task state across conversations
- **AI-Optimized Shorthand**: Compressed format for efficient AI-to-AI communication
- **Enhanced Task Context**: Rich contextual information about code tasks

### Think Tool (Beta - Coming Soon)
- **Claude Reasoning**: Enhanced capability for Claude to think through complex problems
- **Task Delegation**: Automatically delegate information gathering to mini-librarians
- **Knowledge Synthesis**: Combine results from multiple information sources
- **Contextual Memory**: Build and maintain detailed understanding across conversations

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Claude Desktop (latest version)

### Installation Options

#### Option 1: Install Unified Server (Recommended)
```bash
# Clone the repository
git clone https://github.com/isekaizen/ai-dev-toolkit.git
cd ai-dev-toolkit

# Install dependencies
pip install -r requirements.txt

# Install to Claude Desktop
python install_unified.py
```

#### Option 2: Install AI Librarian Only
```bash
# After cloning and installing dependencies
python install_to_claude.py
```

## 📊 Usage

### AI Librarian
```
# Initialize AI Librarian for a project
initialize_librarian("path/to/your/project")

# Search for code implementations
find_implementation("path/to/your/project", "login function")

# Query components
query_component("path/to/your/project", "MyClass")
```

### Task Management
```
# Add a task
add_todo("path/to/project", "Implement login feature", priority="high")

# List tasks
list_todos("path/to/project")

# Update task status
update_todo_status("path/to/project", "task-123", "completed")
```

### Advanced AI Task Management (New)
```
# Create an AI-optimized task
add_ai_task("path/to/project", "Authentication system refactoring", "Improve security and performance", "refactor", 2)

# List AI tasks
list_ai_tasks("path/to/project", status="active", priority=1)

# Add detailed code context to a task
# (Coming in TaskBoard update)
```

### Think Tool (Coming Soon)
```
# Think through a complex problem
think("I need to understand how the authentication system works and its dependencies")

# Get task results
get_task_results("task-12345,task-67890")
```

## ⚙️ Configuration

### Configuration File Location
Claude Desktop configuration file is typically located at:
- Windows: `%APPDATA%\Claude Desktop\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude Desktop/claude_desktop_config.json`

The installation scripts handle all configuration file edits automatically.

## 🔍 Troubleshooting

Common issues and solutions:
- **Toolkit Not Appearing in Claude**: Ensure configuration was saved correctly and Claude Desktop was restarted
- **Permission Errors**: Check allowed directories in the configuration
- **Connection Issues**: Verify Claude Desktop is properly configured and restart the server

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Documentation

Additional documentation is available in the [docs](docs/) directory.

## 📅 Roadmap

- **Beta Release**: Coming very soon with TaskBoard System and Think Tool
- **Improved UI**: Enhanced GUI configurator for easier setup (Planned)
- **Project Templates**: Starter templates for common project types (Planned)
- **Integration with Developer Tools**: Support for VS Code, GitHub, etc. (Planned)
