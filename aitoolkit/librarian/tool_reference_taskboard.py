#!/usr/bin/env python3
"""
Tool Reference TaskBoard Integration

This module integrates the Tool Reference system with the TaskBoard,
providing asynchronous operations for tool index generation and cross-referencing
between .ai_reference and .tool_reference directories.
"""

import os
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Union, Tuple

# Local imports
from .task_board import get_task_board, TaskPriority, TaskStatus, TaskResult
from .tool_reference import initialize_tool_reference, update_tool_reference

# Configure logger
logger = logging.getLogger("ai_librarian.tool_reference_taskboard")

# Task type for tool reference operations
TOOL_REF_TASK_TYPE = "tool_reference"

def register_tool_reference_task_type():
    """Register the tool reference task type with the TaskBoard system"""
    from .taskboard_integration import TASK_TYPE_REGISTRY
    
    # Add tool reference task type to the registry if not already present
    if TOOL_REF_TASK_TYPE not in TASK_TYPE_REGISTRY:
        TASK_TYPE_REGISTRY[TOOL_REF_TASK_TYPE] = {
            "description": "Manage tool reference system and cross-references",
            "mini_librarians": ["tool-indexer", "reference-linker"],
            "handler": "_handle_tool_reference_task"
        }
        logger.info(f"Registered {TOOL_REF_TASK_TYPE} task type with TaskBoard")

def _handle_tool_reference_task(project_path: str, params: Dict[str, Any]) -> TaskResult:
    """
    Handler for tool reference tasks
    
    Args:
        project_path: Path to the project
        params: Task parameters
        
    Returns:
        TaskResult with the outcome
    """
    operation = params.get("operation", "initialize")
    
    try:
        if operation == "initialize":
            result = initialize_tool_reference(project_path)
            return TaskResult(success=True, data=result)
        
        elif operation == "update":
            result = update_tool_reference(project_path)
            return TaskResult(success=True, data=result)
        
        elif operation == "cross_reference":
            result = cross_reference_ai_and_tool_directories(project_path)
            return TaskResult(success=True, data=result)
        
        else:
            return TaskResult(
                success=False,
                data=None,
                error_message=f"Unknown tool reference operation: {operation}"
            )
    
    except Exception as e:
        logger.error(f"Error executing tool reference task: {str(e)}", exc_info=True)
        return TaskResult(
            success=False,
            data=None,
            error_message=f"Error executing tool reference task: {str(e)}"
        )

def cross_reference_ai_and_tool_directories(project_path: str) -> str:
    """
    Create cross-references between .ai_reference and .tool_reference directories
    
    This function establishes bidirectional links between the AI Librarian context
    and the Tool Reference system, improving Claude's ability to navigate between
    code components and the tools that operate on them.
    
    Args:
        project_path: Path to the project
        
    Returns:
        Success message or error information
    """
    try:
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        tool_ref_path = os.path.join(project_path, ".tool_reference")
        
        # Verify both directories exist
        if not os.path.exists(ai_ref_path):
            return f"❌ AI Reference directory not found at {ai_ref_path}"
        
        if not os.path.exists(tool_ref_path):
            return f"❌ Tool Reference directory not found at {tool_ref_path}"
        
        # Create cross-reference directory in AI Reference
        cross_ref_ai_path = os.path.join(ai_ref_path, "tool_references")
        os.makedirs(cross_ref_ai_path, exist_ok=True)
        
        # Create cross-reference directory in Tool Reference
        cross_ref_tool_path = os.path.join(tool_ref_path, "ai_references")
        os.makedirs(cross_ref_tool_path, exist_ok=True)
        
        # Create component to tool mapping
        component_to_tool_map = {}
        
        # Load component registry from AI Reference
        component_registry_path = os.path.join(ai_ref_path, "component_registry.json")
        if os.path.exists(component_registry_path):
            with open(component_registry_path, 'r', encoding='utf-8') as f:
                component_registry = json.load(f)
        else:
            component_registry = {}
        
        # Load tool registry from Tool Reference
        tool_registry_path = os.path.join(tool_ref_path, "registry.json")
        if os.path.exists(tool_registry_path):
            with open(tool_registry_path, 'r', encoding='utf-8') as f:
                tool_registry = json.load(f)
        else:
            tool_registry = {"tools": {}}
        
        # Create mapping of component types to relevant tools
        for component_type, components in component_registry.items():
            relevant_tools = []
            
            # Find tools that work with this component type
            for tool_id, tool_info in tool_registry.get("tools", {}).items():
                # Skip if no applicable_to field
                if "applicable_to" not in tool_info:
                    continue
                
                # Check if tool applies to this component type
                # Get list of applicable component types, ensuring they're all strings
                applicable_types = []
                for t in tool_info["applicable_to"]:
                    if isinstance(t, str):
                        applicable_types.append(t.lower())
                    else:
                        logger.warning(f"Non-string type in applicable_to for tool {tool_id}: {t}")
                
                if component_type.lower() in applicable_types:
                    relevant_tools.append({
                        "id": tool_id,
                        "name": tool_info.get("name", tool_id),
                        "description": tool_info.get("description", "")
                    })
            
            # Add to mapping if we found relevant tools
            if relevant_tools:
                component_to_tool_map[component_type] = relevant_tools
        
        # Save component to tool mapping in AI Reference
        component_tool_map_path = os.path.join(cross_ref_ai_path, "component_tools.json")
        with open(component_tool_map_path, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": tool_registry.get("last_updated", ""),
                "component_tools": component_to_tool_map
            }, f, indent=2)
        
        # Create tool to component mapping (inverse of above)
        tool_to_component_map = {}
        
        for tool_id, tool_info in tool_registry.get("tools", {}).items():
            applicable_components = []
            
            # Skip if no applicable_to field
            if "applicable_to" not in tool_info:
                continue
            
            # Find components that this tool works with
            for component_type in tool_info["applicable_to"]:
                # Check if component_type is actually a string and not a dict or other object
                if not isinstance(component_type, str):
                    logger.warning(f"Non-string component type in applicable_to for tool {tool_id}: {component_type}")
                    continue
                    
                if component_type in component_registry:
                    applicable_components.append({
                        "type": component_type,
                        "count": len(component_registry[component_type]),
                        "sample": list(component_registry[component_type].keys())[:5] # First 5 as sample
                    })
            
            # Add to mapping if we found applicable components
            if applicable_components:
                tool_to_component_map[tool_id] = applicable_components
        
        # Save tool to component mapping in Tool Reference
        tool_component_map_path = os.path.join(cross_ref_tool_path, "tool_components.json")
        with open(tool_component_map_path, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": tool_registry.get("last_updated", ""),
                "tool_components": tool_to_component_map
            }, f, indent=2)
        
        # Create summary of cross-reference
        cross_ref_count = len(component_to_tool_map)
        tool_count = len(tool_registry.get("tools", {}))
        component_type_count = len(component_registry)
        
        # Success message
        success_message = f"""✅ Successfully created cross-references between AI Reference and Tool Reference

Cross-Reference Summary:
✓ {cross_ref_count} component types mapped to relevant tools
✓ {tool_count} tools linked to applicable component types
✓ Bidirectional navigation paths established between {component_type_count} component types and tools

Claude now has improved ability to navigate between code components and the tools
that can work with them, enabling more efficient and contextual tool selection.
        """
        
        logger.info(f"Created cross-references between AI and Tool references for {project_path}")
        return success_message
        
    except Exception as e:
        logger.error(f"Error creating cross-references: {str(e)}")
        return f"❌ Error creating cross-references: {str(e)}"

def initialize_tool_reference_async(project_path: str, priority: str = "medium") -> str:
    """
    Initialize the Tool Reference system asynchronously using TaskBoard
    
    Args:
        project_path: Path to the project
        priority: Task priority (high, medium, low)
        
    Returns:
        Task ID or error message
    """
    try:
        # Register task type if not already registered
        register_tool_reference_task_type()
        
        # Get task board instance
        task_board = get_task_board(project_path)
        
        # Convert priority string to enum
        task_priority = TaskPriority.MEDIUM
        if priority.lower() == "high":
            task_priority = TaskPriority.HIGH
        elif priority.lower() == "low":
            task_priority = TaskPriority.LOW
        
        # Submit task to TaskBoard
        task_id = task_board.submit_task(
            task_type=TOOL_REF_TASK_TYPE,
            params={"operation": "initialize"},
            priority=task_priority
        )
        
        return f"Tool Reference initialization started with task ID: {task_id}"
        
    except Exception as e:
        logger.error(f"Error submitting tool reference initialization task: {str(e)}")
        return f"❌ Error submitting tool reference initialization task: {str(e)}"

def update_tool_reference_async(project_path: str, priority: str = "medium") -> str:
    """
    Update the Tool Reference system asynchronously using TaskBoard
    
    Args:
        project_path: Path to the project
        priority: Task priority (high, medium, low)
        
    Returns:
        Task ID or error message
    """
    try:
        # Register task type if not already registered
        register_tool_reference_task_type()
        
        # Get task board instance
        task_board = get_task_board(project_path)
        
        # Convert priority string to enum
        task_priority = TaskPriority.MEDIUM
        if priority.lower() == "high":
            task_priority = TaskPriority.HIGH
        elif priority.lower() == "low":
            task_priority = TaskPriority.LOW
        
        # Submit task to TaskBoard
        task_id = task_board.submit_task(
            task_type=TOOL_REF_TASK_TYPE,
            params={"operation": "update"},
            priority=task_priority
        )
        
        return f"Tool Reference update started with task ID: {task_id}"
        
    except Exception as e:
        logger.error(f"Error submitting tool reference update task: {str(e)}")
        return f"❌ Error submitting tool reference update task: {str(e)}"

def cross_reference_async(project_path: str, priority: str = "medium") -> str:
    """
    Create cross-references asynchronously using TaskBoard
    
    Args:
        project_path: Path to the project
        priority: Task priority (high, medium, low)
        
    Returns:
        Task ID or error message
    """
    try:
        # Register task type if not already registered
        register_tool_reference_task_type()
        
        # Get task board instance
        task_board = get_task_board(project_path)
        
        # Convert priority string to enum
        task_priority = TaskPriority.MEDIUM
        if priority.lower() == "high":
            task_priority = TaskPriority.HIGH
        elif priority.lower() == "low":
            task_priority = TaskPriority.LOW
        
        # Submit task to TaskBoard
        task_id = task_board.submit_task(
            task_type=TOOL_REF_TASK_TYPE,
            params={"operation": "cross_reference"},
            priority=task_priority
        )
        
        return f"Cross-reference creation started with task ID: {task_id}"
        
    except Exception as e:
        logger.error(f"Error submitting cross-reference task: {str(e)}")
        return f"❌ Error submitting cross-reference task: {str(e)}"