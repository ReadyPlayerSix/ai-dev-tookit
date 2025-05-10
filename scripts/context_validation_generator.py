#!/usr/bin/env python3
"""
Context Validation Generator

This script creates self-diagnostic tools for Claude to validate its understanding
of the project structure and execution environment. It's the fourth phase of the
Tool Index implementation, focusing on ensuring Claude's context matches reality.

Usage:
    python context_validation_generator.py [--project-path PATH]
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
        logging.FileHandler("context_validation_generator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("context-validation-generator")

# Define context validation rules
CONTEXT_VALIDATORS = {
    "server_connection_validator": {
        "validator_id": "server_connection_validator",
        "description": "Validates which server implementation Claude is connected to",
        "validation_checks": [
            {
                "check_name": "server_identity_check",
                "check_description": "Verify which server implementation is active",
                "validation_method": {
                    "tool": "check_project_access",
                    "test_parameters": {"project_path": "."},
                    "success_pattern": "The server has permission to access",
                    "output_analysis": {
                        "if_contains": "ai-librarian",
                        "conclusion": "Connected to the AI Librarian server (librarian/server.py)",
                        "confidence": "high"
                    }
                },
                "corrective_action": "Update context to recognize connection to librarian/server.py"
            }
        ],
        "execution_frequency": "once_per_conversation",
        "validation_priority": "high"
    },
    
    "tool_path_validator": {
        "validator_id": "tool_path_validator",
        "description": "Validates the tool execution paths in Claude's understanding",
        "validation_checks": [
            {
                "check_name": "initialize_librarian_path_check",
                "check_description": "Verify that initialize_librarian is from librarian/server.py",
                "validation_method": {
                    "tool": "initialize_librarian",
                    "test_parameters": {"project_path": "."},
                    "success_pattern": "Successfully initialized AI Librarian",
                    "error_pattern": "Error initializing AI Librarian"
                },
                "corrective_action": "Update context to recognize initialize_librarian is from librarian/server.py"
            }
        ],
        "execution_frequency": "on_doubt",
        "validation_priority": "medium"
    },
    
    "project_structure_validator": {
        "validator_id": "project_structure_validator",
        "description": "Validates Claude's understanding of project structure",
        "validation_checks": [
            {
                "check_name": "directory_structure_check",
                "check_description": "Verify key directory structure understanding",
                "validation_method": {
                    "tool": "directory_tree",
                    "test_parameters": {"path": ".", "max_depth": 2},
                    "analyze": {
                        "check_existence": [
                            "aitoolkit/librarian",
                            "aitoolkit/gui",
                            "scripts"
                        ],
                        "confirm_relationships": [
                            {"parent": "aitoolkit", "child": "librarian"},
                            {"parent": "aitoolkit/librarian", "child": "server.py"}
                        ]
                    }
                },
                "corrective_action": "Update context to match actual project structure"
            }
        ],
        "execution_frequency": "on_explicit_request",
        "validation_priority": "medium"
    },
    
    "active_file_validator": {
        "validator_id": "active_file_validator",
        "description": "Validates that files Claude believes exist actually do",
        "validation_checks": [
            {
                "check_name": "unified_server_check",
                "check_description": "Verify understanding of unified_server.py vs librarian/server.py",
                "validation_method": {
                    "tool": "get_file_info",
                    "test_parameters": {"path": "aitoolkit/unified_server.py"},
                    "success_pattern": "Size: ",
                    "error_pattern": "Error",
                    "output_analysis": {
                        "if_success": "unified_server.py exists but is not currently used by Claude",
                        "if_error": "unified_server.py might have been moved to legacy"
                    }
                },
                "corrective_action": "Update understanding of which server file is active"
            },
            {
                "check_name": "librarian_server_check",
                "check_description": "Verify librarian/server.py status",
                "validation_method": {
                    "tool": "get_file_info",
                    "test_parameters": {"path": "aitoolkit/librarian/server.py"},
                    "success_pattern": "Size: ",
                    "error_pattern": "Error",
                    "output_analysis": {
                        "if_success": "librarian/server.py exists and is the active server Claude uses",
                        "if_error": "Critical error: active server file missing"
                    }
                },
                "corrective_action": "Confirm librarian/server.py is the active server implementation"
            }
        ],
        "execution_frequency": "on_doubt",
        "validation_priority": "high"
    },
    
    "tool_capability_validator": {
        "validator_id": "tool_capability_validator",
        "description": "Validates Claude's understanding of available tool capabilities",
        "validation_checks": [
            {
                "check_name": "todo_tools_check",
                "check_description": "Verify todo management tools are available",
                "validation_method": {
                    "tool": "list_todos",
                    "test_parameters": {"project_path": "."},
                    "analyze_response_type": {
                        "if_error_contains": "not initialized",
                        "conclusion": "Todo tools available but require initialization",
                        "confidence": "high"
                    }
                },
                "corrective_action": "Confirm todo management tools are available and require initialization"
            }
        ],
        "execution_frequency": "on_doubt",
        "validation_priority": "medium"
    }
}

# Define error analysis patterns
ERROR_ANALYZERS = {
    "common_tool_errors": {
        "analyzer_id": "common_tool_errors",
        "description": "Analyzes common error patterns when using tools",
        "error_patterns": [
            {
                "pattern": "AI Librarian not initialized",
                "diagnosis": "Attempting to use librarian tools before initialization",
                "solution": "Run initialize_librarian first",
                "prevention": "Always check if librarian is initialized before using query_component or find_implementation"
            },
            {
                "pattern": "Permission denied",
                "diagnosis": "Trying to access a path without permissions",
                "solution": "Run check_project_access to verify permissions",
                "prevention": "Always check permissions before file operations"
            },
            {
                "pattern": "Path not found",
                "diagnosis": "Referencing a non-existent file or directory",
                "solution": "Verify path exists using get_file_info or search_files",
                "prevention": "Verify paths before operations"
            },
            {
                "pattern": "The specified text segment was not found",
                "diagnosis": "Edit operation with non-existent text segment",
                "solution": "Read file first to verify content before editing",
                "prevention": "Always read_file before edit_file"
            },
            {
                "pattern": "The specified text segment appears multiple times",
                "diagnosis": "Ambiguous edit with non-unique text segment",
                "solution": "Use longer, more specific text segment",
                "prevention": "Ensure edit targets are unique"
            }
        ]
    },
    
    "context_mismatches": {
        "analyzer_id": "context_mismatches",
        "description": "Detects when Claude's understanding doesn't match reality",
        "mismatch_patterns": [
            {
                "pattern": "referencing unified_server.py as active",
                "diagnosis": "Confusion about which server implementation is active",
                "solution": "Run server_connection_validator to verify server",
                "prevention": "Remember librarian/server.py is the active server"
            },
            {
                "pattern": "expecting taskboard functionality to exist",
                "diagnosis": "Confusion about project state - taskboard not yet implemented",
                "solution": "Update context to recognize taskboard is planned but not implemented",
                "prevention": "Remember taskboard is a future feature"
            },
            {
                "pattern": "referencing incorrect file paths",
                "diagnosis": "Outdated or incorrect understanding of project structure",
                "solution": "Run project_structure_validator to update understanding",
                "prevention": "Verify paths before referring to them"
            }
        ]
    }
}

# Define execution tracers
EXECUTION_TRACERS = {
    "tool_execution_tracer": {
        "tracer_id": "tool_execution_tracer",
        "description": "Traces tool execution paths and patterns",
        "trace_targets": [
            {
                "tool": "initialize_librarian",
                "parameters_to_track": ["project_path"],
                "expected_pattern": "Creating .ai_reference directory structure",
                "execution_success_indicator": "Successfully initialized AI Librarian"
            },
            {
                "tool": "query_component",
                "parameters_to_track": ["component_name"],
                "expected_pattern": "Detailed component information",
                "execution_success_indicator": "Component found"
            },
            {
                "tool": "edit_file",
                "parameters_to_track": ["path", "old_text", "new_text"],
                "expected_pattern": "Replace specific text segment",
                "execution_success_indicator": "Successfully edited file"
            }
        ]
    }
}

def create_context_validators(tool_ref_path: str) -> None:
    """
    Create context validator files.
    
    Args:
        tool_ref_path: Path to the .tool_reference directory
    """
    validators_dir = os.path.join(tool_ref_path, "self_diagnostic")
    os.makedirs(validators_dir, exist_ok=True)
    
    for validator_id, validator_data in CONTEXT_VALIDATORS.items():
        validator_path = os.path.join(validators_dir, f"{validator_id}.json")
        
        try:
            with open(validator_path, 'w', encoding='utf-8') as f:
                json.dump(validator_data, f, indent=2)
            logger.info(f"Created context validator: {validator_id}")
        except Exception as e:
            logger.error(f"Error creating context validator {validator_id}: {str(e)}")

def create_error_analyzers(tool_ref_path: str) -> None:
    """
    Create error analyzer files.
    
    Args:
        tool_ref_path: Path to the .tool_reference directory
    """
    analyzers_dir = os.path.join(tool_ref_path, "self_diagnostic")
    os.makedirs(analyzers_dir, exist_ok=True)
    
    for analyzer_id, analyzer_data in ERROR_ANALYZERS.items():
        analyzer_path = os.path.join(analyzers_dir, f"{analyzer_id}.json")
        
        try:
            with open(analyzer_path, 'w', encoding='utf-8') as f:
                json.dump(analyzer_data, f, indent=2)
            logger.info(f"Created error analyzer: {analyzer_id}")
        except Exception as e:
            logger.error(f"Error creating error analyzer {analyzer_id}: {str(e)}")

def create_execution_tracers(tool_ref_path: str) -> None:
    """
    Create execution tracer files.
    
    Args:
        tool_ref_path: Path to the .tool_reference directory
    """
    tracers_dir = os.path.join(tool_ref_path, "self_diagnostic")
    os.makedirs(tracers_dir, exist_ok=True)
    
    for tracer_id, tracer_data in EXECUTION_TRACERS.items():
        tracer_path = os.path.join(tracers_dir, f"{tracer_id}.json")
        
        try:
            with open(tracer_path, 'w', encoding='utf-8') as f:
                json.dump(tracer_data, f, indent=2)
            logger.info(f"Created execution tracer: {tracer_id}")
        except Exception as e:
            logger.error(f"Error creating execution tracer {tracer_id}: {str(e)}")

def create_context_validator_tool(tool_ref_path: str) -> None:
    """
    Create the context validator tool script.
    
    Args:
        tool_ref_path: Path to the .tool_reference directory
    """
    script_content = """#!/usr/bin/env python3
'''
Context Validator Tool

This script validates Claude's understanding of the project structure,
tool paths, and execution environment. It helps Claude correct its
internal context to match reality.

Usage:
    python context_validator.py --check [all|server|tools|structure]
'''

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

def check_server_connection():
    '''Check which server implementation is active'''
    print("Checking server connection...")
    try:
        result = subprocess.run(
            [sys.executable, "-c", "from aitoolkit.librarian.server import mcp; print('AI Librarian server is active')"],
            capture_output=True,
            text=True
        )
        if "AI Librarian server is active" in result.stdout:
            print("✅ Connected to AI Librarian server (librarian/server.py)")
            return True
        else:
            print("❌ Not connected to AI Librarian server")
            return False
    except Exception as e:
        print(f"❌ Error checking server connection: {str(e)}")
        return False

def check_tool_paths():
    '''Check if tools are properly registered and accessible'''
    print("Checking tool paths...")
    tools_to_check = [
        "initialize_librarian",
        "query_component",
        "find_implementation"
    ]
    
    success_count = 0
    for tool in tools_to_check:
        try:
            result = subprocess.run(
                [sys.executable, "-c", f"from aitoolkit.librarian.server import {tool}; print('{tool} is available')"],
                capture_output=True,
                text=True
            )
            if f"{tool} is available" in result.stdout:
                print(f"✅ {tool} is properly registered and available")
                success_count += 1
            else:
                print(f"❌ {tool} is not properly registered")
        except Exception as e:
            print(f"❌ Error checking {tool}: {str(e)}")
    
    return success_count == len(tools_to_check)

def check_project_structure():
    '''Check if the project structure matches expectations'''
    print("Checking project structure...")
    
    expected_paths = [
        "aitoolkit/librarian/server.py",
        "aitoolkit/librarian/filesystem.py",
        "aitoolkit/librarian/enhanced_indexer.py",
        "aitoolkit/librarian/todos.py"
    ]
    
    success_count = 0
    for path in expected_paths:
        if os.path.exists(path):
            print(f"✅ {path} exists as expected")
            success_count += 1
        else:
            print(f"❌ {path} not found")
    
    return success_count == len(expected_paths)

def main():
    parser = argparse.ArgumentParser(description="Validate Claude's context understanding")
    parser.add_argument(
        "--check",
        choices=["all", "server", "tools", "structure"],
        default="all",
        help="What aspect of the context to check"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("=" * 80)
    print("                    Context Validator for Claude")
    print("=" * 80)
    print("")
    
    success = True
    
    if args.check in ["all", "server"]:
        server_success = check_server_connection()
        success = success and server_success
        print("")
    
    if args.check in ["all", "tools"]:
        tools_success = check_tool_paths()
        success = success and tools_success
        print("")
    
    if args.check in ["all", "structure"]:
        structure_success = check_project_structure()
        success = success and structure_success
        print("")
    
    # Print summary
    print("=" * 80)
    if success:
        print("✅ All checked aspects of Claude's context are valid")
    else:
        print("❌ Some context validation checks failed - Claude may need to update its understanding")
    print("=" * 80)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
"""
    
    script_path = os.path.join(os.path.dirname(tool_ref_path), "context_validator.py")
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Make script executable on Unix
        if os.name == 'posix':
            os.chmod(script_path, 0o755)
            
        logger.info(f"Created context validator tool at {script_path}")
    except Exception as e:
        logger.error(f"Error creating context validator tool: {str(e)}")

def update_registry(tool_ref_path: str) -> None:
    """
    Update the registry.json file to include context validation information.
    
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
        
        # Add context validation information
        registry["context_validation"] = {
            "validators": list(CONTEXT_VALIDATORS.keys()),
            "error_analyzers": list(ERROR_ANALYZERS.keys()),
            "execution_tracers": list(EXECUTION_TRACERS.keys()),
            "validator_tool": "context_validator.py"
        }
        
        # Update timestamp
        from datetime import datetime
        registry["last_updated"] = datetime.now().isoformat()
        
        # Write updated registry
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
        
        logger.info("Updated registry with context validation information")
    except Exception as e:
        logger.error(f"Error updating registry: {str(e)}")

def main():
    """Main function to generate context validation components."""
    parser = argparse.ArgumentParser(description="Generate context validation components for the AI-optimized Tool Index")
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
        # Create context validators
        create_context_validators(tool_ref_path)
        
        # Create error analyzers
        create_error_analyzers(tool_ref_path)
        
        # Create execution tracers
        create_execution_tracers(tool_ref_path)
        
        # Create context validator tool
        create_context_validator_tool(tool_ref_path)
        
        # Update the registry
        update_registry(tool_ref_path)
        
        print(f"✅ Successfully created context validation components")
        print("Created context validators:")
        for validator_id in CONTEXT_VALIDATORS.keys():
            print(f"  - {validator_id}")
        
        print("\nCreated error analyzers:")
        for analyzer_id in ERROR_ANALYZERS.keys():
            print(f"  - {analyzer_id}")
            
        print("\nCreated execution tracers:")
        for tracer_id in EXECUTION_TRACERS.keys():
            print(f"  - {tracer_id}")
        
        print("\nCreated context validator tool: context_validator.py")
        
        print("\nThis completes Phase 4 of the Tool Index implementation.")
        print("\nNext steps:")
        print("1. Test the context validator: python context_validator.py --check all")
        print("2. Review the self-diagnostic components")
        print("3. Integrate the Tool Index with your MCP server")
        
        return 0
    except Exception as e:
        logger.error(f"Error creating context validation components: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
