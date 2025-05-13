#!/usr/bin/env python3
"""
Apply TaskBoard integration to AI Librarian server

This script directly integrates the TaskBoard system with the 
AI Librarian server without requiring a server restart.
Run this script to immediately enable TaskBoard functionality.
"""

import os
import sys
import importlib
import argparse
import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("apply_taskboard")

def get_server_context():
    """Import server module and get its context"""
    try:
        # Import directly from the server module
        from aitoolkit.librarian.server import initialize_server, librarian_context, mcp_tools, determine_mini_librarians
        
        # Construct server context dictionary
        server_context = {
            "librarian_context": librarian_context,
            "mcp_tools": mcp_tools,
            "determine_mini_librarians": determine_mini_librarians,
            "initialize_server": initialize_server,
            "project_path": librarian_context.get("project_path", "")
        }
        
        return server_context
    except ImportError as e:
        logger.error(f"Error importing server module: {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting server context: {e}")
        return None

def apply_taskboard(project_path=None):
    """Apply TaskBoard integration to the server"""
    try:
        # Get server context
        server_context = get_server_context()
        if not server_context:
            logger.error("Failed to get server context, cannot apply TaskBoard integration")
            return False
        
        # Use provided project path or get from context
        if project_path is None:
            project_path = server_context.get("project_path")
            if not project_path:
                logger.error("No project path provided and none found in server context")
                return False
                
        logger.info(f"Applying TaskBoard integration for project: {project_path}")
        
        # Import and apply TaskBoard integration
        from aitoolkit.librarian.server_taskboard_integration import apply_taskboard_integration
        apply_taskboard_integration(server_context)
        
        # Register TaskBoard tools directly in original mcp_tools
        from aitoolkit.librarian.taskboard_integration import register_taskboard_mcp_tools
        register_taskboard_mcp_tools(server_context)
        
        logger.info("TaskBoard integration applied successfully!")
        logger.info("New tools added: think, submit_background_task, get_task_status, get_task_result, cancel_task, list_tasks")
        
        return True
    except Exception as e:
        logger.error(f"Error applying TaskBoard integration: {e}", exc_info=True)
        return False

def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description="Apply TaskBoard integration to AI Librarian server")
    parser.add_argument("--project-path", help="Path to the project (optional if server is already initialized)")
    
    args = parser.parse_args()
    
    # Apply TaskBoard integration
    success = apply_taskboard(args.project_path)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())