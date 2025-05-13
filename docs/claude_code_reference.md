# Claude Code Reference for AI Dev Toolkit

This file provides guidance to Claude Code (claude.ai/code) when working with the AI Dev Toolkit repository.

## Project Overview

AI Dev Toolkit is a comprehensive system that enhances Claude's capabilities with persistent context, filesystem access, development tools, and AI-optimized task management. The toolkit creates a bidirectional bridge between projects and Claude, enabling code understanding, filesystem operations, task tracking, and unified context awareness.

## Key Components

- **AI Librarian**: Persistent code comprehension system that indexes and analyzes codebases
- **MCP Server**: Model Context Protocol implementation for communication with Claude Desktop
- **Tool Index System**: Catalogs tool functions and provides AI-optimized metadata
- **File System Integration**: Controlled access to development files with comprehensive operations
- **Task Management System**: Persistent task tracking with code context linking

## Development Commands

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install for Claude Code
python scripts/install_for_claude_code.py

# Install to Claude Desktop
python development/install_to_claude.py
```

### Running the Server

```bash
# Launch the AI Librarian server
python development/launch_librarian.py [allowed_directory_paths...]
```

### Testing

```bash
# Run tests
pytest tests/

# Run a specific test
pytest tests/test_librarian_server.py

# Run sanity check
python scripts/run_sanity_check.py
```

### Code Quality

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint code with flake8
flake8
```

### Project Tools

```bash
# Generate tool index
python scripts/tool_index_generator.py

# Apply robustness improvements
python scripts/apply_robustness.py --server-path path/to/server --timeout 120 --retries 3

# Run enhanced indexer
python scripts/run_enhanced_indexer.py
```

## Architecture

The AI Dev Toolkit uses a modular architecture built around the Model Context Protocol (MCP):

1. **Claude Desktop/Code** communicates with the **AI Librarian Server** via MCP
2. **AI Librarian Server** interacts with the **Project Filesystem**
3. **Unified Context System** connects components across subsystems
4. **AI Librarian Persistent Context** maintains project understanding
5. **Tool Reference System** organizes and describes available tools

The system uses an event-driven architecture with file monitoring to keep context up to date as project files change.

## Filesystem Structure

- `aitoolkit/`: Main Python package
  - `gui/`: GUI implementation for configuration
  - `librarian/`: AI Librarian implementation
  - `mcp/`: MCP protocol implementation
  - `server/`: MCP server implementation
  - `utils/`: Utility functions

- `development/`: Development scripts
  - `install_librarian.py`: Install to Claude Desktop
  - `launch_librarian.py`: Launch the server

- `docs/`: Documentation files
- `scripts/`: Utility and launcher scripts
- `tests/`: Unit tests

## Claude Code Integration

When working with AI Dev Toolkit in Claude Code:

1. The toolkit enhances your capabilities with bidirectional references, task tracking, and filesystem operations
2. Claude Code can access mini-librarians in `.ai_reference/` for detailed code understanding
3. Tool relationships can be accessed to understand component interactions
4. You can use the Task Management System to track progress on tasks

## Common Tasks

### Working with the AI Librarian

```python
# Initialize AI Librarian for a project
initialize_librarian("path/to/your/project")

# Query information about a component
query_component("path/to/your/project", "ComponentName")

# Find implementations of specific functionality
find_implementation("path/to/your/project", "login function")
```

### File Operations

```python
# Read a file
read_file("path/to/your/file.py")

# Write to a file
write_file("path/to/your/file.py", "file content")

# List directory contents
list_directory("path/to/your/directory")
```

### Task Management

```python
# Add a task with high priority
add_todo("path/to/project", "Implement login feature", priority="high")

# List tasks
list_todos("path/to/project")

# Update task status
update_todo_status("path/to/project", "todo-123", "completed")
```

### Mini-Librarian Navigation

To access mini-librarians for detailed code understanding:

```bash
# List available mini-librarians
ls .ai_reference/scripts/

# Read a specific mini-librarian
cat .ai_reference/scripts/___aitoolkit_librarian_ai_dev_toolkit_py.json
```

Mini-librarians provide:
- Detailed method signatures
- Docstrings for classes and methods
- Call graphs showing function relationships
- Dependencies and imported modules
- File level metadata