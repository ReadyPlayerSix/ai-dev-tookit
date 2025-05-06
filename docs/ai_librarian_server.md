# AI Librarian MCP Server

A standalone MCP server that provides code understanding and context maintenance for AI assistants like Claude.

## Features

- Code parsing and component tracking
- Project monitoring for changes
- Persistent context across conversations
- Search for components and implementations
- Automatic updates when code changes

## Setup

### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ai-dev-toolkit.git
cd ai-dev-toolkit/ai-librarian-server

# Install dependencies with uv
uv pip install -r requirements.txt
```

## Usage

### Running the server

```bash
# Run with Python
python server.py [path_to_project1] [path_to_project2] ...

# Or with uv
uv run python server.py [path_to_project1] [path_to_project2] ...
```

### Configuring Claude Desktop

Add the following to your Claude Desktop configuration file (located at `~/Library/Application Support/Claude/claude_desktop_config.json` or equivalent):

```json
{
  "mcpServers": {
    "ai-librarian": {
      "command": "python",
      "args": [
        "D:/Projects/isekaiZen/ai-dev-toolkit/ai-librarian-server/server.py",
        "D:/YourProjectPath"
      ]
    }
  }
}
```

Or using uv:

```json
{
  "mcpServers": {
    "ai-librarian": {
      "command": "uv",
      "args": [
        "run",
        "--directory", 
        "D:/Projects/isekaiZen/ai-dev-toolkit/ai-librarian-server",
        "server.py",
        "D:/YourProjectPath"
      ]
    }
  }
}
```

## Available Tools

- `list_allowed_directories`: List directories the server can access
- `check_project_access`: Check if a directory can be accessed
- `initialize_librarian`: Set up the librarian for a project
- `query_component`: Get details about a component
- `find_implementation`: Search for code implementations
- `generate_librarian`: Update the librarian for a project

## License

MIT License
