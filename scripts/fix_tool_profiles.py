#!/usr/bin/env python3
"""
Fix Tool Profiles

This script creates tool profile files needed for the bidirectional references system.
"""

import os
import json
from pathlib import Path
import sys

def create_tool_profile(project_path, tool_name, profile_data):
    """Create a tool profile JSON file"""
    tool_ref_path = os.path.join(project_path, ".tool_reference")
    tool_profiles_path = os.path.join(tool_ref_path, "tool_profiles")
    
    # Ensure directory exists
    os.makedirs(tool_profiles_path, exist_ok=True)
    
    # Create profile file
    profile_path = os.path.join(tool_profiles_path, f"{tool_name}.json")
    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(profile_data, f, indent=2)
    
    print(f"Created profile for {tool_name}")
    
    # Update registry
    registry_path = os.path.join(tool_ref_path, "registry.json")
    if os.path.exists(registry_path):
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        if "tools" in registry and tool_name in registry["tools"]:
            registry["tools"][tool_name]["has_profile"] = True
            
            # Save updated registry
            with open(registry_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2)
            
            print(f"Updated registry for {tool_name}")

def main():
    """Main function"""
    project_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Define profile data for each tool
    profiles = {
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
            ]
        }
    }
    
    # Create tool profiles
    for tool_name, profile_data in profiles.items():
        create_tool_profile(project_path, tool_name, profile_data)
    
    print("\nCreated all required tool profiles.")
    print("You should now be able to run build_cross_references successfully.")

if __name__ == "__main__":
    main()
