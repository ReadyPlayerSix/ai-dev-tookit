"""
MCP Connector Module

This module provides compatibility classes for connecting with the MCP protocol.
It serves as a backup when the official MCP package isn't available.

The module also includes enhanced MCP protocol timeout settings to prevent
connection issues in Claude Desktop.
"""

# Configure MCP timeouts
import os
import sys

# Set default MCP protocol timeouts (in milliseconds)
# Override default timeout of 30000ms (30s)
os.environ["MCP_DEFAULT_TIMEOUT"] = "300000"  # 5 minutes
os.environ["MCP_MAX_REQUEST_TIMEOUT"] = "600000"  # 10 minutes
os.environ["MCP_INITIALIZATION_TIMEOUT"] = "1200000"  # 20 minutes
os.environ["MCP_LAZY_LOADING"] = "true"  # Enable lazy loading features
os.environ["MCP_REDUCED_TOOLS"] = "true"  # Enable reduced tool set initially
os.environ["MCP_DEBUG"] = "true"  # Enable additional debug logging

# Ensure stderr has proper flush behavior
sys.stderr.reconfigure(line_buffering=True)

import os
import sys
import logging
import inspect
from typing import Dict, Any, Callable, List, Optional, Union, Set, Tuple

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Context class for MCP
class Context:
    """Context object providing access to request info and helper methods."""
    
    def __init__(self, request_context=None):
        self.request_context = request_context or {}
        
    def info(self, message):
        """Log an informational message."""
        logger.info(message)
        
    def warning(self, message):
        """Log a warning message."""
        logger.warning(message)
        
    def error(self, message):
        """Log an error message."""
        logger.error(message)
        
    async def report_progress(self, current, total):
        """Report progress on a long-running operation."""
        logger.info(f"Progress: {current}/{total}")
        
    async def read_resource(self, resource_uri):
        """Read a resource by URI."""
        logger.info(f"Reading resource: {resource_uri}")
        return None, None

# FastMCP class that provides a simplified interface
class FastMCP:
    """
    Simple implementation of FastMCP that can be used as a fallback
    when the real MCP package isn't available.
    """
    
    def __init__(self, name, capabilities=None, dependencies=None, lifespan=None):
        self.name = name
        self.capabilities = capabilities or {}
        self.dependencies = dependencies or []
        self.lifespan = lifespan
        self.tools = {}
        self.resources = {}
        self.prompts = {}
        
    def tool(self, **kwargs):
        """Decorator for registering a tool."""
        def decorator(func):
            name = kwargs.get('name', func.__name__)
            self.tools[name] = {
                'func': func,
                'kwargs': kwargs,
                'signature': inspect.signature(func)
            }
            return func
        return decorator
        
    def resource(self, pattern):
        """Decorator for registering a resource."""
        def decorator(func):
            self.resources[pattern] = {
                'func': func,
                'signature': inspect.signature(func)
            }
            return func
        return decorator
        
    def prompt(self, **kwargs):
        """Decorator for registering a prompt."""
        def decorator(func):
            name = kwargs.get('name', func.__name__)
            self.prompts[name] = {
                'func': func,
                'kwargs': kwargs,
                'signature': inspect.signature(func)
            }
            return func
        return decorator

    def run(self):
        """Run the MCP server."""
        logger.info(f"Starting MCP server: {self.name}")
        logger.warning("This is a fallback implementation. It won't actually handle connections.")
        
    def sse_app(self):
        """Return an ASGI app for SSE transport."""
        async def app(scope, receive, send):
            await send({
                'type': 'http.response.start',
                'status': 200,
                'headers': [
                    [b'content-type', b'text/plain'],
                ],
            })
            await send({
                'type': 'http.response.body',
                'body': b'MCP connector fallback',
            })
        return app

# Attempt to import the real MCP classes
try:
    from mcp.server.fastmcp import FastMCP as RealFastMCP, Context as RealContext
    # If we successfully imported the real classes, use them instead
    FastMCP = RealFastMCP
    Context = RealContext
    logger.info("Using actual MCP package classes")
except ImportError:
    logger.warning("Using fallback MCP connector classes")
