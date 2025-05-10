#!/usr/bin/env python3
"""
Tool Relationships and Decision Trees Generator

This script creates detailed tool relationship maps and decision trees
for the AI-optimized Tool Index. It's the third phase of implementation,
focusing on how tools relate to each other and when to use specific tools.

Usage:
    python tool_relationships_generator.py [--project-path PATH]
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
        logging.FileHandler("tool_relationships_generator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("tool-relationships-generator")

# Define relationship groups
RELATIONSHIP_GROUPS = {
    "file_editing_workflow": {
        "group_name": "file_editing_workflow",
        "description": "Tools used in sequence for file editing operations",
        "tools": ["read_file", "edit_file", "write_file", "enhanced_edit_file"],
        "common_sequences": [
            {
                "sequence": ["read_file", "edit_file"],
                "purpose": "Make targeted modification to existing file",
                "frequency": "very_common"
            },
            {
                "sequence": ["search_files", "read_file", "edit_file"],
                "purpose": "Find files matching criteria, then modify them",
                "frequency": "common"
            },
            {
                "sequence": ["read_file", "enhanced_edit_file"],
                "purpose": "Make complex modifications with enhanced error handling",
                "frequency": "common"
            }
        ],
        "anti_patterns": [
            {
                "pattern": ["edit_file without read_file first"],
                "risk": "May overwrite important content without understanding current state",
                "recommendation": "Always read_file before edit_file"
            },
            {
                "pattern": ["read_file, edit_file with non-unique old_text"],
                "risk": "Ambiguous edit that may change wrong section",
                "recommendation": "Ensure old_text is unique in the file"
            }
        ]
    },
    
    "project_initialization_workflow": {
        "group_name": "project_initialization_workflow",
        "description": "Tools used to set up AI Librarian for a project",
        "tools": ["list_allowed_directories", "check_project_access", "initialize_librarian", "generate_librarian"],
        "common_sequences": [
            {
                "sequence": ["check_project_access", "initialize_librarian"],
                "purpose": "Verify access, then initialize AI Librarian",
                "frequency": "very_common"
            },
            {
                "sequence": ["initialize_librarian", "generate_librarian"],
                "purpose": "Set up and then refresh the AI Librarian data",
                "frequency": "common"
            }
        ],
        "anti_patterns": [
            {
                "pattern": ["initialize_librarian without check_project_access"],
                "risk": "May fail due to permission issues",
                "recommendation": "Always verify access first"
            },
            {
                "pattern": ["query_component without initialize_librarian"],
                "risk": "Will fail if Librarian not initialized",
                "recommendation": "Always initialize before querying"
            }
        ]
    },
    
    "code_understanding_workflow": {
        "group_name": "code_understanding_workflow",
        "description": "Tools used to analyze and understand code",
        "tools": ["query_component", "find_implementation", "read_file", "search_files"],
        "common_sequences": [
            {
                "sequence": ["search_files", "find_implementation"],
                "purpose": "Find relevant files, then search for specific code patterns",
                "frequency": "common"
            },
            {
                "sequence": ["find_implementation", "query_component"],
                "purpose": "Search for functionality, then get detailed information",
                "frequency": "very_common"
            },
            {
                "sequence": ["query_component", "read_file"],
                "purpose": "Find a component, then examine its full context",
                "frequency": "common"
            }
        ],
        "anti_patterns": [
            {
                "pattern": ["read every file manually"],
                "risk": "Inefficient use of context window",
                "recommendation": "Use find_implementation first to locate relevant code"
            }
        ]
    }
}

# Define decision trees
DECISION_TREES = {
    "filesystem_operations": {
        "tree_id": "filesystem_operations",
        "description": "Decision tree for selecting filesystem operation tools",
        "decision_nodes": [
            {
                "question": "operation_type",
                "options": [
                    {
                        "value": "read",
                        "next_question": "target_type"
                    },
                    {
                        "value": "write",
                        "next_question": "modify_or_create"
                    },
                    {
                        "value": "search",
                        "next_question": "search_scope"
                    }
                ]
            },
            {
                "question": "target_type",
                "options": [
                    {
                        "value": "file",
                        "recommendation": {
                            "tool": "read_file",
                            "confidence": "high"
                        }
                    },
                    {
                        "value": "directory",
                        "recommendation": {
                            "tool": "list_directory",
                            "confidence": "high"
                        }
                    }
                ]
            },
            {
                "question": "modify_or_create",
                "options": [
                    {
                        "value": "modify_existing",
                        "next_question": "modification_scope"
                    },
                    {
                        "value": "create_new",
                        "recommendation": {
                            "tool": "write_file",
                            "confidence": "high"
                        }
                    }
                ]
            },
            {
                "question": "modification_scope",
                "options": [
                    {
                        "value": "specific_segment",
                        "recommendation": {
                            "tool": "edit_file",
                            "confidence": "high"
                        }
                    },
                    {
                        "value": "complex_changes",
                        "recommendation": {
                            "tool": "enhanced_edit_file",
                            "confidence": "high"
                        }
                    },
                    {
                        "value": "entire_file",
                        "recommendation": {
                            "tool": "write_file",
                            "confidence": "high"
                        }
                    }
                ]
            },
            {
                "question": "search_scope",
                "options": [
                    {
                        "value": "single_directory",
                        "recommendation": {
                            "tool": "list_directory",
                            "confidence": "high"
                        }
                    },
                    {
                        "value": "recursive",
                        "recommendation": {
                            "tool": "search_files",
                            "confidence": "high"
                        }
                    }
                ]
            }
        ]
    },
    
    "code_analysis": {
        "tree_id": "code_analysis",
        "description": "Decision tree for selecting code analysis tools",
        "decision_nodes": [
            {
                "question": "analysis_goal",
                "options": [
                    {
                        "value": "find_specific_component",
                        "next_question": "know_component_name"
                    },
                    {
                        "value": "search_code_patterns",
                        "recommendation": {
                            "tool": "find_implementation",
                            "confidence": "high"
                        }
                    },
                    {
                        "value": "project_overview",
                        "recommendation": {
                            "tool": "generate_librarian",
                            "confidence": "medium"
                        }
                    }
                ]
            },
            {
                "question": "know_component_name",
                "options": [
                    {
                        "value": "yes",
                        "recommendation": {
                            "tool": "query_component",
                            "confidence": "high"
                        }
                    },
                    {
                        "value": "no",
                        "recommendation": {
                            "tool": "find_implementation",
                            "confidence": "high"
                        }
                    }
                ]
            }
        ]
    },
    
    "project_setup": {
        "tree_id": "project_setup",
        "description": "Decision tree for project setup operations",
        "decision_nodes": [
            {
                "question": "project_status",
                "options": [
                    {
                        "value": "new_project",
                        "next_question": "verify_access"
                    },
                    {
                        "value": "existing_project",
                        "next_question": "librarian_status"
                    }
                ]
            },
            {
                "question": "verify_access",
                "options": [
                    {
                        "value": "need_to_verify",
                        "recommendation": {
                            "tool": "check_project_access",
                            "confidence": "high"
                        }
                    },
                    {
                        "value": "access_confirmed",
                        "recommendation": {
                            "tool": "initialize_librarian",
                            "confidence": "high"
                        }
                    }
                ]
            },
            {
                "question": "librarian_status",
                "options": [
                    {
                        "value": "not_initialized",
                        "recommendation": {
                            "tool": "initialize_librarian",
                            "confidence": "high"
                        }
                    },
                    {
                        "value": "needs_update",
                        "recommendation": {
                            "tool": "generate_librarian",
                            "confidence": "high"
                        }
                    },
                    {
                        "value": "needs_verification",
                        "recommendation": {
                            "tool": "sanity_check",
                            "confidence": "medium"
                        }
                    }
                ]
            }
        ]
    }
}

# Define usage patterns
USAGE_PATTERNS = {
    "file_editing": {
        "pattern_id": "file_editing",
        "description": "Patterns for editing files effectively",
        "patterns": [
            {
                "name": "safe_edit_pattern",
                "description": "Safe pattern for editing files with verification",
                "steps": [
                    {
                        "step": 1,
                        "action": "Use search_files to locate relevant files",
                        "rationale": "Find the right files to edit first"
                    },
                    {
                        "step": 2,
                        "action": "Use read_file to get current content",
                        "rationale": "Understand the current state before making changes"
                    },
                    {
                        "step": 3,
                        "action": "Use edit_file with unique old_text",
                        "rationale": "Make targeted changes to specific portions"
                    },
                    {
                        "step": 4,
                        "action": "Use read_file again to verify changes",
                        "rationale": "Confirm changes were applied correctly"
                    }
                ]
            },
            {
                "name": "complex_edit_pattern",
                "description": "Pattern for complex edits with enhanced safety",
                "steps": [
                    {
                        "step": 1,
                        "action": "Use read_file to get current content",
                        "rationale": "Understand the current state"
                    },
                    {
                        "step": 2,
                        "action": "Use enhanced_edit_file for complex changes",
                        "rationale": "Better error handling and diff generation"
                    },
                    {
                        "step": 3,
                        "action": "Check the diff in the result",
                        "rationale": "Verify changes look correct"
                    }
                ]
            }
        ],
        "warning_signs": [
            "Multiple edits to the same file without verification",
            "Edits based on assumptions about file content",
            "Ambiguous old_text that could match multiple places"
        ]
    },
    
    "project_analysis": {
        "pattern_id": "project_analysis",
        "description": "Patterns for analyzing a project effectively",
        "patterns": [
            {
                "name": "top_down_analysis",
                "description": "Analyze project from high-level structure to details",
                "steps": [
                    {
                        "step": 1,
                        "action": "Use initialize_librarian to set up the librarian",
                        "rationale": "Required first step for project analysis"
                    },
                    {
                        "step": 2,
                        "action": "Use generate_librarian to create comprehensive index",
                        "rationale": "Build the component registry"
                    },
                    {
                        "step": 3,
                        "action": "Use query_component on key components",
                        "rationale": "Understand core parts of the system"
                    },
                    {
                        "step": 4, 
                        "action": "Use find_implementation to search for specific patterns",
                        "rationale": "Dive deeper into specific functionality"
                    }
                ]
            },
            {
                "name": "targeted_analysis",
                "description": "Analyze specific functionality across the project",
                "steps": [
                    {
                        "step": 1,
                        "action": "Use find_implementation with specific search terms",
                        "rationale": "Find where functionality is implemented"
                    },
                    {
                        "step": 2,
                        "action": "Use query_component on identified components",
                        "rationale": "Get detailed understanding of the components"
                    },
                    {
                        "step": 3,
                        "action": "Use read_file to examine full file context",
                        "rationale": "See how components fit into the broader file"
                    }
                ]
            }
        ],
        "warning_signs": [
            "Reading many files without a clear strategy",
            "Failing to initialize the librarian first",
            "Making conclusions based on incomplete code analysis"
        ]
    }
}

def create_relationship_groups(tool_ref_path: str) -> None:
    """
    Create detailed relationship group files.
    
    Args:
        tool_ref_path: Path to the .tool_reference directory
    """
    for group_id, group_data in RELATIONSHIP_GROUPS.items():
        group_path = os.path.join(tool_ref_path, f"relationship_{group_id}.json")
        
        try:
            with open(group_path, 'w', encoding='utf-8') as f:
                json.dump(group_data, f, indent=2)
            logger.info(f"Created relationship group: {group_id}")
        except Exception as e:
            logger.error(f"Error creating relationship group {group_id}: {str(e)}")

def create_decision_trees(tool_ref_path: str) -> None:
    """
    Create decision tree files.
    
    Args:
        tool_ref_path: Path to the .tool_reference directory
    """
    trees_dir = os.path.join(tool_ref_path, "decision_trees")
    os.makedirs(trees_dir, exist_ok=True)
    
    for tree_id, tree_data in DECISION_TREES.items():
        tree_path = os.path.join(trees_dir, f"{tree_id}.json")
        
        try:
            with open(tree_path, 'w', encoding='utf-8') as f:
                json.dump(tree_data, f, indent=2)
            logger.info(f"Created decision tree: {tree_id}")
        except Exception as e:
            logger.error(f"Error creating decision tree {tree_id}: {str(e)}")

def create_usage_patterns(tool_ref_path: str) -> None:
    """
    Create usage pattern files.
    
    Args:
        tool_ref_path: Path to the .tool_reference directory
    """
    patterns_dir = os.path.join(tool_ref_path, "usage_patterns")
    os.makedirs(patterns_dir, exist_ok=True)
    
    for pattern_id, pattern_data in USAGE_PATTERNS.items():
        pattern_path = os.path.join(patterns_dir, f"{pattern_id}.json")
        
        try:
            with open(pattern_path, 'w', encoding='utf-8') as f:
                json.dump(pattern_data, f, indent=2)
            logger.info(f"Created usage pattern: {pattern_id}")
        except Exception as e:
            logger.error(f"Error creating usage pattern {pattern_id}: {str(e)}")

def update_registry(tool_ref_path: str) -> None:
    """
    Update the registry.json file to include relationship mappings.
    
    Args:
        tool_ref_path: Path to the .tool_reference directory
    """
    registry_path = os.path.join(tool_ref_path, "registry.json")
    
    if not os.path.exists(registry_path):
        logger.error(f"Registry file not found at {registry_path}")
        return
    
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # Add relationship and decision tree information
        registry["relationships"] = {
            "groups": list(RELATIONSHIP_GROUPS.keys()),
            "decision_trees": list(DECISION_TREES.keys()),
            "usage_patterns": list(USAGE_PATTERNS.keys())
        }
        
        # Update timestamp
        from datetime import datetime
        registry["last_updated"] = datetime.now().isoformat()
        
        # Write updated registry
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
        
        logger.info("Updated registry with relationship information")
    except Exception as e:
        logger.error(f"Error updating registry: {str(e)}")

def main():
    """Main function to generate tool relationships and decision trees."""
    parser = argparse.ArgumentParser(description="Generate tool relationships and decision trees for the AI-optimized Tool Index")
    parser.add_argument(
        "--project-path", 
        type=str, 
        default=".",
        help="Path to the project directory (default: current directory)"
    )
    
    args = parser.parse_args()
    project_path = os.path.abspath(args.project_path)
    tool_ref_path = os.path.join(project_path, ".tool_reference")
    
    if not os.path.exists(tool_ref_path):
        logger.error(f".tool_reference directory not found at {tool_ref_path}")
        logger.error("Please run the tool_index_generator.py script first")
        return 1
    
    try:
        # Create relationship groups
        create_relationship_groups(tool_ref_path)
        
        # Create decision trees
        create_decision_trees(tool_ref_path)
        
        # Create usage patterns
        create_usage_patterns(tool_ref_path)
        
        # Update the registry
        update_registry(tool_ref_path)
        
        print(f"✅ Successfully created relationship mappings and decision trees")
        print("Created relationship groups:")
        for group_id in RELATIONSHIP_GROUPS.keys():
            print(f"  - {group_id}")
        
        print("\nCreated decision trees:")
        for tree_id in DECISION_TREES.keys():
            print(f"  - {tree_id}")
            
        print("\nCreated usage patterns:")
        for pattern_id in USAGE_PATTERNS.keys():
            print(f"  - {pattern_id}")
        
        print("\nThis completes Phase 3 of the Tool Index implementation.")
        print("\nNext steps:")
        print("1. Review the relationship mappings and decision trees")
        print("2. Proceed to Phase 4: Implementing context validation")
        
        return 0
    except Exception as e:
        logger.error(f"Error creating tool relationships: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
