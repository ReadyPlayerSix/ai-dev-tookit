#!/usr/bin/env python3
"""
Install AI Dev Toolkit Unified Server to Claude Desktop

This script installs the unified server to Claude Desktop,
combining AI Librarian and File System tools in one server.
"""

import os
import sys
import json
import shutil
from pathlib import Path


def find_config_file():
    """Find the Claude Desktop configuration file"""
    # Common locations for Claude Desktop config file
    possible_paths = [
        # Current paths for latest Claude Desktop versions
        os.path.expanduser("~/AppData/Roaming/Claude Desktop/claude_desktop_config.json"),
        os.path.expanduser("~/AppData/Roaming/Claude Desktop/config.json"),
        os.path.expanduser("~/AppData/Local/Claude Desktop/claude_desktop_config.json"),
        os.path.expanduser("~/AppData/Local/Claude Desktop/config.json"),
        os.path.expanduser("~/AppData/Local/Programs/Claude Desktop/claude_desktop_config.json"),
        # Anthropic branded paths
        os.path.expanduser("~/AppData/Roaming/Anthropic/Claude Desktop/claude_desktop_config.json"),
        os.path.expanduser("~/AppData/Roaming/Anthropic/Claude Desktop/config.json"),
        os.path.expanduser("~/AppData/Local/Anthropic/Claude Desktop/claude_desktop_config.json"),
        # Legacy paths
        os.path.expanduser("~/AppData/Roaming/Claude/claude_desktop_config.json"),
        os.path.expanduser("~/AppData/Local/Claude/claude_desktop_config.json"),
        os.path.expanduser("~/AppData/Local/Programs/Claude/claude_desktop_config.json"),
        os.path.expanduser("~/AppData/Roaming/Claude/config.json"),
        # macOS paths
        os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json"),
        os.path.expanduser("~/Library/Application Support/Claude Desktop/claude_desktop_config.json"),
        os.path.expanduser("~/Library/Application Support/Anthropic/Claude Desktop/claude_desktop_config.json"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None


def install_to_claude_desktop():
    """Install the AI Dev Toolkit Unified Server to Claude Desktop"""
    # Find the config file
    config_file = find_config_file()
    if not config_file:
        print("❌ Could not find Claude Desktop configuration file.")
        print("Please make sure Claude Desktop is installed.")
        return False
    
    print(f"Using config file: {config_file}")
    
    # Read the current config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        return False
    
    # Create a backup of the config file
    backup_path = config_file + ".bak"
    try:
        shutil.copy2(config_file, backup_path)
        print(f"✅ Created backup of config file at {backup_path}")
    except Exception as e:
        print(f"⚠️ Warning: Could not create backup of config file: {e}")
    
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    
    # Get allowed directories from user
    print("\nAI Dev Toolkit Unified Server Installation")
    print("=========================================")
    print("\nThis will install the Unified Server to Claude Desktop.")
    print("The server needs access to your project directories.")
    
    # Default to the current directory
    default_dirs = [str(current_dir)]
    
    # Ask for additional directories
    print(f"\nDefault directory: {current_dir}")
    add_more = input("Do you want to add more directories? (y/n): ").lower() == 'y'
    
    additional_dirs = []
    while add_more:
        dir_path = input("Enter directory path (or leave empty to finish): ")
        if not dir_path:
            break
            
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            additional_dirs.append(str(path))
            print(f"Added: {path}")
        else:
            print(f"Directory not found: {path}")
        
        add_more = input("Add another directory? (y/n): ").lower() == 'y'
    
    # Combine all directories
    all_dirs = default_dirs + additional_dirs
    
    # Set up the MCP servers configuration
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Remove any existing AI Librarian and File System servers
    for server_name in ["ai-librarian", "file-system-tools", "ai-dev-toolkit"]:
        if server_name in config["mcpServers"]:
            print(f"Removing existing server: {server_name}")
            del config["mcpServers"][server_name]
    
    # Configure the unified server
    config["mcpServers"]["ai-dev-toolkit"] = {
        "command": sys.executable,
        "args": [str(current_dir / "launch_unified.py")],
        "env": {
            "AI_LIBRARIAN_ALLOWED_DIRS": ",".join(all_dirs)
        }
    }
    
    # Save the updated config
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Successfully installed AI Dev Toolkit Unified Server")
        print(f"Configuration saved to: {config_file}")
        print("\nAllowed directories:")
        for dir_path in all_dirs:
            print(f"- {dir_path}")
        
        print("\nPlease restart Claude Desktop to apply changes")
        return True
    except Exception as e:
        print(f"❌ Error saving config file: {e}")
        # Try to restore from backup
        if os.path.exists(backup_path):
            try:
                shutil.copy2(backup_path, config_file)
                print(f"Restored config file from backup")
            except:
                print(f"Could not restore config file from backup")
        return False


if __name__ == "__main__":
    install_to_claude_desktop()
