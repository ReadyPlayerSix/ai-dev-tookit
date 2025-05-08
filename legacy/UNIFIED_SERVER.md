# AI Dev Toolkit Unified Server

The AI Dev Toolkit Unified Server combines all functionality of the AI Librarian and filesystem tools into a single MCP server that works seamlessly with Claude Desktop.

## Features

This unified server provides:

- **AI Librarian capabilities**: Code understanding, persistent context, component tracking
- **Filesystem operations**: File reading/writing, directory management, search
- **Task management**: AI-optimized todo system with subtasks and inference

## Installation

### Prerequisites

- Python 3.8 or higher
- Claude Desktop (latest version)

### Quick Install

```bash
# Run the installer
python install_unified_server.py
```

This will automatically:

1. Find your Claude Desktop configuration file
2. Add the AI Dev Toolkit Unified Server
3. Remove any previously installed separate servers
4. Create a backup of your configuration

### Installation with Directories

To specify which directories the server should monitor:

```bash
python install_unified_server.py /path/to/project1 /path/to/project2
```

### Installation Options

```
usage: install_unified_server.py [-h] [--name NAME] [--force] [--config CONFIG] [directories ...]

Install AI Dev Toolkit Unified Server to Claude Desktop

positional arguments:
  directories        Directories to monitor (optional)

optional arguments:
  -h, --help         show this help message and exit
  --name NAME        Server name to display in Claude
  --force            Force reinstallation even if already installed
  --config CONFIG    Path to Claude Desktop config file (auto-detected if not specified)
```

## Running the Server Manually

If you want to run the server directly (without installing to Claude Desktop):

```bash
python launch_unified_server.py [directories]
```

## Available Tools

The unified server provides all the tools from both the AI Librarian and filesystem servers:

### AI Librarian Tools

- `initialize_librarian(project_path)`: Set up the AI Librarian for a project
- `query_component(project_path, component_name)`: Get information about a component
- `find_implementation(project_path, search_text)`: Search for implementations
- `generate_librarian(project_path)`: Update the AI Librarian
- `sanity_check(project_path)`: Run a code quality check

### Filesystem Tools

- `read_file(path)`: Read a file's contents
- `write_file(path, content)`: Write content to a file
- `list_directory(path)`: List directory contents
- `create_directory(path)`: Create a new directory
- `search_files(path, pattern)`: Search for files matching a pattern
- `get_file_info(path)`: Get detailed file information
- `directory_tree(path)`: Get a tree view of files and directories

### Task Management Tools

- `add_todo(project_path, title, description, priority, tags)`: Add a new task
- `list_todos(project_path, status, priority, tag)`: List tasks with filtering
- `update_todo_status(project_path, todo_id, status)`: Update a task's status
- `add_subtask(project_path, todo_id, title)`: Add a subtask
- `search_todos(project_path, query)`: Search for tasks
- `infer_todos(project_path, text)`: Extract tasks from text

## Architecture

The unified server follows the same module-level implementation pattern as the working AI Librarian server:

- Uses a module-level FastMCP instance
- Registers tools directly on this instance
- Uses a global state with locks for thread safety
- Implements the same monitoring thread approach

This ensures compatibility with Claude Desktop while providing all functionality in a single server.

## Troubleshooting

If you encounter issues:

1. Check that Claude Desktop is properly configured
2. Verify allowed directories have correct permissions
3. Look for errors in the console output
4. Check the log files:
   - `unified_server.log`
   - `unified_server_launcher.log`
5. Try running the server manually to see detailed output

## Uninstalling

To uninstall the server from Claude Desktop, edit your Claude Desktop configuration file and remove the `"ai-dev-toolkit"` entry from the `mcpServers` section.
