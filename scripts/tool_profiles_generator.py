#!/usr/bin/env python3
"""
Tool Profiles Generator

This script creates detailed tool profiles for the AI-optimized Tool Index.
It's the second phase of the Tool Index implementation, focusing on creating
rich metadata for each tool to help Claude make better decisions.

Usage:
    python tool_profiles_generator.py [--project-path PATH] [--tools TOOL1,TOOL2,...]
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
        logging.FileHandler("tool_profiles_generator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("tool-profiles-generator")

# Tool profile templates
TOOL_PROFILES = {
    "read_file": {
        "tool_id": "read_file",
        "primary_purpose": "retrieve content from file system",
        "execution_context": "file system access required",
        "parameter_patterns": {
            "path": {
                "validation": "must be string, must exist in allowed directories",
                "common_errors": ["path not found", "permission denied"],
                "recovery_strategies": ["check_project_access", "list_allowed_directories"]
            },
            "encoding": {
                "validation": "optional, must be string encoding name",
                "common_errors": ["unknown encoding"],
                "recovery_strategies": ["try utf-8 as default"]
            }
        },
        "always_use_when": [
            "need to examine file contents",
            "need to analyze code",
            "need to read configuration"
        ],
        "never_use_when": [
            "need to modify file",
            "file is known to be binary",
            "path definitely doesn't exist",
            "just need to check if file exists"
        ],
        "use_with": [
            {
                "tool": "edit_file",
                "pattern": "read-then-modify",
                "rationale": "get current content before modifying"
            },
            {
                "tool": "search_files",
                "pattern": "find-then-examine",
                "rationale": "locate files of interest, then read them"
            }
        ],
        "complexity_limits": {
            "max_file_size_recommendation": "5MB",
            "handling_strategy_for_large_files": "read_multiple_files with chunking"
        },
        "coding_limits": {
            "max_code_size_safely_editable": "500 lines",
            "error_rate_threshold": "increasing errors after 300+ lines suggests rewrite"
        },
        "context_validation": {
            "prerequisites": ["file exists", "have read permissions"],
            "post_conditions": ["file content is in context"]
        },
        "common_error_patterns": [
            {
                "pattern": "UnicodeDecodeError",
                "meaning": "File is binary or has unexpected encoding",
                "solution": "specify correct encoding or use binary mode"
            },
            {
                "pattern": "PermissionError",
                "meaning": "No read access to file",
                "solution": "check_project_access to verify permissions"
            }
        ],
        "execution_examples": [
            {
                "intent": "Read Python file to understand class definition",
                "parameters": {"path": "project/src/main.py"},
                "success_pattern": "Content contains class definitions",
                "follow_up": "parse code with query_component or manually analyze"
            }
        ]
    },
    
    "edit_file": {
        "tool_id": "edit_file",
        "primary_purpose": "modify portions of existing files",
        "execution_context": "file system access required, write permissions needed",
        "parameter_patterns": {
            "path": {
                "validation": "must be string, must exist in allowed directories",
                "common_errors": ["path not found", "permission denied"],
                "recovery_strategies": ["check_project_access", "list_allowed_directories"]
            },
            "old_text": {
                "validation": "must exist exactly once in file",
                "common_errors": ["text not found", "text appears multiple times"],
                "recovery_strategies": ["read file first to check content", "make old_text more specific"]
            },
            "new_text": {
                "validation": "any string, can be empty for deletion",
                "common_errors": ["incorrect indentation", "syntax errors"],
                "recovery_strategies": ["preserve original indentation", "validate code before editing"]
            }
        },
        "always_use_when": [
            "need to make targeted changes to portions of a file",
            "modifying specific parameters or values",
            "updating function implementations",
            "need to replace specific text patterns"
        ],
        "never_use_when": [
            "file doesn't exist yet - use write_file instead",
            "need to completely overwrite file - use write_file instead",
            "not sure if old_text appears exactly once",
            "changes are too complex or span multiple non-contiguous sections"
        ],
        "use_with": [
            {
                "tool": "read_file",
                "pattern": "read-then-modify",
                "rationale": "get current content before modifying"
            },
            {
                "tool": "search_files",
                "pattern": "find-then-modify",
                "rationale": "locate files to modify"
            }
        ],
        "complexity_limits": {
            "max_edit_size_recommendation": "300 lines of code",
            "handling_strategy_for_large_edits": "break into multiple smaller edits"
        },
        "coding_limits": {
            "max_code_size_safely_editable": "300 lines",
            "error_rate_threshold": "multiple syntax or logic errors indicate need for rewrite",
            "rewrite_indicators": [
                "needing multiple passes to fix errors",
                "confusion about context or variable scope",
                "significant structural changes to the code"
            ]
        },
        "context_validation": {
            "prerequisites": ["file exists", "have write permissions", "old_text exists exactly once"],
            "post_conditions": ["file contains new_text where old_text was"]
        },
        "common_error_patterns": [
            {
                "pattern": "old_text not found",
                "meaning": "Text has changed or was incorrectly specified",
                "solution": "read_file first, then precisely copy the text to replace"
            },
            {
                "pattern": "old_text appears multiple times",
                "meaning": "Ambiguous replacement target",
                "solution": "make old_text longer and more specific"
            },
            {
                "pattern": "PermissionError",
                "meaning": "No write access to file",
                "solution": "check_project_access to verify permissions"
            }
        ],
        "execution_examples": [
            {
                "intent": "Update a function parameter",
                "parameters": {
                    "path": "project/src/module.py",
                    "old_text": "def process_data(input_file):",
                    "new_text": "def process_data(input_file, debug=False):"
                },
                "success_pattern": "Function signature updated with new parameter",
                "follow_up": "may need to update function body to use new parameter"
            }
        ]
    },
    
    "initialize_librarian": {
        "tool_id": "initialize_librarian",
        "primary_purpose": "set up AI Librarian for a project",
        "execution_context": "requires project directory with write access",
        "parameter_patterns": {
            "project_path": {
                "validation": "must be string, must be a directory, must have access",
                "common_errors": ["path not found", "permission denied"],
                "recovery_strategies": ["check_project_access", "list_allowed_directories"]
            }
        },
        "always_use_when": [
            "starting to work with a new project",
            "need code understanding capabilities",
            "need to track code components across conversations",
            "want to enable code navigation features"
        ],
        "never_use_when": [
            "already initialized for this project",
            "don't have write access to project directory",
            "working with simple scripts rather than project"
        ],
        "use_with": [
            {
                "tool": "check_project_access",
                "pattern": "check-then-initialize",
                "rationale": "verify access before creating files"
            },
            {
                "tool": "query_component",
                "pattern": "initialize-then-query",
                "rationale": "must initialize before querying components"
            }
        ],
        "complexity_limits": {
            "max_project_size_recommendation": "10,000 files",
            "handling_strategy_for_large_projects": "initialize on specific subdirectories"
        },
        "context_validation": {
            "prerequisites": ["project directory exists", "have write permissions"],
            "post_conditions": [".ai_reference directory created", "project added to active monitoring"]
        },
        "common_error_patterns": [
            {
                "pattern": "permission denied",
                "meaning": "No write access to project directory",
                "solution": "check_project_access to verify permissions"
            },
            {
                "pattern": "already initialized",
                "meaning": "Librarian already exists for this project",
                "solution": "use generate_librarian to update instead"
            }
        ],
        "execution_examples": [
            {
                "intent": "Set up AI Librarian for a new project",
                "parameters": {"project_path": "/path/to/project"},
                "success_pattern": "Successfully initialized AI Librarian",
                "follow_up": "query components to understand the codebase"
            }
        ]
    },
    
    "query_component": {
        "tool_id": "query_component",
        "primary_purpose": "retrieve information about a specific code component",
        "execution_context": "requires initialized AI Librarian",
        "parameter_patterns": {
            "project_path": {
                "validation": "must be string, must be a directory with initialized AI Librarian",
                "common_errors": ["librarian not initialized", "permission denied"],
                "recovery_strategies": ["initialize_librarian first", "check_project_access"]
            },
            "component_name": {
                "validation": "must be string, should be a class or function name",
                "common_errors": ["component not found"],
                "recovery_strategies": ["use find_implementation to search first"]
            }
        },
        "always_use_when": [
            "need to find detailed information about a specific component",
            "need to locate where a class or function is defined",
            "need to understand a specific component's implementation",
            "trying to find a component's code before modifying it"
        ],
        "never_use_when": [
            "looking for text rather than components - use find_implementation instead",
            "librarian not initialized - use initialize_librarian first",
            "component name is uncertain - use find_implementation first"
        ],
        "use_with": [
            {
                "tool": "initialize_librarian",
                "pattern": "initialize-then-query",
                "rationale": "must initialize before querying components"
            },
            {
                "tool": "find_implementation",
                "pattern": "search-then-query",
                "rationale": "find component names first, then query details"
            }
        ],
        "context_validation": {
            "prerequisites": ["AI Librarian initialized", "component exists in project"],
            "post_conditions": ["component details in context"]
        },
        "common_error_patterns": [
            {
                "pattern": "librarian not initialized",
                "meaning": "AI Librarian setup required",
                "solution": "run initialize_librarian first"
            },
            {
                "pattern": "component not found",
                "meaning": "Component doesn't exist or has different name",
                "solution": "use find_implementation to search for similar names"
            }
        ],
        "execution_examples": [
            {
                "intent": "Get implementation details of a class",
                "parameters": {
                    "project_path": "/path/to/project",
                    "component_name": "UserAuthentication"
                },
                "success_pattern": "Returns file location and code for UserAuthentication",
                "follow_up": "analyze code structure and relationships"
            }
        ]
    },
    
    "find_implementation": {
        "tool_id": "find_implementation",
        "primary_purpose": "search for text patterns across project files",
        "execution_context": "requires read access to project",
        "parameter_patterns": {
            "project_path": {
                "validation": "must be string, must be a directory with read access",
                "common_errors": ["path not found", "permission denied"],
                "recovery_strategies": ["check_project_access", "list_allowed_directories"]
            },
            "search_text": {
                "validation": "must be string, non-empty",
                "common_errors": ["no matches found"],
                "recovery_strategies": ["try different search terms", "use partial words"]
            },
            "file_pattern": {
                "validation": "optional, file extension filter like '*.py'",
                "common_errors": ["invalid pattern"],
                "recovery_strategies": ["omit to search all files"]
            }
        },
        "always_use_when": [
            "looking for specific text, function calls, or patterns",
            "need to find where certain functionality is implemented",
            "searching for examples of specific coding patterns",
            "discovering component usages",
            "don't know exact component names"
        ],
        "never_use_when": [
            "exact component name is known - use query_component instead",
            "path definitely doesn't exist",
            "looking for general project structure rather than specific code"
        ],
        "use_with": [
            {
                "tool": "query_component",
                "pattern": "search-then-query",
                "rationale": "find components first, then get details"
            },
            {
                "tool": "read_file",
                "pattern": "search-then-read",
                "rationale": "find files of interest, then read them fully"
            }
        ],
        "context_validation": {
            "prerequisites": ["project directory exists", "have read permissions"],
            "post_conditions": ["matching code with context is in context"]
        },
        "common_error_patterns": [
            {
                "pattern": "no matches found",
                "meaning": "Search text doesn't appear or pattern is too specific",
                "solution": "try more general terms or different variations"
            },
            {
                "pattern": "too many matches",
                "meaning": "Search term is too common",
                "solution": "use more specific search text or filter by file_pattern"
            }
        ],
        "execution_examples": [
            {
                "intent": "Find all usages of a function",
                "parameters": {
                    "project_path": "/path/to/project",
                    "search_text": "authenticate_user", 
                    "file_pattern": "*.py"
                },
                "success_pattern": "Returns files and line numbers with matches",
                "follow_up": "examine specific usages in detail"
            }
        ]
    }
}

def update_registry(tool_ref_path: str, updated_tools: List[str]) -> None:
    """
    Update the registry.json file to mark profiles as created.
    
    Args:
        tool_ref_path: Path to the .tool_reference directory
        updated_tools: List of tools that have profiles created
    """
    registry_path = os.path.join(tool_ref_path, "registry.json")
    
    if not os.path.exists(registry_path):
        logger.error(f"Registry file not found at {registry_path}")
        return
    
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # Update profile status
        for tool in updated_tools:
            if tool in registry["tools"]:
                registry["tools"][tool]["has_profile"] = True
        
        # Update timestamp
        from datetime import datetime
        registry["last_updated"] = datetime.now().isoformat()
        
        # Write updated registry
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
        
        logger.info(f"Updated registry for {len(updated_tools)} tools")
    except Exception as e:
        logger.error(f"Error updating registry: {str(e)}")

def create_tool_profile(tool_ref_path: str, tool_name: str) -> bool:
    """
    Create a detailed tool profile.
    
    Args:
        tool_ref_path: Path to the .tool_reference directory
        tool_name: Name of the tool to create a profile for
        
    Returns:
        True if profile was created successfully, False otherwise
    """
    if tool_name not in TOOL_PROFILES:
        logger.warning(f"No profile template for {tool_name}")
        return False
    
    profile_dir = os.path.join(tool_ref_path, "tool_profiles")
    os.makedirs(profile_dir, exist_ok=True)
    
    profile_path = os.path.join(profile_dir, f"{tool_name}.json")
    
    try:
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(TOOL_PROFILES[tool_name], f, indent=2)
        logger.info(f"Created tool profile for {tool_name}")
        return True
    except Exception as e:
        logger.error(f"Error creating profile for {tool_name}: {str(e)}")
        return False

def main():
    """Main function to generate tool profiles."""
    parser = argparse.ArgumentParser(description="Generate detailed tool profiles for the AI-optimized Tool Index")
    parser.add_argument(
        "--project-path", 
        type=str, 
        default=".",
        help="Path to the project directory (default: current directory)"
    )
    parser.add_argument(
        "--tools",
        type=str,
        default=",".join(TOOL_PROFILES.keys()),
        help="Comma-separated list of tools to create profiles for (default: all available tools)"
    )
    
    args = parser.parse_args()
    project_path = os.path.abspath(args.project_path)
    tool_ref_path = os.path.join(project_path, ".tool_reference")
    
    if not os.path.exists(tool_ref_path):
        logger.error(f".tool_reference directory not found at {tool_ref_path}")
        logger.error("Please run the tool_index_generator.py script first")
        return 1
    
    requested_tools = [t.strip() for t in args.tools.split(",") if t.strip()]
    
    try:
        # Create profiles for each tool
        created_tools = []
        for tool in requested_tools:
            if create_tool_profile(tool_ref_path, tool):
                created_tools.append(tool)
        
        # Update the registry
        if created_tools:
            update_registry(tool_ref_path, created_tools)
        
        print(f"✅ Successfully created {len(created_tools)} tool profiles")
        print("Tools with profiles:")
        for tool in created_tools:
            print(f"  - {tool}")
        
        print("\nThis completes Phase 2 of the Tool Index implementation.")
        print("\nNext steps:")
        print("1. Review the created tool profiles")
        print("2. Proceed to Phase 3: Implementing relationship mappings")
        
        return 0
    except Exception as e:
        logger.error(f"Error creating tool profiles: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
