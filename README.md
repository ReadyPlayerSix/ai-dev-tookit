# AI Dev Toolkit

![AI-Assisted](https://img.shields.io/badge/AI--Assisted-Claude%203.7-yellow?logo=anthropic&logoColor=white)
![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)
![Claude Desktop](https://img.shields.io/badge/Claude%20Desktop-Compatible-green)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-purple)
![MCP](https://img.shields.io/badge/MCP-Enabled-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Release](https://img.shields.io/badge/release-v0.4.7--claude--code--integration-orange)

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
- **Navigate between code and tools** with unified context awareness
- **Offload complex cognitive tasks** to specialized AI mini-librarians
- **Create a seamless development workflow** within Claude's interface

With this toolkit, Claude becomes a true development partner - remembering your project structure, understanding component relationships, connecting code to relevant tools, tracking tasks, and assisting with development activities.

All this happens automatically - just initialize once and the system handles everything behind the scenes, continuously updating its understanding of your codebase as it evolves.

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

### Unified Context System (Stable)
- **Automatic Integration**: Zero manual setup - just initialize and everything works
- **Code-Tool Bridging**: Intelligently connects code components to relevant tools
- **Bidirectional References**: Navigate from components to tools and vice versa
- **Context Awareness**: Understands which tools are most useful for specific code
- **Background Maintenance**: Continuously updates cross-references as code evolves

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
- **Edit Bookmarks**: Create, edit, and apply bookmarks for complex code section edits
- **File Operations**: Comprehensive file management capabilities
- **Search & Indexing**: Find files and content with powerful search tools

### Task Management System (Stable)
- **Persistent To-Do Tracking**: Tasks persist across conversations
- **Multi-level Task Structure**: Support for tasks, subtasks, and dependencies
- **Priority & Status Tracking**: Organize work by importance and completion status
- **Code Context Linking**: Associate tasks with specific code components
- **Automatic Task Inference**: Extract potential tasks from conversations

### Tool Index System (Stable)
- **Simple, Robust Implementation**: Single-pass indexing with no subprocesses for improved reliability and performance
- **AI-Optimized Tool Profiles**: Detailed metadata that helps Claude select the right tools 
- **Direct Function Discovery**: Scans common locations for tool functions and imports/analyzes them directly
- **Simplified Output Format**: Flat, reference-catalog style organization for easy navigation
- **Metadata Extraction**: Uses Python's introspection capabilities for accurate tool information

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

### Robustness Features (Stable)
- **Automatic Retries**: Long-running operations automatically retry on failure
- **Timeout Handling**: Graceful handling of timeouts with configurable limits
- **Queue Management**: Clear stale requests before starting new operations
- **Performance Tracking**: Measure and log execution times for optimization
- **Error Recovery**: Robust error handling with detailed diagnostics

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
- Claude Desktop (latest version) or Claude Code
- Git

### Option 1: Install AI Librarian Server for Claude Desktop (Recommended)
```bash
# Clone the repository
git clone https://github.com/isekaizen/ai-dev-toolkit.git
cd ai-dev-toolkit

# Install dependencies
pip install -r requirements.txt

# Install to Claude Desktop
python development/install_to_claude.py
```

### Option 2: Install with Claude Code (Newest)
```bash
# Using Claude Code's terminal:

# Get the installer script
wget https://raw.githubusercontent.com/isekaizen/ai-dev-toolkit/main/scripts/install_for_claude_code.py
# Or with curl:
# curl -O https://raw.githubusercontent.com/isekaizen/ai-dev-toolkit/main/scripts/install_for_claude_code.py

# Run the installer
python install_for_claude_code.py

# Follow the prompts to complete installation
```

The Claude Code installer will:
- Clone the repository from GitHub
- Install necessary dependencies
- Configure the toolkit for your project directories
- Set up CLAUDE.md for improved Claude Code interaction
- Configure for Claude Desktop if requested
- Create desktop shortcuts for the GUI (if tkinter is available)

### Option 3: Use the Development Launcher
```bash
# After cloning and installing dependencies
python development/launch.py
```

## 📊 Usage

### AI Librarian & Unified Context
```
# Initialize AI Librarian for a project
# This one command sets up everything - AI Librarian, Unified Context, and Tool References
initialize_librarian("path/to/your/project")

# Search for code implementations
find_implementation("path/to/your/project", "login function")

# Query components
query_component("path/to/your/project", "MyClass")

# Find tools related to a specific component
find_related_tools("path/to/your/project", "AuthenticationManager")

# Find components related to a specific tool
find_related_components("path/to/your/project", "edit_file")

# Get a unified view of your project
get_unified_context("path/to/your/project")
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

# Edit bookmarks for complex code changes
bookmark_id = create_edit_bookmark("path/to/project", "path/to/file.py", 10, 25)
update_bookmark("path/to/project", bookmark_id, "new content for lines 10-25")
apply_bookmark("path/to/project", bookmark_id)

# List directory contents
list_directory("path/to/your/directory")

# Search for files
search_files("path/to/your/project", "pattern")
```

### Optimizing Performance and Handling Timeouts
```python
# Initialize with robustness features automatically applied
initialize_ai_dev_toolkit("path/to/your/project")

# For other long-running operations, use the robustness decorators
from aitoolkit.utils.tool_wrappers import make_robust

@make_robust(timeout=60.0, max_retries=2)
def my_search_function(query):
    # Implementation here
```

You can also apply the robustness patch to your MCP server installation:

```bash
python scripts/apply_robustness.py --server-path path/to/server --timeout 120 --retries 3
```

This makes search operations and other long-running tasks automatically retry on failure and handle timeouts gracefully.

## 🔌 Architecture

The AI Dev Toolkit uses a modular architecture built around the Model Context Protocol (MCP) to integrate with Claude Desktop:

```
┌───────────────────┐      ┌───────────────┐      ┌───────────┐
│                   │      │               │      │           │
│   Claude Desktop  │◄────►│   AI Librarian│◄────►│Your Project│
│     or Code       │      │     Server    │      │  Filesystem│
└───────────────────┘      └───────────────┘      └───────────┘
                                  ▲
                                  │
                                  ▼
                        ┌─────────────────────┐
                        │                     │
                        │  Unified Context System│
                        │                     │
                        └─────────────────────┘
                                  ▲
                                  │
                                  ▼
                  ┌────────────────┐     ┌────────────────┐
                  │                │     │                │
                  │ AI Librarian   │◄───►│  Tool Reference│
                  │ Persistent     │     │  System        │
                  │ Context        │     │                │
                  └────────────────┘     └────────────────┘
```

The AI Librarian server provides a seamless interface between Claude (Desktop or Code) and your project. The Unified Context System automatically bridges the AI Librarian's code understanding with the Tool Reference System, enabling intelligent navigation between components and tools without any manual configuration.

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
- **Sanity Check Issues**: If experiencing problems with the sanity_check tool, use individual diagnostic tools like find_implementation() and query_component() as alternatives
- **Legacy Files**: Use `git clean -fd` after a `git reset --hard` to ensure all untracked files are removed when reverting to a previous version
- **Duplicate Files**: During our cleanup process, you may encounter duplicate files with extensions like .old, .backup, .fixed - these will be addressed in an upcoming release
- **find_related_files Tool Errors**: This tool has a known issue that will be fixed in an upcoming release
- **Timeout Errors**: For long-running operations that time out, try applying the robustness features with `@make_robust` or use the `apply_robustness.py` script

## 📚 Documentation

Additional documentation is available in the [docs](docs/) directory:

- [AI Librarian Guide](docs/ai_librarian_guide.md)
- [Task System Documentation](docs/todo_list_guide.md)
- [MCP Server Template](docs/mcp-server-template.md)
- [Project Structure](docs/project_structure.md)
- [Tools Reference](docs/tools_reference.md)

## 📅 Roadmap

### Upcoming Releases

- **Beta Release**: TaskBoard System and Think Tool coming soon
- **Codebase Cleanup**: Consolidation of duplicate files and legacy code
- **Sanity Check Improvements**: Enhanced diagnostic capabilities and reporting
- **GUI Improvements**: Enhanced configurator interface with cleanup utilities
- **Project Templates**: Starter templates for common project types

### Future Plans

- **IDE Integration**: Extensions for VS Code and other IDEs
- **Advanced Code Analysis**: Deeper semantic code understanding
- **Team Workflow Tools**: Project management integration

### Current Work in Progress

- **Tool Index Improvements**: Recently implemented the Simple Tool Index system with dramatic performance improvements:
  - Single-pass architecture replaces complex multi-phase processing
  - Direct function discovery with no subprocess handling
  - Up to 10x faster execution (< 5 seconds vs 60+ seconds previously)
  - Improved reliability with fewer failure points
  - Simplified output format for better maintainability

- **Sanity Check Refactoring**: The sanity_check tool will soon be temporarily disabled while we implement significant improvements:
  - Modular class-based design with plugin system
  - Severity levels for issues (critical, warning, info)
  - Two-phase approach: quick scan and detailed analysis
  - Improved reporting with structured JSON and Markdown outputs
  - Better progress tracking and cancellation support
  
- **Directory Structure Cleanup**: Planned consolidation of overlapping functionality:
  - Consolidating duplicate files in the `librarian` directory:
    - Merging enhanced file editing functionality
    - Combining validation tools into a unified module
    - Standardizing naming conventions
  - Cleaning up the `gui` directory:
    - Removing multiple configurator variants
    - Eliminating legacy and backup files
    - Adding a GUI button for legacy file pruning

- **Filesystem Operations**: Enhanced file editing and manipulation capabilities

- **Robustness Improvements**: Enhanced timeout and retry handling:
  - Automatic retry mechanisms for long-running operations
  - Improved queue management to prevent request collisions
  - Performance metrics for identifying bottlenecks
  - Smarter timeout handling with configurable thresholds

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

You're welcome to fork this repository and create your own version to suit your specific needs. This toolkit was created to enhance productivity when working with Claude, and you're encouraged to adapt it to your workflow.

## 🙏 Acknowledgments

- The Claude team at Anthropic for creating an extensible AI assistant
- Contributors to the MCP protocol for enabling rich AI-tool integration
- Everyone in the AI-assisted development community
