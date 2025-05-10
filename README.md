# AI Dev Toolkit

![AI-Assisted](https://img.shields.io/badge/AI--Assisted-Claude%203.7-yellow?logo=anthropic&logoColor=white)
![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)
![Claude Desktop](https://img.shields.io/badge/Claude%20Desktop-Compatible-green)
![MCP](https://img.shields.io/badge/MCP-Enabled-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Release](https://img.shields.io/badge/release-v0.4.0-orange)

A powerful, extensible toolkit that dramatically enhances Claude's capabilities with persistent context, filesystem access, development tools, and AI-optimized task management.

<div align="center">
  <!-- Insert screenshot of GUI here when available -->
  <img src="docs/images/ai-dev-toolkit-banner.png" alt="AI Dev Toolkit Banner" width="800"/>
</div>

## 🌟 Overview

AI Dev Toolkit elevates Claude Desktop beyond a conversational assistant to a comprehensive development partner. The toolkit creates a bidirectional bridge between your projects and Claude, enabling it to:

- **Understand your codebase** through persistent context that spans conversations
- **Access and modify your filesystem** with appropriate permissions
- **Track and manage development tasks** with sophisticated context awareness
- **Offload complex cognitive tasks** to specialized AI mini-librarians
- **Create a seamless development workflow** within Claude's interface

With this toolkit, Claude becomes a true development partner - remembering your project structure, understanding component relationships, tracking tasks, and assisting with development activities.

## 🚀 Features

### AI Librarian Server (Stable)
- **Integrated Architecture**: All capabilities consolidated in one AI Librarian server
- **Simplified Setup**: One-step installation to Claude Desktop
- **Optimized Performance**: Reduced overhead and faster response times
- **Full MCP Compliance**: Complete implementation of Model Context Protocol standards
- **Tool Index Integration**: AI-optimized tool selection and usage guidance

### AI Librarian (Stable)
- **Code Understanding**: Comprehensive codebase indexing with component tracking
- **Persistent Context**: Code structure awareness persists across conversations
- **Component Relationship Analysis**: Automatically detects dependencies and relationships
- **Documentation Generation**: Extracts docstrings and creates documentation
- **Real-time Updates**: Monitors project changes automatically to stay current

### Enhanced Code Analysis (Stable)
- **Reference Finding**: Locate all references to components across the codebase
- **Pattern Detection**: Identify common patterns and anti-patterns
- **File Overview**: Comprehensive analysis of file structure with metrics
- **Component Details**: Rich component information with examples and documentation
- **Usage Context**: Understand how components are used throughout the project

### File System Integration (Stable)
- **Secure Project Access**: Controlled access to your development files
- **Directory Navigation**: Intuitive directory navigation and exploration
- **Code Manipulation**: Read, write, and modify code with proper error handling
- **File Operations**: Comprehensive file management capabilities
- **Search & Indexing**: Find files and content with powerful search tools

### Task Management System (Stable)
- **Persistent To-Do Tracking**: Tasks persist across conversations
- **Multi-level Task Structure**: Support for tasks, subtasks, and dependencies
- **Priority & Status Tracking**: Organize work by importance and completion status
- **Code Context Linking**: Associate tasks with specific code components
- **Automatic Task Inference**: Extract potential tasks from conversations

### Tool Index System (Stable)
- **AI-Optimized Tool Profiles**: Detailed metadata that helps Claude select the right tools
- **Tool Relationships**: Understanding of how tools work together in sequences
- **Decision Trees**: AI-optimized decision frameworks for tool selection
- **Self-Diagnostic Tools**: Capabilities to validate Claude's understanding of context
- **Usage Patterns**: Common patterns for effective tool combinations

### TaskBoard System (Coming Soon - Beta)
- **AI Mini-Librarians**: Specialized AI agents that process specific analysis tasks
- **Asynchronous Processing**: Background task processing for complex operations
- **AI-Optimized Shorthand**: Compressed format for efficient AI-to-AI communication
- **Advanced Context Awareness**: Rich contextual information links tasks to code
- **Distributed Knowledge System**: Intelligence distributed across specialized agents

### Think Tool (Coming Soon - Beta)
- **Advanced AI Reasoning**: Enhanced capability for Claude to reason through complex problems
- **Information Gathering Delegation**: Automatically assign research to mini-librarians
- **Knowledge Synthesis**: Combine insights from multiple specialized agents
- **Contextual Memory**: Build and maintain detailed understanding across sessions
- **Self-directed Exploration**: Allow Claude to explore code paths independently

## 🖼️ Screenshots

<div align="center">
  <!-- These are placeholders - replace with actual screenshots -->
  <table>
    <tr>
      <td><img src="docs/images/screenshot-librarian.png" alt="AI Librarian" width="400"/></td>
      <td><img src="docs/images/screenshot-filesystem.png" alt="File System Integration" width="400"/></td>
    </tr>
    <tr>
      <td><img src="docs/images/screenshot-tasks.png" alt="Task Management" width="400"/></td>
      <td><img src="docs/images/screenshot-configurator.png" alt="Configurator GUI" width="400"/></td>
    </tr>
  </table>
</div>

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Claude Desktop (latest version)
- Git

### Option 1: Install AI Librarian Server (Recommended)
```bash
# Clone the repository
git clone https://github.com/isekaizen/ai-dev-toolkit.git
cd ai-dev-toolkit

# Install dependencies
pip install -r requirements.txt

# Install to Claude Desktop
python development/install_to_claude.py
```

### Option 2: Use the Development Launcher
```bash
# After cloning and installing dependencies
python development/launch.py
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
update_todo_status("path/to/project", "todo-123", "completed")
```

### Advanced AI Task Management
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

### File System Operations
```
# Read a file
read_file("path/to/your/file.py")

# Write to a file
write_file("path/to/your/file.py", "file content")

# List directory contents
list_directory("path/to/your/directory")

# Search for files
search_files("path/to/your/project", "pattern")
```

## 🔌 Architecture

The AI Dev Toolkit uses a modular architecture built around the Model Context Protocol (MCP) to integrate with Claude Desktop:

```
┌─────────────────────┐      ┌───────────────────┐      ┌─────────────────┐
│                     │      │                   │      │                 │
│   Claude Desktop    │◄────►│   AI Librarian    │◄────►│  Your Project   │
│                     │      │     Server        │      │   Filesystem    │
└─────────────────────┘      └───────────────────┘      └─────────────────┘
                                      ▲
                                      │
                                      ▼
                             ┌────────────────────┐
                             │                    │
                             │ Persistent Context & Tool Index │
                             │                    │
                             └────────────────────┘
```

The AI Librarian server provides a seamless interface between Claude Desktop and your project, maintaining persistent context and intelligent tool selection capabilities.

## 🤖 AI-Assisted Development

This toolkit was developed with Claude's assistance, demonstrating the power of human-AI collaboration in creating developer tools. The project itself serves as an example of enhancing AI capabilities through specialized extensions.

Key AI-assisted development techniques used in this project:

- **Iterative Design**: Human-AI dialogue to refine architecture and interfaces
- **Context-Aware Coding**: Using AI Librarian to maintain project context
- **Specialized AI Agents**: Mini-librarians handling specific cognitive tasks
- **Task Decomposition**: Breaking complex problems into manageable chunks
- **Knowledge Integration**: Combining domain expertise with AI capabilities

## 🔍 Troubleshooting

Common issues and solutions:

- **Toolkit Not Appearing in Claude**: Ensure configuration was saved correctly and Claude Desktop was restarted
- **Permission Errors**: Check allowed directories in the configuration
- **Connection Issues**: Verify Claude Desktop is properly configured and restart the server
- **Import Errors**: Make sure all dependencies are installed
- **File Access Problems**: Verify the server has appropriate permissions to access your files

## 📚 Documentation

Additional documentation is available in the [docs](docs/) directory:

- [AI Librarian Guide](docs/ai_librarian_guide.md)
- [Task System Documentation](docs/todo_list_guide.md)
- [MCP Server Template](docs/mcp-server-template.md)
- [Project Structure](docs/project_structure.md)
- [Tools Reference](docs/tools_reference.md)

## 📅 Roadmap

- **Beta Release**: TaskBoard System and Think Tool coming soon
- **GUI Improvements**: Enhanced configurator interface
- **Project Templates**: Starter templates for common project types
- **IDE Integration**: Extensions for VS Code and other IDEs
- **Collaborative Mode**: Multi-user collaboration capabilities
- **Advanced Code Analysis**: Deeper semantic code understanding
- **Team Workflow Tools**: Project management integration

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get involved.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The Claude team at Anthropic for creating an extensible AI assistant
- Contributors to the MCP protocol for enabling rich AI-tool integration
- Everyone in the AI-assisted development community
