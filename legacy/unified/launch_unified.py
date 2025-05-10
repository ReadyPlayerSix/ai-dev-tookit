#!/usr/bin/env python3
"""
AI Dev Toolkit Unified Server Launcher

This script launches the unified server that combines AI Librarian and
filesystem functionality in one MCP server.

Usage:
    python launch_unified.py [project_dir1] [project_dir2] ...
"""

import os
import sys
import subprocess
import argparse

def main():
    """Launch the AI Dev Toolkit Unified Server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Launch the Unified MCP Server")
    
    # Allow specifying directories to monitor
    parser.add_argument(
        "directories", 
        nargs="*", 
        help="Directories to monitor (optional)"
    )
    
    # Debug mode
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Get the path to the server script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "aitoolkit", "unified_server.py")
    
    # Check if the server script exists
    if not os.path.exists(server_path):
        print(f"Error: Server script not found at {server_path}")
        return 1
    
    # Prepare command to run the server
    cmd = [sys.executable, server_path]
    
    # Add any directory arguments
    if args.directories:
        cmd.extend(args.directories)
        
    # Set up environment for the directories if provided
    if args.directories:
        allowed_dirs = [os.path.abspath(d) for d in args.directories if os.path.exists(d)]
        if allowed_dirs:
            os.environ["AI_LIBRARIAN_ALLOWED_DIRS"] = ",".join(allowed_dirs)
            print(f"Monitoring directories: {', '.join(allowed_dirs)}")
    
    # Configure debug logging if requested
    if args.debug:
        os.environ["DEBUG"] = "1"
        print("Debug logging enabled")
        
    # Print startup message
    print("=" * 80)
    print("Starting AI Dev Toolkit Unified Server")
    print("=" * 80)
    print(f"Server script: {server_path}")
    if args.directories:
        print(f"Watching directories: {', '.join(args.directories)}")
    else:
        print("No specific directories specified - will use current directory as default")
    print("=" * 80)
    
    # Start the server
    try:
        print("Starting unified server...")
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
