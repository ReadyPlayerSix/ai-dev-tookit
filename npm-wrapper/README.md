# AI Dev Toolkit - MCP Server

This npm package provides a wrapper for the Python-based AI Dev Toolkit MCP server, making it easy to use with Claude Desktop and other MCP clients that expect npm packages.

## Overview

AI Dev Toolkit enhances AI assistants like Claude with powerful capabilities:

1. **File System Tools**: Read, write, and navigate the file system
2. **AI Librarian**: Persistent code comprehension system that maintains project context
3. **Project Starter**: Project generation and scaffolding
4. **Think Tool**: Structured reasoning for complex problems

## Requirements

- **Node.js**: v14 or higher
- **Python**: 3.8 or higher
- **uv**: Python package manager ([install instructions](https://github.com/astral-sh/uv))

## Installation

### Using with Claude Desktop

1. Install the package globally:
   ```bash
   npm install -g @isekaizen/ai-dev-toolkit
   ```

2. Configure Claude Desktop by adding this to your config:
   ```json
   {
     "mcpServers": {
       "ai-dev-toolkit": {
         "command": "npx",
         "args": ["-y", "@isekaizen/ai-dev-toolkit"]
       }
     }
   }
   ```

3. Restart Claude Desktop and the AI Dev Toolkit will be available.

### Using with Other MCP Clients

For other MCP clients that support npm packages, configuration will vary but generally follow the pattern:

```
npx -y @isekaizen/ai-dev-toolkit
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Repository

For the full source code and documentation, visit the [GitHub repository](https://github.com/isekaizen/ai-dev-toolkit).
