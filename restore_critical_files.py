#!/usr/bin/env python3
"""
Quick restoration script to bring back critical files that might have been removed.
This will restore files from the pre-cleanup tag that are needed for basic functionality.
"""

import os
import subprocess
import sys

# Files that are critical for basic functionality
CRITICAL_FILES = [
    "aitoolkit/mcp/connector.py",  # MCP connector for Claude Desktop
    "aitoolkit/librarian/server.py",  # Main server implementation
    "aitoolkit/mcp/integrated_server.py",  # MCP server integration
    "development/launch_librarian.py",  # Server launcher
    "scripts/launchers/run_server.bat",  # Windows launcher
    "scripts/launchers/run_server.sh",  # Unix launcher
]

def restore_file(file_path):
    """Restore a file from the pre-cleanup tag."""
    print(f"Attempting to restore {file_path}...")
    
    # Check if the file exists already
    if os.path.exists(file_path):
        print(f"File already exists: {file_path}")
        return True
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Restore from tag
    try:
        output = subprocess.check_output(
            ["git", "show", "v0.6.1-pre-cleanup:" + file_path], 
            stderr=subprocess.STDOUT
        )
        
        with open(file_path, "wb") as f:
            f.write(output)
            
        print(f"✅ Successfully restored {file_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to restore {file_path}: {e}")
        return False

def main():
    success_count = 0
    failure_count = 0
    
    print("Starting critical file restoration...")
    print(f"Using reference tag: v0.6.1-pre-cleanup")
    print("-" * 50)
    
    for file_path in CRITICAL_FILES:
        if restore_file(file_path):
            success_count += 1
        else:
            failure_count += 1
    
    print("-" * 50)
    print(f"Restoration complete: {success_count} files restored, {failure_count} failed")
    
    if failure_count > 0:
        print("\nIf restoration failed, you can manually restore by checking out files:")
        print("git checkout v0.6.1-pre-cleanup -- [filename]")
        
    print("\nTo restore all changes and undo the cleanup:")
    print("git reset --hard v0.6.1-pre-cleanup")
    
    return 0 if failure_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())