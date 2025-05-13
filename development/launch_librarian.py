#!/usr/bin/env python3
"""
Launch the AI Librarian Server

This script launches the standalone AI Librarian server,
allowing it to be used with Claude Desktop.

Usage:
    python launch_librarian.py [directories...]
    
Each directory provided as an argument will be monitored for changes
and added to the AI Librarian's allowed directories.
"""

import os
import sys
import logging
from importlib import import_module

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    try:
        # Configure console logging first
        root_logger = logging.getLogger()
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
        
        # Log startup information
        logging.info("Starting AI Librarian server...")
        logging.info(f"Allowed directories: {sys.argv[1:] or [os.getcwd()]}")
        
        # Check if MCP is installed before attempting to import
        try:
            import mcp
            logging.info(f"Found MCP package version {mcp.__version__}")
            # Check if we can import FastMCP
            from mcp.server.fastmcp import FastMCP
            mcp_available = True
        except ImportError:
            logging.warning("MCP package not found.")
            logging.warning("Running in limited functionality mode without Claude Desktop connection.")
            print("")
            print("============================================================")
            print("WARNING: MCP package not installed.")
            print("The server will run without Claude Desktop connectivity.")
            print("")
            print("To install MCP, run:")
            print("python scripts/install_mcp_dependencies.py [--venv]")
            print("============================================================")
            print("")
            mcp_available = False
        
        # Attempt to directly load the server module
        from aitoolkit.librarian.server import mcp
        
        # Log MCP availability
        if mcp_available:
            logging.info("MCP available - Claude Desktop connection enabled")
        else:
            logging.warning("MCP not available - Claude Desktop connection disabled")
        
        # Run the server
        mcp.run()
        
    except ImportError as e:
        print(f"Error loading AI Librarian server: {e}")
        print("Please ensure AI Dev Toolkit is correctly installed.")
        print("You can install the toolkit with: pip install -e .")
        return 1
    except Exception as e:
        print(f"Error starting AI Librarian server: {e}")
        import traceback
        print(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
