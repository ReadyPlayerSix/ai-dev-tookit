#!/usr/bin/env python3
"""
Install AI Dev Toolkit Unified Server to Claude Desktop

This script installs the unified server to Claude Desktop,
replacing any separate AI Librarian and File System servers.
"""

import os
import sys
import json
import argparse
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


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Install AI Dev Toolkit Unified Server to Claude Desktop")
    
    # Allow specifying directories to monitor
    parser.add_argument(
        "directories", 
        nargs="*", 
        help="Directories to monitor (optional)"
    )
    
    # Server name
    parser.add_argument(
        "--name", 
        type=str, 
        default="AI Dev Toolkit",
        help="Server name to display in Claude"
    )
    
    # Force reinstall
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force reinstallation even if already installed"
    )
    
    # Config file path
    parser.add_argument(
        "--config", 
        type=str,
        help="Path to Claude Desktop config file (auto-detected if not specified)"
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()
    
    # Find the config file
    config_file = args.config if args.config else find_config_file()
    if not config_file:
        print("❌ Could not find Claude Desktop configuration file.")
        print("Please specify the path manually with --config.")
        sys.exit(1)
    
    print(f"Using config file: {config_file}")
    
    # Read the current config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        sys.exit(1)
    
    # Check if the unified server is already installed
    server_name = "ai-dev-toolkit"
    if "mcpServers" in config and server_name in config["mcpServers"] and not args.force:
        print("✅ AI Dev Toolkit Unified Server is already installed.")
        print("Use --force to reinstall.")
        return
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Get the allowed directories
    allowed_dirs = []
    for dir_path in args.directories:
        abs_path = os.path.abspath(dir_path)
        if os.path.exists(abs_path) and os.path.isdir(abs_path):
            allowed_dirs.append(abs_path)
    
    # Prepare the environment variables
    env_vars = {}
    if allowed_dirs:
        env_vars["AI_LIBRARIAN_ALLOWED_DIRS"] = ",".join(allowed_dirs)
    
    # Create the server configuration
    server_config = {
        "command": sys.executable,
        "args": [
            os.path.join(project_root, "launch_unified_server.py"),
            "--name", args.name
        ],
        "env": env_vars
    }
    
    # Add directories to args if provided
    if allowed_dirs:
        server_config["args"].extend(allowed_dirs)
    
    # Update the config
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Check for existing AI Librarian and File System servers to remove
    removed_servers = []
    for old_server in ["ai-librarian", "file-system-tools"]:
        if old_server in config["mcpServers"]:
            removed_servers.append(old_server)
            del config["mcpServers"][old_server]
    
    # Add the unified server
    config["mcpServers"][server_name] = server_config
    
    # Save the updated config
    try:
        # Create a backup of the config file
        backup_path = config_file + ".bak"
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        # Write the updated config
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Successfully installed AI Dev Toolkit Unified Server as '{server_name}'.")
        if removed_servers:
            print(f"Removed old servers: {', '.join(removed_servers)}")
        if allowed_dirs:
            print(f"Monitoring directories: {', '.join(allowed_dirs)}")
        print("Please restart Claude Desktop for the changes to take effect.")
        
        # Additional steps for success
        print("\nTo use the AI Dev Toolkit in Claude Desktop:")
        print("1. Restart Claude Desktop")
        print("2. Start a new conversation")
        print("3. Use tools like `initialize_librarian()` to set up a project")
        print("   or `list_directory()` to explore files")
    except Exception as e:
        print(f"❌ Error saving config file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
