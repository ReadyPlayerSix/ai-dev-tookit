"""
MCP Server Integration for AI Librarian

This file integrates both the AI-optimized todo system and filesystem capabilities
into a single MCP server for the AI Librarian, replacing the need for a separate
filesystem MCP server.
"""
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import os
import asyncio
import json
import sys

from mcp.server.fastmcp import FastMCP, Context

# Import our internal modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from librarian.filesystem import register_filesystem_tools
from librarian.ai_task_system import (
    add_ai_task, list_ai_tasks, get_ai_task, 
    update_ai_task_status, add_subtask,
    update_subtask_status, infer_tasks, search_ai_tasks
)
from librarian.core import (
    initialize_librarian_tool,
    generate_librarian,
    query_component,
    find_implementation
)


class AILibrarianServer:
    """MCP Server for AI Librarian with integrated filesystem capabilities"""
    
    def __init__(self, name: str = "AI Librarian", version: str = "0.2.0"):
        """
        Initialize the AI Librarian MCP server.
        
        Args:
            name: Server name
            version: Server version
        """
        self.mcp = FastMCP(name, version=version)
        self.register_tools()
    
    def register_tools(self):
        """Register all tools with the MCP server"""
        # Register librarian core tools
        self.mcp.tool()(initialize_librarian_tool)
        self.mcp.tool()(generate_librarian)
        self.mcp.tool()(query_component)
        self.mcp.tool()(find_implementation)
        
        # Register AI task tools
        self.mcp.tool()(add_ai_task)
        self.mcp.tool()(list_ai_tasks)
        self.mcp.tool()(get_ai_task)
        self.mcp.tool()(update_ai_task_status)
        self.mcp.tool()(add_subtask)
        self.mcp.tool()(update_subtask_status)
        self.mcp.tool()(infer_tasks)
        self.mcp.tool()(search_ai_tasks)
        
        # Register filesystem tools
        register_filesystem_tools(self.mcp)
    
    def run(self):
        """Run the MCP server"""
        self.mcp.run()


def create_server():
    """Create and return an AI Librarian MCP server instance"""
    return AILibrarianServer()


if __name__ == "__main__":
    # If this module is run directly, start the server
    server = create_server()
    server.run()
