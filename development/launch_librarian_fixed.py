#!/usr/bin/env python3
"""
Launch the AI Librarian Server

This script launches the standalone AI Librarian server,
allowing it to be used with Claude Desktop.

Usage:
    python launch_librarian_fixed.py [directories...]
    
Each directory provided as an argument will be monitored for changes
and added to the AI Librarian's allowed directories.
"""

import os
import sys
import logging
from importlib import import_module

# Add the parent directory to the path to ensure aitoolkit can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def main():
    try:
        # Configure console logging 
        root_logger = logging.getLogger()
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
        
        # Log startup information
        logging.info("Starting AI Librarian server...")
        logging.info(f"Allowed directories: {sys.argv[1:] or [os.getcwd()]}")
        
        # Check if FastMCP is available locally
        try:
            # Try to load the server directly
            from aitoolkit.librarian.server import mcp
            logging.info("Server module loaded successfully")
            
            # Run the server
            mcp.run()
            
        except ImportError as e:
            if "FastMCP" in str(e) or "mcp" in str(e):
                print("The MCP package is not installed. You can mock the server for development:")
                print("\n1. Create a simple mock server:")
                print("   - Edit aitoolkit/librarian/server.py")
                print("   - Replace FastMCP import with a mock implementation")
                print("\n2. If you need the actual MCP package:")
                print("   - Install it with: pip install mcp[cli]")
                print("   - Or check the project documentation for setup instructions")
                
                return 1
            else:
                # Rethrow other import errors
                raise
                
    except ImportError as e:
        print(f"Error loading AI Librarian server: {e}")
        print("Please ensure AI Dev Toolkit is correctly installed.")
        return 1
    except Exception as e:
        print(f"Error starting AI Librarian server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())