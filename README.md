# AI Dev Toolkit

A comprehensive Model Context Protocol (MCP) server designed to enhance AI assistants like Claude with powerful development capabilities.

## Overview

The AI Dev Toolkit provides an MCP server that extends Claude with file system access, code comprehension, project management, and reasoning tools. It creates a seamless development experience by maintaining context across conversations and providing deep understanding of your codebase.

### Key Features

- **File System Tools**: Secure access to read, write, and manage files with appropriate permissions
- **AI Librarian**: Persistent code comprehension system that analyzes and understands your codebase
- **Project Starter**: Templates and scaffolding for new development projects
- **Think Tool**: Structured reasoning tools for complex problem-solving

## Installation

### Prerequisites

- Python 3.8 or higher
- `uv` package manager (recommended) or `pip`
- Claude Desktop (for best experience)

### Quick Install

```bash
# Using uv (recommended)
uv add "isekaizen-ai-dev-toolkit[cli]"

# Using pip
pip install "isekaizen-ai-dev-toolkit[cli]"
```

### Claude Desktop Integration

The AI Dev Toolkit comes with a convenient GUI for Claude Desktop configuration:

1. Launch the GUI configurator:
   ```bash
   uv run ai-dev-toolkit-gui
   ```

2. The configurator will:
   - Detect your Claude Desktop installation
   - Allow selection of enabled tools
   - Configure project directories
   - Set up the MCP server

## Usage

### Starting the Server

```bash
# Start the server with default settings
uv run ai-dev-toolkit

# Start with specific directories
uv run ai-dev-toolkit /path/to/project1 /path/to/project2
```

### Using Claude with AI Librarian

1. Initialize a project:
   ```
   initialize_librarian("path/to/your/project")
   ```

2. Claude will analyze your codebase and maintain context across conversations.

3. Use the AI Librarian tools:
   ```
   query_component("path/to/project", "ComponentName")
   find_implementation("path/to/project", "search text")
   ```

### Project Management

Create new projects with the proper structure:

```
create_project_plan("Project Name", "Description", "web|cli|library|api", ["Feature 1", "Feature 2"])
```

### File Operations

Securely access and modify files:

```
read_file("path/to/file.txt")
write_file("path/to/file.txt", "content")
list_directory("path/to/directory")
search_files("path/to/directory", "search term")
```

## Components

### MCP Server

The MCP server follows the Model Context Protocol standard, providing a structured interface for AI assistants to access development tools and resources.

### AI Librarian

The AI Librarian maintains a comprehensive index of your codebase, creating:

- Mini-librarians for individual files
- Component registry for classes and functions
- Contextual linking between components
- Real-time monitoring for code changes

### Project Starter

Templates and generators for various project types, providing:

- Standard directory structures
- Starter files
- GitHub repository setup
- Common development workflows

### Think Tool

A structured reasoning interface for complex problems:

```
think("This is a complex problem. Let me break it down step by step...")
```

## Development

This project is currently in PRE-ALPHA status. Several features are implemented, while others are planned for future releases.

### Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
