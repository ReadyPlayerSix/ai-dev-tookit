#!/usr/bin/env python3
"""
AI Dev Toolkit Unified Server Launcher

This script launches the unified server that combines AI Librarian and
filesystem functionality in one MCP server.

Usage:
    python launch_unified_server.py [project_dir1] [project_dir2] ...
"""

import os
import sys
import subprocess
import logging
import importlib.util
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("unified_server_launcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("unified-launcher")

def check_requirements():
    """Check if required packages are installed and install them if needed."""
    # Check if mcp is installed
    if importlib.util.find_spec("mcp") is None:
        logger.info("Installing MCP package...")
        print("Installing required dependencies...")        
        try:
            # Try using uv first as recommended
            result = subprocess.run([sys.executable, "-m", "uv", "pip", "install", "mcp[cli]>=0.1.5"], 
                                   check=False, capture_output=True, text=True)
            if result.returncode != 0:
                # Fall back to pip if uv fails
                subprocess.run([sys.executable, "-m", "pip", "install", "mcp[cli]>=0.1.5"], check=True)
        except Exception as e:
            logger.error(f"Failed to install requirements: {str(e)}")
            print(f"Error installing requirements: {str(e)}")
            print("Please install them manually: pip install 'mcp[cli]>=0.1.5'")
            sys.exit(1)
        logger.info("Successfully installed MCP package")
        print("Dependencies installed successfully!")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Launch the Unified MCP Server")
    
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
    """Start the unified server with the specified directories."""
    # Parse command line arguments
    args = parse_args()
    
    # Check and install requirements first
    check_requirements()
    
    # Get the path to the server script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(script_dir, "aitoolkit", "unified_server.py")
    
    # Add the project directory to Python path so imports work correctly
    sys.path.insert(0, script_dir)
    
    # Check if the server script exists
    if not os.path.exists(server_path):
        logger.error(f"Server script not found at {server_path}")
        print(f"Error: Server script not found at {server_path}")
        sys.exit(1)
    
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
        logging.getLogger().setLevel(logging.DEBUG)
        print("Debug logging enabled")
        
    # Log the command
    logger.info(f"Starting unified server with command: {' '.join(cmd)}")
    
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
        # Use subprocess with more robust error handling
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        # Monitor the output in real-time
        print("Server running - press Ctrl+C to stop")
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())
                logger.info(output.strip())
            
            error = process.stderr.readline()
            if error:
                print(f"ERROR: {error.strip()}", file=sys.stderr)
                logger.error(error.strip())
            
            # Check if process has exited
            if process.poll() is not None:
                break
                
        # Get any remaining output
        remaining_out, remaining_err = process.communicate()
        if remaining_out:
            print(remaining_out.strip())
            logger.info(remaining_out.strip())
        if remaining_err:
            print(f"ERROR: {remaining_err.strip()}", file=sys.stderr) 
            logger.error(remaining_err.strip())
            
        # Check exit code
        if process.returncode != 0:
            logger.error(f"Server exited with error code {process.returncode}")
            print(f"Server failed with exit code {process.returncode}")
            sys.exit(process.returncode)
            
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        print("\nServer stopped by user")
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            process.wait(timeout=5)  # Wait for process to terminate
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
