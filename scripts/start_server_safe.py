#!/usr/bin/env python3
"""
Start the AI Librarian server with timeout prevention
"""

import os
import sys
import subprocess

# Set environment variables to prevent timeouts
env = os.environ.copy()
env.update({
    "MCP_DEFAULT_TIMEOUT": "300000",  # 5 minutes
    "MCP_MAX_REQUEST_TIMEOUT": "600000",  # 10 minutes
    "MCP_INITIALIZATION_TIMEOUT": "900000",  # 15 minutes
    "MCP_HEARTBEAT_INTERVAL": "10000",  # 10 seconds
    "PYTHONUNBUFFERED": "1"  # Unbuffered output
})

# Find the server script
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
server_script = os.path.join(project_root, "development", "launch_librarian.py")

if not os.path.exists(server_script):
    print(f"Error: Server script not found at {server_script}")
    sys.exit(1)

# Get allowed directories from command line
allowed_dirs = sys.argv[1:] if len(sys.argv) > 1 else [project_root]

print("Starting AI Librarian server with timeout prevention...")
print(f"Allowed directories: {allowed_dirs}")
print("\nPress Ctrl+C to stop the server")

try:
    # Start the server with the modified environment
    cmd = [sys.executable, server_script] + allowed_dirs
    subprocess.run(cmd, env=env)
except KeyboardInterrupt:
    print("\nShutting down server...")
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)