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


class FileSystemToolsServer:
    """MCP Server providing comprehensive filesystem operations"""
    
    def __init__(self, name: str = "FileSystem Tools", version: str = "0.1.0"):
        """
        Initialize the FileSystem Tools MCP server.
        
        Args:
            name: Server name
            version: Server version
        """
        self.mcp = FastMCP(name, version=version)
        self.register_tools()
    
    def register_tools(self):
        """Register all filesystem tools with the MCP server"""
        # Register filesystem tools
        register_filesystem_tools(self.mcp)
    
    def run(self):
        """Run the MCP server"""
        self.mcp.run()


def create_server():
    """Create and return a FileSystem Tools server instance"""
    return FileSystemToolsServer()


if __name__ == "__main__":
    # If this module is run directly, start the server
    server = create_server()
    server.run()
