#!/usr/bin/env python3
"""
Fix Claude Desktop Configuration

This script directly modifies the Claude Desktop configuration to add the file-system-tools server.
"""

import os
import json
import sys
from pathlib import Path

def find_config():
    """Find the Claude Desktop configuration file"""
    possible_paths = [
        os.path.expanduser("~/AppData/Roaming/Claude Desktop/claude_desktop_config.json"),
        os.path.expanduser("~/AppData/Local/Claude Desktop/claude_desktop_config.json"),
        os.path.expanduser("~/AppData/Roaming/Anthropic/Claude Desktop/claude_desktop_config.json"),
        os.path.expanduser("~/AppData/Local/Anthropic/Claude Desktop/claude_desktop_config.json"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found config at: {path}")
            return path
    
    print("Could not find Claude Desktop configuration file.")
    return None

def update_config(config_path, project_dirs=None):
    """Update the Claude Desktop configuration"""
    if not config_path:
        return False
    
    # Read existing config
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        return False
    
    # Make sure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Get project directories
    project_dirs = project_dirs or []
    if not project_dirs:
        print("No project directories specified. Using current directory.")
        project_dirs = [os.getcwd()]
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the file-system-tools server
    filesystem_server_path = os.path.join(script_dir, "src", "mcp", "filesystem_server.py")
    if not os.path.exists(filesystem_server_path):
        print(f"WARNING: File system server not found at {filesystem_server_path}")
    
    # Create the file-system-tools server configuration
    config["mcpServers"]["file-system-tools"] = {
        "command": "python",
        "args": [
            filesystem_server_path
        ],
        "env": {
            "AI_DEV_TOOLKIT_ALLOWED_DIRS": ",".join(project_dirs),
            "AI_LIBRARIAN_ALLOWED_DIRS": ",".join(project_dirs)
        }
    }
    
    # Check for AI Librarian server and update it if it exists
    librarian_server_path = os.path.join(script_dir, "aitoolkit", "librarian", "server.py")
    if "ai-librarian" in config["mcpServers"]:
        print("Updating AI Librarian server configuration...")
        config["mcpServers"]["ai-librarian"] = {
            "command": "python",
            "args": [
                librarian_server_path
            ],
            "env": {
                "AI_LIBRARIAN_ALLOWED_DIRS": ",".join(project_dirs)
            }
        }
    
    # Write the updated config
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, indent=2, ensure_ascii=False, f)
        print("Successfully updated Claude Desktop configuration.")
        return True
    except Exception as e:
        print(f"Error writing config: {e}")
        return False

def main():
    """Main entry point"""
    print("Claude Desktop Configuration Fixer")
    
    # Find the config file
    config_path = find_config()
    if not config_path:
        print("Could not find Claude Desktop configuration file.")
        return 1
    
    # Get project directories
    project_dirs = []
    if len(sys.argv) > 1:
        project_dirs = sys.argv[1:]
    else:
        # Ask the user for directories
        print("Enter project directories (one per line, blank line to finish):")
        while True:
            dir_input = input("> ").strip()
            if not dir_input:
                break
            if os.path.exists(dir_input):
                project_dirs.append(os.path.abspath(dir_input))
            else:
                print(f"Directory does not exist: {dir_input}")
    
    # Update the config
    success = update_config(config_path, project_dirs)
    
    if success:
        print("\nConfiguration updated successfully!")
        print("\nEnabled servers:")
        print("- File System Tools")
        print("- AI Librarian (if it was already enabled)")
        print(f"\nProject directories ({len(project_dirs)}):")
        for dir_path in project_dirs:
            print(f"- {dir_path}")
        print("\nPlease restart Claude Desktop for changes to take effect.")
        return 0
    else:
        print("Failed to update configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
