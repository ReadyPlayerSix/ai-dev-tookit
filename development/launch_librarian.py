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

def main():
    try:
        # Attempt to directly load the server module
        from aitoolkit.librarian.server import mcp
        
        # Configure console logging 
        root_logger = logging.getLogger()
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
        
        # Log startup information
        logging.info("Starting AI Librarian server...")
        logging.info(f"Allowed directories: {sys.argv[1:] or [os.getcwd()]}")
        
        # Run the server
        mcp.run()
        
    except ImportError as e:
        print(f"Error loading AI Librarian server: {e}")
        print("Please ensure AI Dev Toolkit is correctly installed.")
        return 1
    except Exception as e:
        print(f"Error starting AI Librarian server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
