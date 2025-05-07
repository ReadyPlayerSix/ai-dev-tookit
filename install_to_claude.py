#!/usr/bin/env python
"""
Installation script for AI Librarian MCP server with Claude Desktop
"""
import os
import json
import shutil
from pathlib import Path


def install_to_claude_desktop():
    """Install the AI Librarian MCP server to Claude Desktop"""
    # Determine Claude Desktop config path based on platform
    home = Path.home()
    
    if os.name == 'nt':  # Windows
        config_dir = home / "AppData" / "Roaming" / "Claude"
    elif os.name == 'posix':  # macOS/Linux
        if os.path.exists(home / "Library" / "Application Support" / "Claude"):  # macOS
            config_dir = home / "Library" / "Application Support" / "Claude"
        else:  # Linux
            config_dir = home / ".config" / "Claude"
    else:
        print(f"Unsupported platform: {os.name}")
        return False
    
    # Ensure config directory exists
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Path to Claude Desktop config file
    config_file = config_dir / "claude_desktop_config.json"
    
    # Create or update config
    config = {}
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except:
            print(f"Warning: Could not read existing config file {config_file}")
    
    # Add or update AI Librarian server configuration
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    
    # Get allowed directories from user
    print("\nAI Librarian MCP Server Installation")
    print("====================================")
    print("\nThis will install the AI Librarian MCP server to Claude Desktop.")
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
    
    # Configure the server
    config["mcpServers"]["ai-librarian"] = {
        "command": "python",
        "args": ["-m", "ai_dev_toolkit.src.mcp.server"],
        "env": {
            "AI_LIBRARIAN_ALLOWED_DIRS": ",".join(all_dirs)
        }
    }
    
    # Save config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nSuccessfully installed AI Librarian MCP server to Claude Desktop")
    print(f"Configuration saved to: {config_file}")
    print("\nAllowed directories:")
    for dir_path in all_dirs:
        print(f"- {dir_path}")
    
    print("\nPlease restart Claude Desktop to apply changes")
    
    return True


if __name__ == "__main__":
    install_to_claude_desktop()
