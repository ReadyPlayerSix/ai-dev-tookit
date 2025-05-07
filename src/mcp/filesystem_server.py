"""
FileSystem Tools MCP Server

This is a standalone MCP server that provides comprehensive filesystem operations,
designed to work alongside the AI Librarian but with a focused purpose.
"""
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import os
import sys

from mcp.server.fastmcp import FastMCP

# Import our filesystem module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from librarian.filesystem import register_filesystem_tools


def get_allowed_directories() -> list[str]:
    """Returns the allowed directories."""
    # Read from environment variable if set
    env_dirs = os.environ.get("AI_DEV_TOOLKIT_ALLOWED_DIRS", "")
    
    if env_dirs:
        return [d.strip() for d in env_dirs.split(",") if d.strip()]
    
    # Check command line arguments
    if len(sys.argv) > 1:
        return [os.path.abspath(arg) for arg in sys.argv[1:] if os.path.exists(arg)]
    
    # Fallback to current directory if nothing else is specified
    return [os.getcwd()]


# Create the MCP server
mcp = FastMCP("file-system-tools", version="0.1.0")

# Register filesystem tools with the MCP server
register_filesystem_tools(mcp)

# Direct tool for listing allowed directories
@mcp.tool()
def list_allowed_directories() -> List[str]:
    """
    Returns the list of directories that this server is allowed to access.
    
    Returns:
        A list of allowed directory paths
    """
    return get_allowed_directories()


if __name__ == "__main__":
    # If this module is run directly, start the server
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="FileSystem Tools MCP Server")
    parser.add_argument("--allowed-directories", type=str, help="Comma-separated list of allowed directories")
    parser.add_argument("directories", nargs="*", help="Directories to allow access to")
    args = parser.parse_args()
    
    # Process allowed directories from command line
    if args.allowed_directories:
        allowed_dirs = [dir.strip() for dir in args.allowed_directories.split(",") if dir.strip()]
        # Set environment variable for get_allowed_directories() to use
        os.environ["AI_DEV_TOOLKIT_ALLOWED_DIRS"] = ",".join(allowed_dirs)
        print(f"Using allowed directories from --allowed-directories flag: {allowed_dirs}")
    elif args.directories:
        # Set environment variable based on positional arguments
        allowed_dirs = [os.path.abspath(dir) for dir in args.directories if os.path.exists(dir)]
        os.environ["AI_DEV_TOOLKIT_ALLOWED_DIRS"] = ",".join(allowed_dirs)
        print(f"Using allowed directories from positional arguments: {allowed_dirs}")
    
    # Show the actual directories that will be used
    print(f"Allowed directories: {get_allowed_directories()}")
    
    # Run the server
    mcp.run()
