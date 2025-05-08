# Integrated MCP Server

This module provides an integrated MCP server that combines AI Librarian and enhanced filesystem functionality into a single server.

## Features

- **Code Understanding**: Full AI Librarian functionality for code context
- **Enhanced File Operations**: Improved filesystem tools with semantic understanding
- **Relationship Analysis**: Find related files and references throughout the codebase
- **File Overviews**: Comprehensive analysis of file structure and complexity
- **Task Management**: AI-optimized task tracking system

## Using the Integrated Server

### Installing to Claude Desktop

The easiest way to install the integrated server is to use the provided installation script:

```bash
python install_integrated_server.py [directories_to_monitor]
```

This will update your Claude Desktop configuration to use the integrated server, replacing the separate AI Librarian and File System servers if they were previously installed.

### Running Directly

You can also run the integrated server directly:

```bash
python launch_integrated_server.py [directories_to_monitor]
```

### Programmatic Usage

```python
from aitoolkit.mcp import IntegratedServer, create_server

# Create the server
server = create_server()

# Run the server
server.run()
```

## Enhanced Tools

The integrated server provides several enhanced tools that improve on the basic functionality:

### find_related_files

Find files related to a specific file based on imports, references, and project structure.

```
Find files related to src/librarian/core.py
```

### find_references

Find all references to a component (class, function, variable) across the codebase.

```
Find references to query_component function
```

### get_file_overview

Get a comprehensive overview of a file including its structure, imports, and complexity metrics.

```
Show me an overview of aitoolkit/librarian/server.py
```

### optimized_query_component

An optimized version of the standard query_component that provides more detailed information and better performance.

```
Tell me about the IntegratedServer class
```

## Configuration

The integrated server reads the following environment variables:

- `AI_LIBRARIAN_ALLOWED_DIRS`: Comma-separated list of directories to monitor
