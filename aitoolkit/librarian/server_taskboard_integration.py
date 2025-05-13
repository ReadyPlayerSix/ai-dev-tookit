#!/usr/bin/env python3
"""
Server integration patch for TaskBoard system

This module contains the integration code to connect the TaskBoard system
to the existing AI Librarian server. You can apply this integration by 
importing and calling the apply_taskboard_integration function.
"""

import logging
from typing import Dict, Any

# Configure logger
logger = logging.getLogger("ai_librarian.server_taskboard_integration")

def apply_taskboard_integration(server_context: Dict[str, Any]) -> None:
    """
    Apply TaskBoard integration to the server context
    
    Args:
        server_context: The server context dictionary
    """
    try:
        logger.info("Applying TaskBoard integration to server...")
        
        # Import the TaskBoard integration module
        from .taskboard_integration import initialize_taskboard
        
        # Get project path from context
        if "project_path" not in server_context:
            logger.error("Cannot integrate TaskBoard: project_path not found in server context")
            return
            
        project_path = server_context["project_path"]
        
        # Initialize TaskBoard with the server context
        initialize_taskboard(project_path, server_context)
        
        # Update server's determine_mini_librarians function to use TaskBoard's registry
        if "determine_mini_librarians" in server_context:
            original_determine_mini_librarians = server_context["determine_mini_librarians"]
            
            # Create enhanced version that checks TaskBoard first
            def enhanced_determine_mini_librarians(task_type, task_params=None):
                # Import here to avoid circular imports
                from .taskboard_integration import get_mini_librarians_for_task
                
                # First try TaskBoard registry
                mini_librarians = get_mini_librarians_for_task(task_type)
                if mini_librarians:
                    return mini_librarians
                
                # Fall back to original function
                return original_determine_mini_librarians(task_type, task_params)
            
            # Replace the function in the server context
            server_context["determine_mini_librarians"] = enhanced_determine_mini_librarians
        
        # Update server's initialization to include TaskBoard initialization
        if "initialize_server" in server_context:
            original_initialize_server = server_context["initialize_server"]
            
            # Create enhanced version that initializes TaskBoard
            def enhanced_initialize_server(project_path, allowed_dirs=None):
                # First call original initialization
                result = original_initialize_server(project_path, allowed_dirs)
                
                # Then initialize TaskBoard
                from .taskboard_integration import initialize_taskboard
                initialize_taskboard(project_path, server_context)
                
                return result
            
            # Replace the function in the server context
            server_context["initialize_server"] = enhanced_initialize_server
        
        logger.info("TaskBoard integration applied successfully")
        
    except Exception as e:
        logger.error(f"Error applying TaskBoard integration: {str(e)}", exc_info=True)
        
def initialize_taskboard_server(project_path: str) -> None:
    """
    Initialize the TaskBoard for a project
    
    This function can be called directly to initialize the TaskBoard
    without modifying the server context.
    
    Args:
        project_path: Path to the project
    """
    try:
        # Import the TaskBoard integration module
        from .taskboard_integration import initialize_taskboard
        
        # Initialize TaskBoard
        initialize_taskboard(project_path)
        
        logger.info(f"TaskBoard initialized for {project_path}")
        
    except Exception as e:
        logger.error(f"Error initializing TaskBoard: {str(e)}", exc_info=True)