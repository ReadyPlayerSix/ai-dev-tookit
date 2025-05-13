#!/usr/bin/env python3
"""
Apply TaskBoard integration to Claude Desktop

This script applies TaskBoard integration to a running Claude Desktop
instance without requiring a server restart. It modifies the server
context directly to add the TaskBoard functionality.
"""

import os
import sys
import json
import logging
import argparse
import importlib.util
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("apply_taskboard_claude")

def get_project_root():
    """Get the project root directory"""
    # Start with the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up one level to get project root
    project_root = os.path.dirname(current_dir)
    
    return project_root

def import_apply_taskboard(project_root):
    """Import the apply_taskboard module"""
    try:
        # Construct path to apply_taskboard.py
        apply_taskboard_path = os.path.join(
            project_root, "aitoolkit", "librarian", "apply_taskboard.py"
        )
        
        # Ensure the file exists
        if not os.path.exists(apply_taskboard_path):
            logger.error(f"apply_taskboard.py not found at {apply_taskboard_path}")
            return None
        
        # Import the module from file path
        spec = importlib.util.spec_from_file_location(
            "apply_taskboard", apply_taskboard_path
        )
        apply_taskboard_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(apply_taskboard_module)
        
        return apply_taskboard_module
    except Exception as e:
        logger.error(f"Error importing apply_taskboard module: {e}", exc_info=True)
        return None

def apply_taskboard_to_claude(project_path=None):
    """Apply TaskBoard integration to Claude Desktop"""
    try:
        # Get project root
        project_root = get_project_root()
        logger.info(f"Project root: {project_root}")
        
        # Import apply_taskboard module
        apply_taskboard_module = import_apply_taskboard(project_root)
        if not apply_taskboard_module:
            return False
        
        # If no project path provided, try to get from environment
        if not project_path:
            # Find all AI Librarian allowed directories
            claude_config_paths = [
                # Windows
                os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Claude", "claude_desktop_config.json"),
                # macOS
                os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Claude", "claude_desktop_config.json"),
                # Linux
                os.path.join(os.path.expanduser("~"), ".config", "Claude", "claude_desktop_config.json")
            ]
            
            # Try to find and read Claude Desktop config
            for config_path in claude_config_paths:
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                            
                        # Check for AI Librarian server config
                        if "mcpServers" in config and "ai-librarian" in config["mcpServers"]:
                            server_config = config["mcpServers"]["ai-librarian"]
                            
                            # Get allowed directories from environment
                            if "env" in server_config and "AI_LIBRARIAN_ALLOWED_DIRS" in server_config["env"]:
                                allowed_dirs = server_config["env"]["AI_LIBRARIAN_ALLOWED_DIRS"].split(",")
                                
                                # Use first allowed directory as project path
                                if allowed_dirs and allowed_dirs[0]:
                                    project_path = allowed_dirs[0]
                                    logger.info(f"Using project path from Claude Desktop config: {project_path}")
                                    break
                    except Exception as e:
                        logger.warning(f"Error reading Claude Desktop config at {config_path}: {e}")
        
        # If still no project path, use project root
        if not project_path:
            project_path = project_root
            logger.info(f"No project path found in Claude Desktop config, using project root: {project_path}")
        
        # Apply TaskBoard integration
        result = apply_taskboard_module.apply_taskboard(project_path)
        
        if result:
            logger.info("TaskBoard successfully applied to Claude Desktop!")
            logger.info("New tools available:")
            logger.info("  - think: Start deep analysis tasks")
            logger.info("  - submit_background_task: Submit custom background tasks")
            logger.info("  - get_task_status: Check task status")
            logger.info("  - get_task_result: Get completed task results")
            logger.info("  - cancel_task: Cancel pending tasks")
            logger.info("  - list_tasks: List all tasks")
            
            # Give user instructions on what to do next
            logger.info("\nTo use the new tools in Claude Desktop:")
            logger.info("1. Go to Claude Desktop and send a message to reset the connection")
            logger.info("2. Try out the Think Tool with: think(\"How does the authentication system work in this project?\")")
            
            return True
        else:
            logger.error("Failed to apply TaskBoard integration")
            return False
            
    except Exception as e:
        logger.error(f"Error applying TaskBoard to Claude Desktop: {e}", exc_info=True)
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Apply TaskBoard integration to Claude Desktop")
    parser.add_argument("--project-path", help="Path to the project (optional)")
    
    args = parser.parse_args()
    
    # Apply TaskBoard integration
    success = apply_taskboard_to_claude(args.project_path)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())