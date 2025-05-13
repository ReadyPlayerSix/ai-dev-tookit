#!/usr/bin/env python3
"""
Install TaskBoard System to Claude Desktop

This script updates the Claude Desktop configuration to use
the TaskBoard-enabled version of the AI Librarian server.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("install_taskboard")

def install_taskboard_to_claude():
    """Install the TaskBoard-enabled server to Claude Desktop"""
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
        logger.error(f"Unsupported platform: {os.name}")
        return False
    
    # Ensure config directory exists
    if not config_dir.exists():
        logger.error(f"Claude Desktop config directory not found: {config_dir}")
        return False
    
    # Path to Claude Desktop config file
    config_file = config_dir / "claude_desktop_config.json"
    
    # Create or update config
    if not config_file.exists():
        logger.error(f"Claude Desktop config file not found: {config_file}")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Error reading config file: {e}")
        return False
    
    # Check if AI Librarian server is configured
    if "mcpServers" not in config or "ai-librarian" not in config["mcpServers"]:
        logger.error("AI Librarian server not found in Claude Desktop config")
        return False
    
    # Get the current AI Librarian server config
    librarian_config = config["mcpServers"]["ai-librarian"]
    
    # Find our server file
    server_args = librarian_config.get("args", [])
    if not server_args:
        logger.error("No server path found in AI Librarian config")
        return False
    
    # Get the server path
    server_path = server_args[0]
    server_dir = os.path.dirname(os.path.dirname(os.path.dirname(server_path)))
    
    # Create the TaskBoard initialization script path
    taskboard_script = os.path.join(server_dir, "scripts", "apply_taskboard_to_claude.py")
    
    logger.info(f"Project directory: {server_dir}")
    logger.info(f"TaskBoard initialization script: {taskboard_script}")
    
    if not os.path.exists(taskboard_script):
        logger.error(f"TaskBoard initialization script not found: {taskboard_script}")
        return False
    
    # Update the server command to use the apply_taskboard_to_claude.py script
    config["mcpServers"]["ai-librarian-taskboard"] = {
        "command": librarian_config.get("command", "python"),
        "args": [
            # First argument: include the modified server path
            taskboard_script
        ],
        "env": librarian_config.get("env", {})
    }
    
    # Save the updated config
    try:
        logger.info("Saving updated Claude Desktop config")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving config file: {e}")
        return False
    
    logger.info("TaskBoard system installed to Claude Desktop")
    logger.info("Please restart Claude Desktop to apply changes")
    
    # Additional instructions
    print("\n===================================================")
    print("TaskBoard System Installation Complete!")
    print("===================================================")
    print("\nTo use the TaskBoard system:")
    print("1. Restart Claude Desktop")
    print("2. Try using the 'think' tool: think(\"How does the authentication system work?\")")
    print("\nOther available tools:")
    print("- submit_background_task: Submit a task to be processed asynchronously")
    print("- get_task_status: Check the status of a task")
    print("- get_task_result: Get the result of a completed task")
    print("- cancel_task: Cancel a pending task")
    print("- list_tasks: List all tasks with filtering options")
    print("\nThe TaskBoard system allows long-running operations to be processed")
    print("in the background without causing timeouts.")
    
    return True

if __name__ == "__main__":
    install_taskboard_to_claude()