#!/usr/bin/env python3
"""
TaskBoard integration for AI Librarian server

This module provides integration functions between the TaskBoard system
and the AI Librarian server, allowing async task processing to be used
with MCP tools.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union

# Local imports
from .task_board import get_task_board, TaskPriority, TaskStatus


# Configure logger
logger = logging.getLogger("ai_librarian.taskboard_integration")

# ================================
# Task Type Registry
# ================================

# This maps task types to the corresponding mini-librarians and handler functions
TASK_TYPE_REGISTRY = {
    # Code analysis tasks
    "code_analysis": {
        "description": "Analyze code components and their relationships",
        "mini_librarians": ["component-analyzer", "dependency-mapper"],
        "handler": "_handle_code_analysis_task"
    },
    "semantic_search": {
        "description": "Perform semantic search across the codebase",
        "mini_librarians": ["semantic-indexer", "code-searcher"],
        "handler": "_handle_semantic_search_task"
    },
    "think": {
        "description": "Perform deep analysis on complex problems",
        "mini_librarians": ["component-analyzer", "dependency-mapper", "semantic-indexer"],
        "handler": "_handle_think_task"
    },
    "documentation_generation": {
        "description": "Generate documentation for code components",
        "mini_librarians": ["component-analyzer", "doc-generator"],
        "handler": "_handle_documentation_task"
    },
    "task_decomposition": {
        "description": "Break down complex tasks into smaller units",
        "mini_librarians": ["task-analyzer", "dependency-mapper"],
        "handler": "_handle_task_decomposition"
    }
}

# ================================
# Integration Functions
# ================================

def get_registered_task_types() -> Dict[str, Dict[str, Any]]:
    """Get all registered task types with their descriptions"""
    return {task_type: {"description": info["description"]} 
            for task_type, info in TASK_TYPE_REGISTRY.items()}

def get_mini_librarians_for_task(task_type: str) -> List[str]:
    """Get the mini-librarians needed for a specific task type"""
    if task_type in TASK_TYPE_REGISTRY:
        return TASK_TYPE_REGISTRY[task_type].get("mini_librarians", [])
    return []

def get_task_handler_name(task_type: str) -> Optional[str]:
    """Get the handler function name for a specific task type"""
    if task_type in TASK_TYPE_REGISTRY:
        return TASK_TYPE_REGISTRY[task_type].get("handler")
    return None

def initialize_taskboard_system(project_path: str) -> None:
    """Initialize the TaskBoard system for a project"""
    # Ensure TaskBoard is initialized
    get_task_board(project_path)
    logger.info(f"TaskBoard system initialized for {project_path}")

def register_mini_librarians(project_path: str) -> None:
    """Register mini-librarians with the system based on the tool index"""
    try:
        # Get the tool index path
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        tool_index_path = os.path.join(ai_ref_path, "tool_index")
        
        # Check if registry exists
        registry_path = os.path.join(tool_index_path, "registry.json")
        if not os.path.exists(registry_path):
            logger.warning(f"Tool registry not found at {registry_path}")
            return
            
        # Load registry
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
            
        # Update TaskBoard integration section
        registry["taskboard_integration"] = {
            "task_type_to_mini_librarian_mapping": {
                task_type: info["mini_librarians"]
                for task_type, info in TASK_TYPE_REGISTRY.items()
            }
        }
        
        # Save updated registry
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
            
        logger.info(f"Registered TaskBoard mini-librarians in {registry_path}")
        
    except Exception as e:
        logger.error(f"Error registering mini-librarians: {str(e)}")

# ================================
# MCP Tool Integration
# ================================

def register_taskboard_mcp_tools(server_context: Dict[str, Any]) -> None:
    """Register TaskBoard MCP tools with the server context"""
    from .task_board import (
        submit_background_task,
        get_task_status_mcp,
        get_task_result_mcp,
        cancel_task_mcp,
        list_tasks_mcp,
        think
    )
    
    # Register MCP tools
    tools = server_context.get("mcp_tools", {})
    
    # Add TaskBoard tools
    tools["submit_background_task"] = {
        "function": submit_background_task,
        "description": "Submit a task to be processed asynchronously in the background",
        "parameters": [
            {"name": "project_path", "type": "string", "description": "Path to the project"},
            {"name": "task_type", "type": "string", "description": "Type of task (e.g., 'code_analysis', 'semantic_search')"},
            {"name": "parameters", "type": "object", "description": "Parameters for the task"},
            {"name": "priority", "type": "string", "description": "Priority of the task ('high', 'medium', 'low')", "default": "medium"}
        ]
    }
    
    tools["get_task_status"] = {
        "function": get_task_status_mcp,
        "description": "Get the status of a background task",
        "parameters": [
            {"name": "project_path", "type": "string", "description": "Path to the project"},
            {"name": "task_id", "type": "string", "description": "ID of the task to check"}
        ]
    }
    
    tools["get_task_result"] = {
        "function": get_task_result_mcp,
        "description": "Get the result of a completed background task",
        "parameters": [
            {"name": "project_path", "type": "string", "description": "Path to the project"},
            {"name": "task_id", "type": "string", "description": "ID of the task to get the result for"}
        ]
    }
    
    tools["cancel_task"] = {
        "function": cancel_task_mcp,
        "description": "Cancel a pending background task",
        "parameters": [
            {"name": "project_path", "type": "string", "description": "Path to the project"},
            {"name": "task_id", "type": "string", "description": "ID of the task to cancel"}
        ]
    }
    
    tools["list_tasks"] = {
        "function": list_tasks_mcp,
        "description": "List background tasks",
        "parameters": [
            {"name": "project_path", "type": "string", "description": "Path to the project"},
            {"name": "status", "type": "string", "description": "Optional status filter ('pending', 'running', 'completed', 'failed', 'timeout', 'cancelled')"},
            {"name": "task_type", "type": "string", "description": "Optional task type filter"}
        ]
    }
    
    tools["think"] = {
        "function": think,
        "description": "The 'think' function starts a deep analysis task that processes complex problems",
        "parameters": [
            {"name": "project_path", "type": "string", "description": "Path to the project"},
            {"name": "query", "type": "string", "description": "The question or problem to analyze"},
            {"name": "priority", "type": "string", "description": "Priority of the task ('high', 'medium', 'low')", "default": "high"}
        ]
    }
    
    # Update MCP tools in server context
    server_context["mcp_tools"] = tools
    
    logger.info("Registered TaskBoard MCP tools")

# ================================
# Initialization
# ================================

def initialize_taskboard(project_path: str, server_context: Optional[Dict[str, Any]] = None) -> None:
    """Initialize the TaskBoard system for a project"""
    # Initialize TaskBoard
    initialize_taskboard_system(project_path)
    
    # Register mini-librarians
    register_mini_librarians(project_path)
    
    # Register MCP tools if server context is provided
    if server_context is not None:
        register_taskboard_mcp_tools(server_context)
    
    logger.info(f"TaskBoard fully initialized for {project_path}")

# ================================
# Task Handlers (placeholders)
# ================================

def _handle_code_analysis_task(project_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a code analysis task"""
    # This would be implemented with actual mini-librarian calls
    import time
    time.sleep(1)  # Simulate work
    
    return {
        "status": "success",
        "result": f"Analyzed code components for {project_path}",
        "components_analyzed": 5,
        "relationships_found": 12
    }

def _handle_semantic_search_task(project_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a semantic search task"""
    # This would be implemented with actual mini-librarian calls
    import time
    time.sleep(1.5)  # Simulate work
    
    return {
        "status": "success",
        "result": f"Performed semantic search for {params.get('query', '')}",
        "files_searched": 20,
        "matches_found": 7
    }

def _handle_think_task(project_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a think task"""
    # This would be implemented with actual mini-librarian calls
    import time
    time.sleep(2)  # Simulate work
    
    query = params.get("query", "")
    
    return {
        "status": "success",
        "result": f"Deep analysis completed for query: {query}",
        "components_analyzed": 15,
        "insights": [
            "The authentication system uses JWT tokens for validation",
            "User permissions are checked in the AuthGuard middleware",
            "There are 3 distinct user roles with different permission levels"
        ]
    }

def _handle_documentation_task(project_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a documentation generation task"""
    # This would be implemented with actual mini-librarian calls
    import time
    time.sleep(1.2)  # Simulate work
    
    return {
        "status": "success",
        "result": f"Generated documentation for {project_path}",
        "files_documented": 8,
        "components_documented": 12
    }

def _handle_task_decomposition(project_path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a task decomposition task"""
    # This would be implemented with actual mini-librarian calls
    import time
    time.sleep(0.8)  # Simulate work
    
    return {
        "status": "success",
        "result": f"Decomposed task into subtasks",
        "task": params.get("task", ""),
        "subtasks": [
            "Research authentication requirements",
            "Design database schema for users",
            "Implement login endpoint",
            "Create JWT token generation",
            "Set up password hashing"
        ]
    }