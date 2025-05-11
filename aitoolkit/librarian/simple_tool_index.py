#!/usr/bin/env python3
"""
Simple Tool Index

A streamlined, efficient tool indexer that creates a quick reference catalog
of available tools for Claude. This implementation replaces the multi-phase,
subprocess-based approach with a direct, single-pass indexing process.

Usage:
    from simple_tool_index import initialize_tool_index
    result = initialize_tool_index("/path/to/project")
"""

import os
import sys
import json
import inspect
import logging
import importlib
import importlib.util
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple-tool-index")

# Tool categories for organization
TOOL_CATEGORIES = {
    "filesystem": [
        "read_file", "write_file", "edit_file", "enhanced_edit_file",
        "search_files", "move_file", "directory_tree", "create_directory",
        "get_file_info", "read_multiple_files"
    ],
    "librarian": [
        "initialize_librarian", "query_component", "find_implementation",
        "generate_librarian", "find_related_files"
    ],
    "todo": [
        "add_todo", "list_todos", "update_todo_status",
        "add_subtask", "search_todos", "infer_todos"
    ],
    "server": [
        "list_allowed_directories", "check_project_access"
    ],
    "bookmarks": [
        "create_edit_bookmark", "get_bookmark_content", "update_bookmark",
        "apply_bookmark", "list_bookmarks", "remove_bookmark"
    ],
    "unified": [
        "get_unified_context", "build_cross_references",
        "find_related_tools", "find_related_components"
    ]
}

def extract_tool_metadata(func: Callable) -> Dict[str, Any]:
    """
    Extract metadata from a tool function using its docstring and signature.
    
    Args:
        func: The function to extract metadata from
        
    Returns:
        Dictionary containing the tool's metadata
    """
    # Get function signature
    sig = inspect.signature(func)
    
    # Extract docstring
    docstring = inspect.getdoc(func) or ""
    
    # Parse parameters
    parameters = {}
    for name, param in sig.parameters.items():
        if name == 'self':
            continue
            
        param_info = {
            "name": name,
            "required": param.default == inspect.Parameter.empty
        }
        
        # Try to determine type
        if param.annotation != inspect.Parameter.empty:
            param_info["type"] = str(param.annotation).replace("<class '", "").replace("'>", "")
        else:
            param_info["type"] = "unknown"
            
        # Add default value if present
        if param.default != inspect.Parameter.empty:
            param_info["default"] = param.default
            
        parameters[name] = param_info
    
    # Extract usage examples from docstring
    usage_examples = []
    if "Examples:" in docstring:
        example_section = docstring.split("Examples:")[1].strip()
        usage_examples = [example.strip() for example in example_section.split("\n\n")]
    
    # Create metadata
    metadata = {
        "id": func.__name__,
        "description": docstring.split("\n\n")[0] if docstring else "",
        "parameters": parameters,
        "return_type": str(sig.return_annotation).replace("<class '", "").replace("'>", "") 
                       if sig.return_annotation != inspect.Signature.empty else "unknown",
        "usage_examples": usage_examples,
        "category": next((cat for cat, tools in TOOL_CATEGORIES.items() 
                         if func.__name__ in tools), "other")
    }
    
    return metadata

def find_tool_modules(project_path: str) -> List[str]:
    """
    Find all potential tool modules in the project.
    
    Args:
        project_path: Path to the project
        
    Returns:
        List of module paths that likely contain tools
    """
    module_paths = []
    
    # Common locations for tool definitions
    potential_tool_dirs = [
        os.path.join(project_path, "aitoolkit/server/tools"),
        os.path.join(project_path, "src/mcp/server/tools"),
        os.path.join(project_path, "aitoolkit/mcp/tools"),
        os.path.join(project_path, "aitoolkit/librarian")
    ]
    
    for tool_dir in potential_tool_dirs:
        if os.path.exists(tool_dir):
            for root, dirs, files in os.walk(tool_dir):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        module_paths.append(os.path.join(root, file))
    
    return module_paths

def import_tool_function(module_path: str, function_name: str) -> Optional[Callable]:
    """
    Import a specific function from a module file.
    
    Args:
        module_path: Path to the module file
        function_name: Name of the function to import
        
    Returns:
        The imported function or None if not found
    """
    try:
        module_name = os.path.basename(module_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, function_name):
            return getattr(module, function_name)
            
        return None
    except Exception as e:
        logger.warning(f"Error importing {function_name} from {module_path}: {str(e)}")
        return None

def find_and_index_tools(project_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Find and index all tools in the project.
    
    Args:
        project_path: Path to the project
        
    Returns:
        Dictionary of tool metadata indexed by tool ID
    """
    tool_index = {}
    
    # Get all potential tool modules
    module_paths = find_tool_modules(project_path)
    
    # Flatten all tool categories into a single list
    all_tool_names = []
    for tools in TOOL_CATEGORIES.values():
        all_tool_names.extend(tools)
    
    # For each tool name, try to find and import it
    for tool_name in all_tool_names:
        found = False
        
        for module_path in module_paths:
            func = import_tool_function(module_path, tool_name)
            if func:
                try:
                    metadata = extract_tool_metadata(func)
                    tool_index[tool_name] = metadata
                    logger.info(f"Indexed tool: {tool_name}")
                    found = True
                    break
                except Exception as e:
                    logger.warning(f"Error extracting metadata for {tool_name}: {str(e)}")
        
        if not found:
            logger.warning(f"Could not find implementation for tool: {tool_name}")
    
    return tool_index

def initialize_tool_index(project_path: str) -> Dict[str, Any]:
    """
    Initialize the Tool Reference system for a project.
    
    This implementation creates a simple, flat reference catalog of tools
    that Claude can quickly access. Unlike the multi-phase approach, this
    performs all indexing in a single pass without subprocesses.
    
    Args:
        project_path: The root directory of the project
        
    Returns:
        Dictionary with the result of the operation
    """
    try:
        start_time = datetime.now()
        logger.info(f"Initializing tool index for {project_path}")
        
        # Normalize path
        project_path = os.path.abspath(project_path)
        
        if not os.path.exists(project_path):
            return {
                "status": "error",
                "message": f"Project path does not exist: {project_path}"
            }
        
        # Create .tool_reference directory
        tool_ref_path = os.path.join(project_path, ".tool_reference")
        os.makedirs(tool_ref_path, exist_ok=True)
        os.makedirs(os.path.join(tool_ref_path, "tool_profiles"), exist_ok=True)
        
        # Find and index tools
        tool_index = find_and_index_tools(project_path)
        
        # Create registry.json
        registry = {
            "version": "1.0.0",
            "description": "Simple Tool Reference Catalog for Claude",
            "last_updated": datetime.now().isoformat(),
            "tools": {
                tool_id: {
                    "id": tool_id,
                    "description": metadata.get("description", ""),
                    "category": metadata.get("category", "other"),
                    "profile_path": f"tool_profiles/{tool_id}.json",
                    "parameters_count": len(metadata.get("parameters", {}))
                }
                for tool_id, metadata in tool_index.items()
            }
        }
        
        # Write registry file
        registry_path = os.path.join(tool_ref_path, "registry.json")
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
        
        # Create categories.json
        categories = {
            "version": "1.0.0",
            "description": "Tool categorization for Claude",
            "categories": {
                category: {
                    "name": category,
                    "description": f"Tools related to {category} operations",
                    "tools": [tool for tool in tools if tool in tool_index]
                }
                for category, tools in TOOL_CATEGORIES.items()
                if any(tool in tool_index for tool in tools)
            }
        }
        
        # Write categories file
        categories_path = os.path.join(tool_ref_path, "categories.json")
        with open(categories_path, 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=2)
        
        # Write individual tool profiles
        for tool_id, metadata in tool_index.items():
            profile_path = os.path.join(tool_ref_path, "tool_profiles", f"{tool_id}.json")
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        
        # Create a README
        readme_content = """# Simple Tool Reference Catalog

This directory contains a streamlined, efficient tool reference catalog for Claude,
designed for quick lookups and easy maintenance.

## Structure
- `registry.json` - Master index of all tools
- `categories.json` - Categorization of tools by purpose
- `tool_profiles/` - Detailed metadata for each tool

This catalog helps Claude understand available tools, their parameters, and how
to use them effectively without unnecessary complexity.
"""
        readme_path = os.path.join(tool_ref_path, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Create result message
        tool_count = len(tool_index)
        result = {
            "status": "success",
            "message": f"Successfully initialized Simple Tool Index at {tool_ref_path}",
            "detail": f"Indexed {tool_count} tools across {len(categories['categories'])} categories in {duration:.2f} seconds",
            "tool_count": tool_count,
            "category_count": len(categories["categories"]),
            "duration_seconds": duration
        }
        
        logger.info(f"Tool index initialized with {tool_count} tools in {duration:.2f} seconds")
        return result
        
    except Exception as e:
        logger.error(f"Error initializing tool index: {str(e)}")
        import traceback
        return {
            "status": "error",
            "message": f"Error initializing tool index: {str(e)}",
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        result = initialize_tool_index(project_path)
        
        if result["status"] == "success":
            print(f"✅ {result['message']}")
            print(f"   {result['detail']}")
            sys.exit(0)
        else:
            print(f"❌ {result['message']}")
            sys.exit(1)
    else:
        print("Usage: python simple_tool_index.py <project_path>")
        sys.exit(1)
