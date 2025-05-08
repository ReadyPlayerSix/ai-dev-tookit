#!/usr/bin/env python3
"""
Launcher for the Integrated MCP Server

This script launches the integrated server that combines AI Librarian and
enhanced filesystem functionality in one package.
"""

import os
import sys
import argparse
from pathlib import Path


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Launch the Integrated MCP Server")
    
    # Allow specifying directories to monitor
    parser.add_argument(
        "directories", 
        nargs="*", 
        help="Directories to monitor (optional)"
    )
    
    # Optional name override
    parser.add_argument(
        "--name", 
        type=str, 
        default="AI Dev Toolkit",
        help="Server name to display in Claude"
    )
    
    # Optional version override
    parser.add_argument(
        "--version", 
        type=str, 
        default="0.3.0",
        help="Server version"
    )
    
    # Debug mode
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()
    
    # Set up environment for the directories if provided
    if args.directories:
        allowed_dirs = [os.path.abspath(d) for d in args.directories if os.path.exists(d)]
        if allowed_dirs:
            os.environ["AI_LIBRARIAN_ALLOWED_DIRS"] = ",".join(allowed_dirs)
            print(f"Monitoring directories: {', '.join(allowed_dirs)}")
    
    # Configure debug logging if requested
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        print("Debug logging enabled")
    
    # Import the server
    try:
        from aitoolkit.mcp.integrated_server import create_server
        
        # Create and run the server
        server = create_server()
        if args.name != "AI Dev Toolkit":
            server.mcp.name = args.name
        if args.version != "0.3.0":
            server.mcp.version = args.version
            
        print(f"Starting integrated server ({args.name} v{args.version})...")
        server.run()
    except ImportError as e:
        print(f"Error importing integrated server: {e}")
        print("Make sure you're running this script from the root directory of the project.")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
