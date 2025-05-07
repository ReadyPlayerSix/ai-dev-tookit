"""
AI Librarian Indexer

This module provides utilities for indexing codebases and generating the AI Librarian 
reference system.

IMPORTANT: This is the basic indexer which is now DEPRECATED in favor of enhanced_indexer.py.
All new code should use enhanced_indexer.py which provides more comprehensive analysis.
This module is maintained for backward compatibility only.
"""

import os
import sys
import warnings
from typing import Dict, List, Set, Any, Optional, Tuple

# Import everything from enhanced_indexer
from .enhanced_indexer import (
    scan_directory,
    parse_python_file as enhanced_parse_python_file,
    extract_function_info,
    extract_attribute_path,
    extract_assignment_value,
    find_end_line,
    extract_code_snippet,
    analyze_dependencies,
    generate_mini_librarians,
    extract_project_info,
    generate_enhanced_component_registry,
    generate_diagnostics,
    initialize_enhanced_librarian
)

# Show deprecation warning
warnings.warn(
    "The basic indexer.py module is deprecated and will be removed in a future version. "
    "Please use enhanced_indexer.py instead.",
    DeprecationWarning,
    stacklevel=2
)

def parse_python_file(file_path: str) -> Dict[str, List[str]]:
    """
    Parse a Python file and extract its structure.
    (Legacy implementation for backward compatibility)
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Dictionary containing classes and functions in the file
    """
    try:
        # Use the enhanced parser but simplify the result
        enhanced_info = enhanced_parse_python_file(file_path)
        
        # Convert to the simpler format expected by legacy code
        return {
            "classes": list(enhanced_info.get("classes", {}).keys()),
            "functions": list(enhanced_info.get("functions", {}).keys()),
            "imports": [imp.get("name", "") for imp in enhanced_info.get("imports", [])]
        }
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return {
            "classes": [],
            "functions": [],
            "imports": []
        }

def generate_mini_librarian(file_path: str, file_info: Dict[str, List[str]], output_dir: str) -> str:
    """
    Generate a mini-librarian JSON file for a Python file.
    (Legacy implementation for backward compatibility)
    
    Args:
        file_path: Path to the Python file
        file_info: Dictionary containing file information (classes, functions)
        output_dir: Directory where the mini-librarian should be saved
        
    Returns:
        Path to the generated mini-librarian file
    """
    # Create a relative path for the mini-librarian
    rel_path = os.path.relpath(file_path, os.path.dirname(output_dir))
    rel_path = rel_path.replace('\\', '/')
    
    # Create output path
    mini_librarian_path = os.path.join(
        output_dir, 
        f"{rel_path.replace('/', '_').replace('.', '_')}.json"
    )
    
    # Add file description
    description = f"Mini-librarian for {rel_path}"
    
    # Create the mini-librarian content
    mini_librarian = {
        "file_path": rel_path,
        "classes": file_info["classes"],
        "functions": file_info["functions"],
        "imports": file_info["imports"],
        "description": description
    }
    
    # Write the mini-librarian
    os.makedirs(os.path.dirname(mini_librarian_path), exist_ok=True)
    import json
    with open(mini_librarian_path, 'w', encoding='utf-8') as f:
        json.dump(mini_librarian, f, indent=2)
    
    return os.path.relpath(mini_librarian_path, output_dir)

def generate_script_index(files_info: Dict[str, Dict], output_file: str) -> None:
    """
    Generate the script index file.
    (Legacy implementation for backward compatibility)
    
    Args:
        files_info: Dictionary containing information about all files
        output_file: Path where the script index should be saved
    """
    import json
    script_index = {"files": {}, "version": "0.1.0"}
    
    for file_path, info in files_info.items():
        rel_path = file_path.replace('\\', '/')
        script_index["files"][rel_path] = {
            "path": rel_path,
            "classes": info["file_info"]["classes"],
            "functions": info["file_info"]["functions"],
            "mini_librarian": info["mini_librarian_path"]
        }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(script_index, f, indent=2)

def generate_component_registry(files_info: Dict[str, Dict], output_file: str) -> None:
    """
    Generate the component registry file.
    (Legacy implementation for backward compatibility)
    
    Args:
        files_info: Dictionary containing information about all files
        output_file: Path where the component registry should be saved
    """
    import json
    components = {}
    
    # Collect all components
    for file_path, info in files_info.items():
        file_info = info["file_info"]
        rel_path = file_path.replace('\\', '/')
        
        # Add classes
        for class_name in file_info["classes"]:
            components[class_name] = {
                "type": "class",
                "file": rel_path,
                "references": []
            }
        
        # Add functions
        for func_name in file_info["functions"]:
            components[func_name] = {
                "type": "function",
                "file": rel_path,
                "references": []
            }
    
    # Write the component registry
    registry = {
        "components": components,
        "version": "0.1.0"
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)

def initialize_librarian(project_path: str) -> Tuple[str, int, int]:
    """
    Initialize or update the AI Librarian for a project.
    (Legacy implementation - redirects to enhanced version)
    
    Args:
        project_path: Path to the project root
        
    Returns:
        Tuple containing (status message, file count, component count)
    """
    warnings.warn(
        "initialize_librarian() is deprecated. Please use initialize_enhanced_librarian() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # Simply redirect to the enhanced version
    return initialize_enhanced_librarian(project_path)

if __name__ == "__main__":
    # Simple example usage
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        print("Note: Using enhanced indexer since the basic indexer is deprecated.")
        message, file_count, component_count = initialize_enhanced_librarian(project_path)
        print(message)
        print(f"Found {component_count} components in {file_count} files")
    else:
        print("Usage: python indexer.py <project_path>")
