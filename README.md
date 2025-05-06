# AI Dev Toolkit - MCP Server

## ⚠️ DEVELOPMENT STATUS: PRE-ALPHA ⚠️

This project is currently in early development and **not ready for production use**. Tools are being actively developed and may change significantly before the first release.

A comprehensive Model Context Protocol (MCP) server combining file system tools, AI Librarian, code comprehension, project scaffolding, and the Think Tool.

## Overview

The AI Dev Toolkit enhances AI assistants like Claude with powerful capabilities:

1. **File System Tools**: Read, write, and navigate the file system
2. **AI Librarian**: Persistent code comprehension system that maintains project context
3. **Project Starter**: Project generation and scaffolding
4. **Think Tool**: Structured reasoning for complex problems
5. **Context Compression**: Store and retrieve conversation history (Coming Soon)

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Claude Desktop (or other MCP-compatible AI assistant)
- Administrator privileges (for Claude Desktop integration on Windows)

### Installation

```bash
# Clone the repository
git clone https://github.com/[your-github-username]/ai-dev-toolkit.git
cd ai-dev-toolkit

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the installation script (coming soon)
python install.py
```

> **Note**: The installation script is still in development. Currently, you'll need to manually start the server using the provided scripts.

### Using the GUI Configuration Tool

The AI Dev Toolkit includes a graphical configuration tool that makes it easy to integrate with Claude Desktop:

1. Run `launch_gui.bat` (Windows) or `python launch_gui.py` (all platforms)
2. The GUI will:
   - Detect your Claude Desktop installation automatically
   - Allow you to select which toolkit features to enable
   - Let you manage project directories that Claude can access
   - Help you create new projects
   - Monitor the MCP server status

![AI Dev Toolkit GUI](docs/images/gui-screenshot.png)

> **Note**: The GUI handles all Claude Desktop configuration automatically, so you don't need to manually edit configuration files.

### Connect to Claude Desktop (Windows)

If you prefer not to use the GUI, we also provide a simple script to automatically connect the toolkit to Claude Desktop:

1. Run `connect_to_claude.bat` (requires administrator privileges)
2. The script will:
   - Find your Claude Desktop installation
   - Update the configuration to include the MCP server
   - Restart Claude Desktop if needed

For manual configuration:
1. Open Claude Desktop
2. Go to Settings > MCP Servers
3. Click "Add Server" 
4. Enter the following details:
   - Name: AI Dev Toolkit
   - URL: http://localhost:8000
5. Click "Save"
6. Grant permissions when prompted

### Start the Server

The server will start automatically when Claude Desktop launches, but you can also start it manually:

```bash
# Start the server
python src/server.py
```

Or use the GUI to monitor and restart the server as needed.

### Using the Tools

In Claude Desktop, you can access the tools by typing:
```
@AI Dev Toolkit
```

## Available Tools

### File System Tools

- `read_file`: Read file contents
- `write_file`: Write to a file
- `edit_file`: Make line-based edits
- `create_directory`: Create a directory
- `list_directory`: List directory contents
- `directory_tree`: View directory structure
- `move_file`: Move or rename files
- `search_files`: Find files matching a pattern
- `get_file_info`: Get file metadata

### AI Librarian Tools

- `initialize_librarian`: Set up the AI Librarian
- `query_component`: Find component details
- `find_implementation`: Locate code implementations
- `generate_librarian`: Generate the librarian files

### Project Starter Tools

- `create_project_plan`: Generate a project plan
- `generate_project_structure`: Create directory structure
- `create_starter_files`: Generate starter code
- `setup_github_repo`: GitHub setup instructions

### Think Tool

- `think`: A scratchpad for reasoning through problems

### Coming Soon

- **Context Compression**: Store and retrieve conversation history in an AI-optimized format
- **RAG Integration**: Connect to vector databases and knowledge bases for enhanced context

## Examples

### Using the AI Librarian

```
# First, initialize the AI Librarian for a project (creates persistent context)
initialize_librarian("D:/Projects/my-project")

# Now Claude will maintain awareness of your codebase across conversations
# You can query components directly
query_component("D:/Projects/my-project", "MyClass")

# Search for implementations
find_implementation("D:/Projects/my-project", "connect_database")

# The AI Librarian automatically monitors your codebase for changes
# No manual updates needed - Claude always stays in sync with your code
```

### Creating a New Project

```
# Create a project plan
create_project_plan(
    project_name="TaskMaster",
    project_description="A task management application",
    project_type="web",
    key_features=["User authentication", "Task creation and management", "Categories and tags"]
)

# Generate the project structure
generate_project_structure(
    structure_text="taskmaster/\n├── src/\n│   ├── components/\n...",
    output_directory="D:/Projects/taskmaster"
)

# Create starter files
create_starter_files(
    project_directory="D:/Projects/taskmaster",
    project_name="TaskMaster",
    project_type="web"
)
```

## Context Compression (Coming Soon)

The Context Compression tool will:

- Store conversation history in a format optimized for AI language models
- Save compressed context in `.ai_reference` as JSON files
- Allow continuity between sessions without manual context copying
- Prioritize project-relevant information

Benefits:
- Dramatically improved context retention between sessions
- Better understanding of project history
- More consistent assistance

## RAG Integration (Future)

Future versions will include:
- Connection to vector databases
- Document embedding and retrieval
- Semantic search across project documentation
- Integration with knowledge management systems

## Development

### Project Structure

```
ai-dev-toolkit/
├── .ai_reference/       # AI Librarian self-reference system
├── docs/                # Documentation
│   ├── project-plan.md   # Project plan and design document
│   ├── architecture/     # System architecture documentation
│   └── images/           # Documentation images
├── gui/                 # GUI configuration tool
│   └── configurator.py   # Main GUI implementation
├── src/
│   ├── server.py         # Main MCP server implementation
│   ├── librarian/        # AI Librarian components
│   ├── mcp/              # MCP protocol components
│   └── utils/            # Utility functions
├── scripts/
│   ├── connect_to_claude.bat       # Claude Desktop connection script
│   ├── run_project_generator.bat   # Project generation runner
│   ├── project-generator-script.py  # Project generation implementation
│   ├── run_librarian_generator.bat # AI Librarian update script
│   └── context-compressor.py       # Context compression tool
├── tests/                # Test cases
├── launch_gui.bat        # GUI launcher for Windows
├── launch_gui.py         # GUI launcher for all platforms
├── gui_installer.py      # GUI installation script
├── requirements.txt      # Project dependencies
├── install.py            # Installation script
└── README.md             # This file
```

### Running Tests

```bash
# Run tests
python -m pytest tests/
```

## Development Roadmap & Timeline

| Feature | Status | Expected Completion |
|---------|--------|---------------------|
| File System Tools | In Progress | Q2 2025 |
| AI Librarian | Planning | Q2 2025 |
| Project Starter | Concept | Q3 2025 |
| Think Tool | Concept | Q3 2025 |
| GUI Configuration Tool | In Progress | Q2 2025 |
| Context Compression | Planned | Q4 2025 |
| RAG Integration | Future | 2026 |

### How Tools Connect to Claude

This project uses the Model Context Protocol (MCP) to connect tools to Claude:

1. The MCP server runs locally on your machine
2. Claude Desktop connects to the server via localhost
3. Once connected, Claude can "see" and invoke the available tools
4. Tools execute on your local machine and return results to Claude
5. Claude interprets the results and communicates them back to you

![MCP Architecture](docs/mcp-architecture.png)

> **Note**: The architecture diagram will be added in a future update.

## Troubleshooting

### GUI Issues

If the GUI fails to start:
1. Make sure Python and Tkinter are properly installed
2. Try running the GUI installer: `python gui_installer.py`
3. Check if you have permissions to write to the Claude Desktop configuration

### Claude Desktop Connection

If the automatic connection script fails:

1. Check if Claude Desktop is running and close it
2. Try running the script with administrator privileges
3. Manually edit the Claude config at: `%APPDATA%\Claude\config.json`
4. Ensure the server is running before connecting Claude

### Server Issues

If the server fails to start:

1. Check if another process is using port 8000
2. Verify Python version is 3.8 or higher
3. Make sure all dependencies are installed
4. Check logs for specific error messages

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
