#!/usr/bin/env python3
"""
Tool Reference System Manager

This module provides the main interface for interacting with the Tool Reference
system, which gives Claude intelligence about how to use tools effectively.
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tool-reference")

def initialize_tool_reference(project_path: str) -> str:
    """
    Initialize the Tool Reference system for a project.
    
    This tool creates the .tool_reference directory structure and builds a comprehensive
    metadata system that helps Claude select and use tools effectively. Once initialized,
    Claude will have enhanced awareness of tool capabilities, relationships, and usage patterns.
    
    Args:
        project_path: The root directory of the project
        
    Returns:
        A success message or error information
    """
    try:
        # Check if project path exists
        if not os.path.exists(project_path):
            return f"❌ Directory does not exist: {project_path}"
        
        # Check if tool reference already exists
        tool_ref_path = os.path.join(project_path, ".tool_reference")
        if os.path.exists(tool_ref_path):
            # Refresh the tool reference
            return update_tool_reference(project_path)
            
        # Get path to the tool_index_builder.py script
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        builder_script = os.path.join(script_dir, "scripts", "tool_index_builder.py")
        
        if not os.path.exists(builder_script):
            # Try alternative location
            builder_script = os.path.join(script_dir, "scripts", "tool_index", "tool_index_builder.py")
            
        if not os.path.exists(builder_script):
            return f"❌ Tool index builder script not found at {builder_script}"
        
        # Run the builder script
        logger.info(f"Running tool index builder for {project_path}")
        result = subprocess.run(
            [sys.executable, builder_script, "--project-path", project_path, "--all"],
            capture_output=True, 
            text=True,
            check=False
        )
        
        # Check if the tool reference was created
        if not os.path.exists(tool_ref_path):
            return f"❌ Failed to create Tool Reference at {tool_ref_path}:\n{result.stderr}"
        
        # Count the created resources
        tool_count = 0
        registry_path = os.path.join(tool_ref_path, "registry.json")
        if os.path.exists(registry_path):
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                tool_count = len(registry.get("tools", {}))
        
        relationship_count = 0
        relationship_files = [f for f in os.listdir(tool_ref_path) if f.startswith("relationship_") and f.endswith(".json")]
        relationship_count = len(relationship_files)
        
        decision_tree_count = 0
        decision_trees_dir = os.path.join(tool_ref_path, "decision_trees")
        if os.path.exists(decision_trees_dir):
            decision_tree_count = len([f for f in os.listdir(decision_trees_dir) if f.endswith(".json")])
        
        tool_profiles_count = 0
        tool_profiles_dir = os.path.join(tool_ref_path, "tool_profiles")
        if os.path.exists(tool_profiles_dir):
            tool_profiles_count = len([f for f in os.listdir(tool_profiles_dir) if f.endswith(".json")])
        
        # Create success message
        success_message = f"""✅ Successfully initialized Tool Reference at {tool_ref_path}

Tool Reference Initialization Report:
✓ Tool registry created with {tool_count} tools
✓ {tool_profiles_count} detailed tool profiles generated
✓ {relationship_count} tool relationship groups defined
✓ {decision_tree_count} decision trees for tool selection

Claude now has enhanced awareness of tool capabilities, relationships between tools,
and optimal usage patterns. This will help me make better decisions about which tools
to use in different situations and how to combine them effectively.
        """
        
        logger.info(f"Successfully initialized Tool Reference at {tool_ref_path}")
        return success_message
    
    except Exception as e:
        logger.error(f"Error initializing Tool Reference: {str(e)}")
        return f"❌ Error initializing Tool Reference: {str(e)}"

def update_tool_reference(project_path: str) -> str:
    """
    Update an existing Tool Reference system.
    
    Args:
        project_path: The root directory of the project
        
    Returns:
        A success message or error information
    """
    try:
        # Check if project path exists
        if not os.path.exists(project_path):
            return f"❌ Directory does not exist: {project_path}"
        
        # Check if tool reference exists
        tool_ref_path = os.path.join(project_path, ".tool_reference")
        if not os.path.exists(tool_ref_path):
            return initialize_tool_reference(project_path)
        
        # Get path to the tool_index_builder.py script
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        builder_script = os.path.join(script_dir, "scripts", "tool_index_builder.py")
        
        if not os.path.exists(builder_script):
            # Try alternative location
            builder_script = os.path.join(script_dir, "scripts", "tool_index", "tool_index_builder.py")
            
        if not os.path.exists(builder_script):
            return f"❌ Tool index builder script not found at {builder_script}"
        
        # Run the builder script with clean option
        logger.info(f"Updating tool index for {project_path}")
        result = subprocess.run(
            [sys.executable, builder_script, "--project-path", project_path, "--clean", "--all"],
            capture_output=True, 
            text=True,
            check=False
        )
        
        # Check if the tool reference was updated
        if not os.path.exists(tool_ref_path):
            return f"❌ Failed to update Tool Reference at {tool_ref_path}:\n{result.stderr}"
        
        # Count the created resources
        tool_count = 0
        registry_path = os.path.join(tool_ref_path, "registry.json")
        if os.path.exists(registry_path):
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                tool_count = len(registry.get("tools", {}))
        
        relationship_count = 0
        relationship_files = [f for f in os.listdir(tool_ref_path) if f.startswith("relationship_") and f.endswith(".json")]
        relationship_count = len(relationship_files)
        
        decision_tree_count = 0
        decision_trees_dir = os.path.join(tool_ref_path, "decision_trees")
        if os.path.exists(decision_trees_dir):
            decision_tree_count = len([f for f in os.listdir(decision_trees_dir) if f.endswith(".json")])
        
        tool_profiles_count = 0
        tool_profiles_dir = os.path.join(tool_ref_path, "tool_profiles")
        if os.path.exists(tool_profiles_dir):
            tool_profiles_count = len([f for f in os.listdir(tool_profiles_dir) if f.endswith(".json")])
        
        # Update the last_updated field in registry.json
        if os.path.exists(registry_path):
            try:
                with open(registry_path, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                
                registry["last_updated"] = datetime.now().isoformat()
                
                with open(registry_path, 'w', encoding='utf-8') as f:
                    json.dump(registry, f, indent=2)
            except Exception as e:
                logger.warning(f"Error updating timestamp in registry.json: {str(e)}")
        
        # Create success message
        success_message = f"""✅ Successfully updated Tool Reference at {tool_ref_path}

Tool Reference Update Report:
✓ Tool registry updated with {tool_count} tools
✓ {tool_profiles_count} detailed tool profiles updated
✓ {relationship_count} tool relationship groups refreshed
✓ {decision_tree_count} decision trees for tool selection updated

Claude's awareness of tool capabilities, relationships, and usage patterns has been refreshed.
        """
        
        logger.info(f"Successfully updated Tool Reference at {tool_ref_path}")
        return success_message
    
    except Exception as e:
        logger.error(f"Error updating Tool Reference: {str(e)}")
        return f"❌ Error updating Tool Reference: {str(e)}"

def generate_tool_reference(project_path: str) -> str:
    """
    Alias for initialize_tool_reference for consistency with generate_librarian.
    
    Args:
        project_path: The root directory of the project
        
    Returns:
        A success message or error information
    """
    return initialize_tool_reference(project_path)
