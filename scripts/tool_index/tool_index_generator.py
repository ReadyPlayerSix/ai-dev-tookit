#!/usr/bin/env python3
"""
Tool Index Generator

This script creates an AI-optimized Tool Index for Claude, implementing
a structured metadata repository that helps Claude select and use the
appropriate tools for different tasks.

Usage:
    python tool_index_generator.py [--project-path PATH]
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tool_index_generator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("tool-index-generator")

# Define the core tools to include in the initial implementation
CORE_TOOLS = [
    "read_file",
    "write_file",
    "edit_file",
    "enhanced_edit_file",
    "search_files",
    "list_allowed_directories",
    "check_project_access",
    "initialize_librarian",
    "query_component",
    "find_implementation"
]

# Define tool categories
TOOL_CATEGORIES = {
    "filesystem": [
        "read_file", 
        "write_file", 
        "edit_file", 
        "enhanced_edit_file", 
        "search_files",
        "move_file", 
        "directory_tree",
        "create_directory",
        "get_file_info",
        "read_multiple_files"
    ],
    "librarian": [
        "initialize_librarian", 
        "query_component", 
        "find_implementation", 
        "generate_librarian",
        "sanity_check",
        "find_related_files"
    ],
    "todo": [
        "add_todo", 
        "list_todos", 
        "update_todo_status",
        "add_subtask", 
        "search_todos", 
        "infer_todos"
    ],
    "server": [
        "list_allowed_directories",
        "check_project_access"
    ]
}

# Define basic tool relationships
TOOL_RELATIONSHIPS = {
    "read_file": {
        "often_used_with": ["edit_file", "search_files"],
        "usually_precedes": ["edit_file", "enhanced_edit_file"],
        "common_sequence": ["search_files", "read_file", "edit_file"]
    },
    "edit_file": {
        "often_used_with": ["read_file"],
        "usually_follows": ["read_file"],
        "alternative_to": ["enhanced_edit_file", "write_file"]
    },
    "initialize_librarian": {
        "usually_precedes": ["query_component", "find_implementation", "generate_librarian"],
        "often_used_with": ["check_project_access"]
    },
    "check_project_access": {
        "usually_precedes": ["initialize_librarian"],
        "often_used_with": ["list_allowed_directories"]
    }
}

def create_tool_reference_structure(project_path: str) -> str:
    """
    Create the basic .tool_reference directory structure.
    
    Args:
        project_path: Path to the project
        
    Returns:
        Path to the created .tool_reference directory
    """
    tool_ref_path = os.path.join(project_path, ".tool_reference")
    
    # Create main directories
    os.makedirs(tool_ref_path, exist_ok=True)
    os.makedirs(os.path.join(tool_ref_path, "tool_profiles"), exist_ok=True)
    os.makedirs(os.path.join(tool_ref_path, "decision_trees"), exist_ok=True)
    os.makedirs(os.path.join(tool_ref_path, "usage_patterns"), exist_ok=True)
    os.makedirs(os.path.join(tool_ref_path, "self_diagnostic"), exist_ok=True)
    
    logger.info(f"Created .tool_reference directory structure at {tool_ref_path}")
    
    return tool_ref_path

def create_registry_file(tool_ref_path: str) -> None:
    """
    Create the main registry.json file.
    
    Args:
        tool_ref_path: Path to the .tool_reference directory
    """
    registry = {
        "version": "0.1.0",
        "description": "AI-optimized Tool Index for Claude",
        "last_updated": "",  # Will be set at runtime
        "tools": {
            tool: {
                "id": tool,
                "category": next((cat for cat, tools in TOOL_CATEGORIES.items() if tool in tools), "other"),
                "profile_path": f"tool_profiles/{tool}.json",
                "has_profile": False  # Will be updated when profiles are created
            }
            for tool in CORE_TOOLS
        }
    }
    
    # Set last_updated to current timestamp
    from datetime import datetime
    registry["last_updated"] = datetime.now().isoformat()
    
    # Write the registry file
    registry_path = os.path.join(tool_ref_path, "registry.json")
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)
    
    logger.info(f"Created registry.json at {registry_path}")

def create_categories_file(tool_ref_path: str) -> None:
    """
    Create the categories.json file.
    
    Args:
        tool_ref_path: Path to the .tool_reference directory
    """
    categories = {
        "version": "0.1.0",
        "description": "Tool categorization for Claude",
        "categories": {
            category: {
                "name": category,
                "description": f"Tools related to {category} operations",
                "tools": tools
            }
            for category, tools in TOOL_CATEGORIES.items()
        }
    }
    
    # Write the categories file
    categories_path = os.path.join(tool_ref_path, "categories.json")
    with open(categories_path, 'w', encoding='utf-8') as f:
        json.dump(categories, f, indent=2)
    
    logger.info(f"Created categories.json at {categories_path}")

def create_relationships_file(tool_ref_path: str) -> None:
    """
    Create the relationships.json file.
    
    Args:
        tool_ref_path: Path to the .tool_reference directory
    """
    relationships = {
        "version": "0.1.0",
        "description": "Tool relationships for Claude",
        "tool_relationships": TOOL_RELATIONSHIPS,
        "common_workflows": [
            {
                "name": "file_editing",
                "description": "Edit existing files",
                "tools": ["search_files", "read_file", "edit_file"],
                "typical_sequence": ["search_files", "read_file", "edit_file"]
            },
            {
                "name": "project_initialization",
                "description": "Initialize AI Librarian for a project",
                "tools": ["list_allowed_directories", "check_project_access", "initialize_librarian"],
                "typical_sequence": ["list_allowed_directories", "check_project_access", "initialize_librarian"]
            }
        ]
    }
    
    # Write the relationships file
    relationships_path = os.path.join(tool_ref_path, "relationships.json")
    with open(relationships_path, 'w', encoding='utf-8') as f:
        json.dump(relationships, f, indent=2)
    
    logger.info(f"Created relationships.json at {relationships_path}")

def main():
    """Main function to run the tool index generator."""
    parser = argparse.ArgumentParser(description="Generate an AI-optimized Tool Index for Claude")
    parser.add_argument(
        "--project-path", 
        type=str, 
        default=".",
        help="Path to the project directory (default: current directory)"
    )
    
    args = parser.parse_args()
    project_path = os.path.abspath(args.project_path)
    
    try:
        # Create the directory structure
        tool_ref_path = create_tool_reference_structure(project_path)
        
        # Create the main files
        create_registry_file(tool_ref_path)
        create_categories_file(tool_ref_path)
        create_relationships_file(tool_ref_path)
        
        print(f"✅ Successfully created Tool Index structure at {tool_ref_path}")
        print("This completes Phase 1 of the Tool Index implementation.")
        print("\nNext steps:")
        print("1. Review the created directory structure and files")
        print("2. Proceed to Phase 2: Implementing detailed tool profiles")
        
        return 0
    except Exception as e:
        logger.error(f"Error creating Tool Index: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
