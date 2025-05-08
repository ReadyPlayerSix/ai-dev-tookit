# MCP Server Creation and Connection Template

This comprehensive guide provides a template and best practices for creating Model Context Protocol (MCP) servers and connecting them to Claude Desktop.

## Table of Contents
1. [MCP Server Structure](#mcp-server-structure)
2. [Server Implementation Template](#server-implementation-template)
3. [Tool Implementation](#tool-implementation)
4. [Resource Implementation](#resource-implementation)
5. [Prompt Implementation](#prompt-implementation)
6. [Connecting to Claude Desktop](#connecting-to-claude-desktop)
7. [Testing and Debugging](#testing-and-debugging)
8. [Common Issues and Solutions](#common-issues-and-solutions)

## MCP Server Structure

An MCP server consists of:

- **Server Definition**: A FastMCP instance that handles communication with the MCP client
- **Tools**: Functions that can be called by the model to perform actions
- **Resources**: Data sources that can be accessed by the model
- **Prompts**: Predefined prompts that can be invoked by the user

### Key Components

```
my_mcp_server/
├── server.py            # Main server implementation
├── requirements.txt     # Dependencies
├── tools/               # Tool implementations
│   └── __init__.py
├── resources/           # Resource implementations
│   └── __init__.py
└── README.md            # Documentation
```

## Server Implementation Template

Here's a robust template for implementing an MCP server:

```python
#!/usr/bin/env python3
"""
My MCP Server

Description of what this server does and its capabilities.

Key Features:
- Feature 1
- Feature 2
- Feature 3

Usage:
    python server.py [additional_args...]
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the current directory to sys.path to ensure local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import FastMCP with robust error handling
try:
    # First try the pip-installed mcp package
    from mcp.server.fastmcp import FastMCP, Context
except ImportError:
    try:
        # Try to install mcp package
        import subprocess
        print("Attempting to install mcp package...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp[cli]"])
        from mcp.server.fastmcp import FastMCP, Context
        print("Successfully installed and imported mcp package")
    except Exception as e:
        print(f"Error installing mcp package: {e}")
        raise ImportError("Could not import FastMCP. Please install the mcp package: pip install mcp[cli]")

# Configure logging
logger = logging.getLogger("my-mcp-server")
logger.setLevel(logging.INFO)

# Clear any existing handlers
if logger.handlers:
    logger.handlers.clear()

# File handler - all levels
file_handler = logging.FileHandler("my_mcp_server.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Console handler - only warnings and errors
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.WARNING)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Create the MCP server
mcp = FastMCP(
    "my-mcp-server",  # Server name shown to the user
    capabilities={
        "resources": {"subscribe": True, "listChanged": True},
        "tools": {"listChanged": True},
        "prompts": {"listChanged": True}
    }
)

# Dictionary to store permission status of directories
permission_status = {}

# Parse directories from command line args
def initialize_allowed_directories():
    """Initialize the list of directories that this server is allowed to access."""
    allowed_dirs = []
    
    # Check for directories in environment variables
    if "MCP_SERVER_ALLOWED_DIRS" in os.environ:
        env_dirs = os.environ["MCP_SERVER_ALLOWED_DIRS"].split(",")
        for dir_path in env_dirs:
            if dir_path and os.path.exists(dir_path):
                allowed_dirs.append(os.path.abspath(dir_path))
                logger.info(f"Added allowed directory from environment: {dir_path}")
    
    # Check for directories in command line args
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if os.path.exists(arg) and arg not in allowed_dirs:
                allowed_dirs.append(os.path.abspath(arg))
                logger.info(f"Added allowed directory from command line: {arg}")
    
    # Add the current directory as a fallback
    if not allowed_dirs:
        current_dir = os.getcwd()
        allowed_dirs.append(current_dir)
        logger.info(f"Added current directory: {current_dir}")
    
    # Update our permission status tracker
    for dir_path in allowed_dirs:
        permission_status[dir_path] = True
    
    logger.info(f"Allowed directories: {allowed_dirs}")
    return allowed_dirs

# Get allowed directories
ALLOWED_DIRECTORIES = initialize_allowed_directories()

#-----------------------------------------------------------------
# Tool Implementations
#-----------------------------------------------------------------

@mcp.tool()
def list_allowed_directories() -> List[str]:
    """
    Returns the list of directories that this server is allowed to access.
    
    Returns:
        A list of allowed directory paths
    """
    return ALLOWED_DIRECTORIES

@mcp.tool()
def check_access(path: str) -> str:
    """
    Check if the server has permission to access a specific path.
    
    Args:
        path: The path to check
        
    Returns:
        Status message about access
    """
    try:
        # Normalize the path
        path = os.path.abspath(path)
        
        # First check our permission tracker
        if path in permission_status and permission_status[path]:
            return f"✅ The server has permission to access: {path}"
        
        # Check if the path is within any of the allowed directories
        for allowed_dir in ALLOWED_DIRECTORIES:
            if path.startswith(allowed_dir) or allowed_dir.startswith(path):
                permission_status[path] = True
                return f"✅ The server has permission to access: {path}"
        
        # Try to access the path
        if not os.path.exists(path):
            return f"❌ Path does not exist: {path}"
        
        # Try to list a directory or read a file as a basic access test
        try:
            if os.path.isdir(path):
                os.listdir(path)
            else:
                with open(path, 'r') as f:
                    f.read(1)  # Read just the first byte
            
            # If we get here, we have access
            permission_status[path] = True
            return f"✅ The server has permission to access: {path}"
        except PermissionError:
            permission_status[path] = False
            return f"❌ Permission denied: {path}"
    except Exception as e:
        logger.error(f"Error checking access: {str(e)}")
        return f"❌ Error checking access: {str(e)}"

# Add more tool implementations here
# @mcp.tool()
# def my_tool(arg1: str, arg2: int = 0) -> Dict[str, Any]:
#     """
#     Description of what this tool does.
#     
#     Args:
#         arg1: Description of arg1
#         arg2: Description of arg2
#         
#     Returns:
#         Description of the return value
#     """
#     try:
#         # Tool implementation
#         result = {"status": "success", "data": f"Processed {arg1} with {arg2}"}
#         return result
#     except Exception as e:
#         logger.error(f"Error in my_tool: {str(e)}")
#         return {"status": "error", "message": str(e)}

#-----------------------------------------------------------------
# Resource Implementations
#-----------------------------------------------------------------

# Example resource implementation
# @mcp.resource("my-data://{param}")
# def get_my_data(param: str) -> str:
#     """
#     Get data for the specified parameter.
#     
#     Args:
#         param: The parameter to get data for
#         
#     Returns:
#         The data for the parameter
#     """
#     try:
#         # Resource implementation
#         return f"Data for {param}"
#     except Exception as e:
#         logger.error(f"Error getting data for {param}: {str(e)}")
#         return f"Error: {str(e)}"

#-----------------------------------------------------------------
# Prompt Implementations
#-----------------------------------------------------------------

# Example prompt implementation
# @mcp.prompt()
# def my_prompt() -> str:
#     """
#     Description of what this prompt does.
#     """
#     return """
#     This is a prompt template that can be invoked by the user.
#     It can contain placeholders for arguments that will be filled in.
#     """

#-----------------------------------------------------------------
# Main Function
#-----------------------------------------------------------------

if __name__ == "__main__":
    logger.info(f"Starting MCP server with allowed directories: {ALLOWED_DIRECTORIES}")
    mcp.run()
```

## Tool Implementation

Tools are functions that can be called by the model to perform actions. They should:

1. Be decorated with `@mcp.tool()`
2. Have clear docstrings that describe what the tool does, its arguments, and its return value
3. Include error handling to gracefully handle unexpected inputs
4. Return structured responses that can be easily understood by the model

Example tool implementation:

```python
@mcp.tool()
def read_file(path: str) -> Dict[str, Any]:
    """
    Read the contents of a file.
    
    Args:
        path: Path to the file to read
        
    Returns:
        Dictionary with the file contents or error information
    """
    try:
        # Check access permission
        if path not in permission_status:
            for allowed_dir in ALLOWED_DIRECTORIES:
                if path.startswith(allowed_dir):
                    permission_status[path] = True
                    break
            else:
                return {
                    "status": "error",
                    "message": f"Access denied: {path} is not within allowed directories"
                }
        
        # Ensure the file exists
        if not os.path.exists(path):
            return {"status": "error", "message": f"File not found: {path}"}
        
        # Read the file
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Return the content with metadata
        return {
            "status": "success",
            "path": path,
            "content": content,
            "size": len(content)
        }
    except Exception as e:
        logger.error(f"Error reading file {path}: {str(e)}")
        return {"status": "error", "message": str(e)}
```

## Resource Implementation

Resources provide data that can be accessed by the model. They should:

1. Be decorated with `@mcp.resource(pattern)`
2. Have a URL pattern that clearly indicates the resource type and parameters
3. Return the resource data in a format that can be understood by the model

Example resource implementation:

```python
@mcp.resource("config://{name}")
def get_config(name: str) -> str:
    """
    Get configuration information.
    
    Args:
        name: Name of the configuration to get
        
    Returns:
        Configuration information
    """
    try:
        configs = {
            "server": "This is the server configuration",
            "client": "This is the client configuration",
            "database": "This is the database configuration"
        }
        
        if name in configs:
            return configs[name]
        else:
            return f"Configuration not found: {name}"
    except Exception as e:
        logger.error(f"Error getting configuration {name}: {str(e)}")
        return f"Error: {str(e)}"
```

## Prompt Implementation

Prompts provide pre-defined templates that can be invoked by the user. They should:

1. Be decorated with `@mcp.prompt()`
2. Return a string or a list of messages that will be shown to the user

Example prompt implementation:

```python
@mcp.prompt()
def help_prompt() -> str:
    """
    Provide help information about the server.
    """
    return """
    # MCP Server Help
    
    This server provides the following capabilities:
    
    ## Tools
    - `list_allowed_directories()`: List directories the server can access
    - `check_access(path)`: Check if the server can access a path
    - `read_file(path)`: Read a file's contents
    
    ## Resources
    - `config://{name}`: Get configuration information
    
    ## Examples
    
    To read a file:
    ```
    result = read_file("/path/to/file")
    print(result["content"])
    ```
    
    To check access:
    ```
    access = check_access("/path/to/check")
    print(access)
    ```
    """
```

## Connecting to Claude Desktop

To connect your MCP server to Claude Desktop, you need to add it to the `claude_desktop_config.json` file:

### Manual Configuration

1. Locate the Claude Desktop configuration directory:
   - Windows: `%APPDATA%\Claude`
   - macOS: `~/Library/Application Support/Claude`
   - Linux: `~/.config/Claude`

2. Edit or create the `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "python",
      "args": ["/path/to/your/server.py"],
      "env": {
        "MCP_SERVER_ALLOWED_DIRS": "/path/to/dir1,/path/to/dir2"
      }
    }
  }
}
```

### Installation Script

Create an installation script to automate the process:

```python
#!/usr/bin/env python3
"""
Installation script for MCP server with Claude Desktop
"""
import os
import json
import sys
from pathlib import Path

def install_to_claude_desktop():
    """Install the MCP server to Claude Desktop"""
    # Determine Claude Desktop config path based on platform
    home = Path.home()
    
    if os.name == 'nt':  # Windows
        config_dir = home / "AppData" / "Roaming" / "Claude"
    elif os.name == 'posix':  # macOS/Linux
        if os.path.exists(home / "Library" / "Application Support" / "Claude"):  # macOS
            config_dir = home / "Library" / "Application Support" / "Claude"
        else:  # Linux
            config_dir = home / ".config" / "Claude"
    else:
        print(f"Unsupported platform: {os.name}")
        return False
    
    # Ensure config directory exists
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Path to Claude Desktop config file
    config_file = config_dir / "claude_desktop_config.json"
    
    # Create or update config
    config = {}
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except:
            print(f"Warning: Could not read existing config file {config_file}")
    
    # Add or update server configuration
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    
    # Get allowed directories from user
    print("\nMCP Server Installation")
    print("====================================")
    print("\nThis will install the MCP server to Claude Desktop.")
    print("The server needs access to your directories.")
    
    # Default to the current directory
    default_dirs = [str(current_dir)]
    
    # Ask for additional directories
    print(f"\nDefault directory: {current_dir}")
    add_more = input("Do you want to add more directories? (y/n): ").lower() == 'y'
    
    additional_dirs = []
    while add_more:
        dir_path = input("Enter directory path (or leave empty to finish): ")
        if not dir_path:
            break
            
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            additional_dirs.append(str(path))
            print(f"Added: {path}")
        else:
            print(f"Directory not found: {path}")
        
        add_more = input("Add another directory? (y/n): ").lower() == 'y'
    
    # Combine all directories
    all_dirs = default_dirs + additional_dirs
    
    # Configure the server
    config["mcpServers"]["my-mcp-server"] = {
        "command": "python",
        "args": [str(current_dir / "server.py")],
        "env": {
            "MCP_SERVER_ALLOWED_DIRS": ",".join(all_dirs)
        }
    }
    
    # Save config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nSuccessfully installed MCP server to Claude Desktop")
    print(f"Configuration saved to: {config_file}")
    print("\nAllowed directories:")
    for dir_path in all_dirs:
        print(f"- {dir_path}")
    
    print("\nPlease restart Claude Desktop to apply changes")
    
    return True

if __name__ == "__main__":
    install_to_claude_desktop()
```

## Testing and Debugging

### Running the Server Directly

Test your server by running it directly:

```bash
python server.py [/path/to/dir1] [/path/to/dir2]
```

### Debugging with Logging

Use the logging configuration to debug issues:

```python
# Enable debug logging
logger.setLevel(logging.DEBUG)
console_handler.setLevel(logging.DEBUG)
```

### Checking Claude Desktop Logs

Claude Desktop logs can be found in:
- Windows: `%USERPROFILE%\AppData\Roaming\Claude\logs`
- macOS: `~/Library/Logs/Claude`
- Linux: `~/.config/Claude/logs`

### Common Debugging Steps

1. Verify server starts without errors
2. Check Claude Desktop logs for connection issues
3. Test individual tools with direct calls
4. Verify access permissions to directories

## Common Issues and Solutions

### Import Errors

**Problem**: Unable to import FastMCP or related modules.

**Solution**: 
- Install the MCP package: `pip install mcp[cli]`
- Check your Python path
- Use the import error handling shown in the template

### Permission Issues

**Problem**: Server cannot access required directories.

**Solution**:
- Verify allowed directories are correctly specified
- Use the `check_access` tool to verify permissions
- Update Claude Desktop permissions settings

### Connection Issues

**Problem**: Claude Desktop cannot connect to the server.

**Solution**:
- Verify the server path in `claude_desktop_config.json` is correct
- Make sure the server is executable
- Check logs for specific error messages
- Restart Claude Desktop after configuration changes

### Tool Errors

**Problem**: Tools return errors or unexpected results.

**Solution**:
- Add robust error handling to all tools
- Return structured error information
- Use logging to track tool execution and errors
- Test tools independently before integrating with Claude

### Resource Loading Issues

**Problem**: Resources are not properly loaded or recognized.

**Solution**:
- Verify resource patterns are correctly formatted
- Ensure resource implementations return expected data types
- Test resources independently before integrating with Claude

## Best Practices

1. **Robust Error Handling**: Always include try/except blocks in your tools and resources
2. **Clear Documentation**: Provide detailed docstrings for all tools, resources, and prompts
3. **Structured Responses**: Return structured data that can be easily parsed
4. **Permissions Management**: Carefully check access permissions for all file operations
5. **Logging**: Use comprehensive logging to track server operations and errors
6. **Graceful Degradation**: Tools should handle unexpected inputs and fail gracefully
7. **Environment Variables**: Use environment variables for configuration instead of hardcoding values
8. **Versioning**: Include version information in your server metadata
9. **Testing**: Test all tools and resources independently before deploying

---

This template provides a solid foundation for creating and connecting MCP servers to Claude Desktop. Adapt it to your specific needs and requirements.