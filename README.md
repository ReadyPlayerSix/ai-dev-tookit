# AI Dev Toolkit

![AI-Assisted](https://img.shields.io/badge/AI--Assisted-Claude%203.7-yellow?logo=anthropic&logoColor=white)
![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)
![Claude Desktop](https://img.shields.io/badge/Claude%20Desktop-Compatible-green)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-purple)
![MCP](https://img.shields.io/badge/MCP-Enabled-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Release](https://img.shields.io/badge/release-v0.5.3--security--integration-orange)

A powerful, extensible toolkit that dramatically enhances Claude's capabilities with persistent context, filesystem access, development tools, and AI-optimized task management.

<div align="center">
  <!-- Insert screenshot of GUI here when available -->
  <img src="docs/images/ai-dev-toolkit-banner.png" alt="AI Dev Toolkit Banner" width="800"/>
</div>

## 🌟 Overview

AI Dev Toolkit elevates Claude beyond a conversational assistant to a comprehensive development partner. The toolkit creates a bidirectional bridge between your projects and Claude, enabling it to:

- **Understand your codebase** through persistent context that spans conversations
- **Access and modify your filesystem** with appropriate permissions
- **Track and manage development tasks** with sophisticated context awareness
- **Navigate between code and tools** with unified context awareness
- **Offload complex cognitive tasks** to specialized AI mini-librarians
- **Process long-running operations asynchronously** with the TaskBoard system
- **Analyze codebase security** with professional-level vulnerability assessment
- **Create a seamless development workflow** within Claude's interface

With this toolkit, Claude becomes a true development partner - remembering your project structure, understanding component relationships, connecting code to relevant tools, tracking tasks, and assisting with development activities.

All this happens automatically - just initialize once and the system handles everything behind the scenes, continuously updating its understanding of your codebase as it evolves.

## 🚀 Features

> **Note:** The GUI components are currently under development. Claude Desktop features are in pre-beta phase, while Claude Code features have more streamlined implementation. Feature stability is indicated for each component.

### AI Librarian Server
- **Integrated Architecture**: All capabilities consolidated in one AI Librarian server *(Stable: Code, Pre-Beta: Desktop)*
- **Simplified Setup**: One-step installation to Claude Desktop/Code *(Stable: Code, Beta: Desktop)*
- **Optimized Performance**: Reduced overhead and faster response times *(Stable)*
- **Full MCP Compliance**: Complete implementation of Model Context Protocol standards *(Stable: Desktop)*
- **Tool Index Integration**: AI-optimized tool selection and usage guidance *(Stable)*

### AI Librarian
- **Code Understanding**: Comprehensive codebase indexing with component tracking *(Stable)*
- **Persistent Context**: Code structure awareness persists across conversations *(Stable)*
- **Component Relationship Analysis**: Automatically detects dependencies and relationships *(Stable)*
- **Documentation Generation**: Extracts docstrings and creates documentation *(Stable)*
- **Real-time Updates**: Monitors project changes automatically to stay current *(Stable)*
- **Mini-Librarians**: Handle large codebases by breaking them into specialized knowledge units *(Stable: Code, Beta: Desktop)*

### Unified Context System
- **Automatic Integration**: Zero manual setup - just initialize and everything works *(Stable)*
- **Code-Tool Bridging**: Intelligently connects code components to relevant tools *(Stable)*
- **Bidirectional References**: Navigate from components to tools and vice versa *(Stable)*
- **Context Awareness**: Understands which tools are most useful for specific code *(Stable)*
- **Background Maintenance**: Continuously updates cross-references as code evolves *(Stable)*

### Enhanced Code Analysis
- **Reference Finding**: Locate all references to components across the codebase *(Stable)*
- **Pattern Detection**: Identify common patterns and anti-patterns *(Stable)*
- **File Overview**: Comprehensive analysis of file structure with metrics *(Stable)*
- **Component Details**: Rich component information with examples and documentation *(Stable)*
- **Usage Context**: Understand how components are used throughout the project *(Stable)*
- **Large Codebase Support**: Efficient handling of multi-module projects via mini-librarians *(Stable: Code, Beta: Desktop)*

### File System Integration
- **Secure Project Access**: Controlled access to your development files *(Stable)*
- **Directory Navigation**: Intuitive directory navigation and exploration *(Stable)*
- **Code Manipulation**: Read, write, and modify code with proper error handling *(Stable)*
- **Edit Bookmarks**: Create, edit, and apply bookmarks for complex code section edits *(Stable: Code, Beta: Desktop)*
- **File Operations**: Comprehensive file management capabilities *(Stable)*
- **Search & Indexing**: Find files and content with powerful search tools *(Stable)*

### TaskBoard System
- **Asynchronous Processing**: Execute long-running operations in the background *(Stable)*
- **Prioritized Task Queue**: Manage operations by priority with automatic timeouts *(Stable)*
- **Background Workers**: Pool of worker threads for parallel task execution *(Stable)*
- **Task Persistence**: Operations survive server restarts with automatic recovery *(Stable)*
- **Think Tool**: Deep analytical reasoning capabilities for complex problems *(Stable)*
- **Progress Tracking**: Monitor task status, results and execution metrics *(Stable)*
- **Cross-component Integration**: Unified task processing across all subsystems *(Stable)*

### Task Management System
- **Persistent To-Do Tracking**: Tasks persist across conversations *(Stable)*
- **Multi-level Task Structure**: Support for tasks, subtasks, and dependencies *(Stable)*
- **Priority & Status Tracking**: Organize work by importance and completion status *(Stable)*
- **Code Context Linking**: Associate tasks with specific code components *(Stable)*
- **Automatic Task Inference**: Extract potential tasks from conversations *(Stable: Code, Beta: Desktop)*

### Security Analysis
- **Vulnerability Assessment**: Professional-level security analysis of codebases *(Stable)*
- **Pattern-based Scanning**: Detection of common security vulnerabilities *(Stable)*
- **AST-based Analysis**: Sophisticated code analysis for security issues *(Stable)*
- **Severity Classification**: Issues categorized by criticality (Critical to Info) *(Stable)*
- **Standardized Reporting**: CWE IDs and detailed vulnerability descriptions *(Stable)*
- **AI Toolkit-Specific Patterns**: Custom rules for AI Dev Toolkit components *(Stable)*
- **Integration with Sanity Check**: Combined code quality and security assessment *(Stable)*
- **Independent Security Tool**: Can be used standalone with `security_analyze()` function *(Stable)*

### Tool Index System
- **Simple, Robust Implementation**: Single-pass indexing with no subprocesses for improved reliability and performance *(Stable)*
- **AI-Optimized Tool Profiles**: Detailed metadata that helps Claude select the right tools *(Stable)*
- **Asynchronous Tool Indexing**: Background processing of tool indexing via TaskBoard integration *(Stable)*
- **Bidirectional References**: Cross-references between code components and applicable tools *(Stable)*
- **Component-Tool Mapping**: Automatic mapping of which tools work with specific components *(Stable)*
- **Direct Function Discovery**: Scans common locations for tool functions and imports/analyzes them directly *(Stable)*
- **Simplified Output Format**: Flat, reference-catalog style organization for easy navigation *(Stable)*
- **Metadata Extraction**: Uses Python's introspection capabilities for accurate tool information *(Stable)*

### TaskBoard System (New!)
- **AI Mini-Librarians**: Specialized AI agents that process specific analysis tasks *(Stable)*
- **Asynchronous Processing**: Background task processing for complex operations *(Stable)*
- **Task Queue Management**: Prioritized task execution with timeout handling *(Stable)*
- **Resilient Operations**: Automatic recovery from failures and timeouts *(Stable)*
- **AI-Optimized Shorthand**: Compressed format for efficient AI-to-AI communication *(Stable: Code, Beta: Desktop)*
- **Advanced Context Awareness**: Rich contextual information links tasks to code *(Stable)*
- **Distributed Knowledge System**: Intelligence distributed across specialized agents *(Stable: Code, Beta: Desktop)*

### Think Tool
- **Structured Reflection**: Claude's scratchpad for reasoning through complex problems *(Stable)*
- **Requirements Verification**: Check if all required information is collected *(Stable)*
- **Rule Compliance Checking**: Verify if planned actions comply with policies *(Stable)*
- **Detailed Planning**: Break down complex tasks into manageable steps *(Stable)*
- **Results Analysis**: Process and verify the results of other tools *(Stable)*
- **Clear Separation**: Keep internal thought processes separate from user conversation *(Stable)*
- **Decision Support**: Compare approaches and select the best option *(Stable)*

### Robustness Features
- **Automatic Retries**: Long-running operations automatically retry on failure *(Stable)*
- **Timeout Handling**: Graceful handling of timeouts with configurable limits *(Stable)*
- **Queue Management**: Clear stale requests before starting new operations *(Stable)*
- **Performance Tracking**: Measure and log execution times for optimization *(Stable)*
- **Error Recovery**: Robust error handling with detailed diagnostics *(Stable)*
- **Large Codebase Handling**: Efficient processing of large repositories with segmentation *(Stable: Code, Beta: Desktop)*

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

> **Note:** The GUI components are currently under development. Command-line and code-based interactions are fully functional, while the graphical interface for directory selection and configuration is in beta phase.

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

```python
# Initialize AI Librarian for a project
# This one command sets up everything - AI Librarian, Unified Context, and Tool References
initialize_enhanced_librarian("path/to/your/project")

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

#### Large Codebase Support

For larger codebases, the AI Dev Toolkit uses mini-librarians to provide efficient navigation and understanding:

```python
# Access mini-librarians directly (Claude Code)
read_file(".ai_reference/scripts/___aitoolkit_librarian_ai_dev_toolkit_py.json")

# Get component information from mini-librarians
get_component_details("path/to/project", "ComponentName") 

# Search across mini-librarians
search_mini_librarians("path/to/project", "function_name")
```

### Task Management
```python
# Add a task
add_todo("path/to/project", "Implement login feature", priority="high")

# List tasks
list_todos("path/to/project")

# Update task status
update_todo_status("path/to/project", "todo-123", "completed")
```

### Advanced AI Task Management
```python
# Create an AI-optimized task
add_ai_task("path/to/project", "Authentication system refactoring", "Improve security and performance", "refactor", 2)

# List AI tasks
list_ai_tasks("path/to/project", status="active", priority=1)

# Add detailed code context to a task
add_task_context(task_id, "code_snippet", "Task relates to authentication system")
```

### Think Tool
```python
# Use the think tool as a scratchpad for reflection
think("""
User wants to implement a new authentication feature.
- Required information:
  * User roles and permissions structure
  * Current authentication flow
  * Security requirements
- Implementation approach options:
  * Extend existing AuthManager
  * Create new specialized AuthProvider
  * Use third-party authentication library
- Considerations:
  * Performance impact
  * Security implications
  * Maintenance complexity
- Decision:
  * Extending existing AuthManager seems most appropriate
  * Need to add role validation logic
  * Will require unit tests for new functionality
""")

# For deeper, time-consuming analysis, use deep_analysis from the TaskBoard system
task_id = deep_analysis(project_path, "I need to understand how the authentication system works and its dependencies")
get_task_status(project_path, task_id)
get_task_result(project_path, task_id)
```

### File System Operations
```python
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

### Claude Code vs Desktop Functionality

Claude Code can simulate toolkit functionality through mini-librarians and adapter patterns:

| Feature | Claude Code | Claude Desktop |
|---------|------------|----------------|
| File Operations | Native tools + Simulated toolkit via adapters | MCP Server with direct toolkit access |
| Mini-Librarians | Direct JSON access and interpretation | Server API access |
| Task Management | Simulated through adapter patterns | Direct function calls |
| GUI Configuration | Command-line installer | Visual interface (Beta) |
| Large Codebase Handling | Native tools with mini-librarian guidance | Server-based processing (Beta) |
| Installation | One-command direct install | Requires Desktop config |
| Toolkit Functions | Simulated via adapter patterns in `.ai_reference` | Direct function calls |

#### Claude Code Adapter Patterns

Claude Code uses adapter patterns stored in the `.ai_reference` directory to simulate toolkit functionality:

```python
# Example: Instead of direct toolkit call like:
result = create_edit_bookmark("path/to/project", "path/to/file.py", 10, 25)

# Claude Code reads the adapter pattern and executes:
file_content = read_file("path/to/file.py")
content_to_edit = file_content.splitlines()[10:25]
# Store in memory for later application
session_bookmarks["bookmark1"] = {"file": "path/to/file.py", "start": 10, "end": 25, "content": content_to_edit}
```

### Security Analysis

```python
# Run a comprehensive security analysis on your project
security_report = security_analyze("path/to/your/project")

# Enhanced sanity check with security analysis included
check_report = enhanced_sanity_check("path/to/your/project", include_security=True)
```

The adapter patterns provide Claude Code with the context and steps needed to achieve equivalent functionality using native tools.

### Optimizing Performance and Handling Timeouts
```python
# Initialize with robustness features automatically applied
# This is the recommended all-in-one initialization method
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

The AI Dev Toolkit uses a modular architecture built around the Model Context Protocol (MCP) to integrate with Claude:

### Claude Desktop Architecture
```
┌───────────────────┐      ┌───────────────┐      ┌───────────┐
│                   │      │               │      │           │
│   Claude Desktop  │◄────►│   AI Librarian│◄────►│Your Project│
│                   │      │     Server    │      │  Filesystem│
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

### Claude Code Architecture
```
┌───────────────────┐      ┌───────────────┐      ┌───────────┐
│                   │      │ Built-in Tools│      │           │
│   Claude Code     │◄────►│ + AI Librarian│◄────►│Your Project│
│                   │      │   Components  │      │  Filesystem│
└───────────────────┘      └───────────────┘      └───────────┘
                                  ▲
                                  │
                                  ▼
                        ┌─────────────────────┐
                        │                     │
                        │ .ai_reference/      │
                        │ Mini-Librarians     │
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

The AI Librarian components provide a seamless interface between Claude and your project. The Unified Context System automatically bridges the AI Librarian's code understanding with the Tool Reference System, enabling intelligent navigation between components and tools without any manual configuration.

Claude Code can directly access Mini-Librarians through its file system tools, while Claude Desktop requires the MCP server to access these components.

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

- **Beta Release**: Advanced GUI interface improvements coming soon
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

- **Sanity Check & Security Analysis**: The sanity_check tool has been significantly improved:
  - Integration with the Security Analyzer for comprehensive assessment
  - Support for severity levels (critical, warning, info)
  - Enhanced error handling and encoding fixes
  - Professional security assessment with CWE IDs
  - AST-based analysis for deeper code understanding
  - Improved reporting with structured outputs
  
- **Directory Structure Cleanup**: Ongoing consolidation of overlapping functionality:
  - Consolidating duplicate files in the `librarian` directory:
    - Merging enhanced file editing functionality
    - Standardizing naming conventions across modules
    - Removing deprecated functionality (basic indexer has been replaced by enhanced_indexer)
  - Cleaning up the `gui` directory:
    - Standardizing on configurator_new.py as the primary GUI implementation
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
