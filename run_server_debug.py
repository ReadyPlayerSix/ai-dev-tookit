#!/usr/bin/env python3
"""
Debug Server Launcher

This script runs the AI Librarian server with debug logging enabled
to help diagnose issues with tool registration.
"""

import os
import sys
import logging
import subprocess

def configure_logging():
    """Configure debug logging for the server."""
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Create console handler
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(message)s'))
    
    # Add handler to root logger
    root_logger.addHandler(console)
    
    return root_logger

def main():
    """Main function."""
    logger = configure_logging()
    logger.info("Starting AI Librarian server with debug logging")
    
    # Add the current directory to the Python path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # Import the server module
    try:
        from aitoolkit.librarian.server import mcp
        
        # Log all registered tools
        logger.info("Registered MCP tools:")
        tools = mcp._tools if hasattr(mcp, '_tools') else []
        for tool in tools:
            logger.info(f"- {tool.__name__}")
        
        # Log TaskBoard availability
        from aitoolkit.librarian.server import TASKBOARD_AVAILABLE
        logger.info(f"TaskBoard available: {TASKBOARD_AVAILABLE}")
        
        # Log registered tools and their docstrings
        logger.info("\nDetailed tool information:")
        for tool in tools:
            logger.info(f"Tool: {tool.__name__}")
            logger.info(f"Docstring: {tool.__doc__}")
            logger.info("-" * 50)
        
        # Run the server
        logger.info("Running MCP server...")
        mcp.run()
        
    except ImportError as e:
        logger.error(f"Error importing server module: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error running server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())