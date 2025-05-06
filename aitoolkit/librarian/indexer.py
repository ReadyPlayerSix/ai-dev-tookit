"""
AI Librarian Indexer

This module provides utilities for indexing codebases and generating the AI Librarian 
reference system.
"""

import os
import json
import ast
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple

def scan_directory(directory: str, exclude_dirs: Optional[List[str]] = None) -> List[str]:
    """
    Scan a directory for Python files.
    
    Args:
        directory: The directory to scan
        exclude_dirs: Optional list of directories to exclude
        
    Returns:
        List of paths to Python files
    """
    if exclude_dirs is None:
        exclude_dirs = ['venv', 'env', '.venv', '.env', '__pycache__', 'node_modules', '.git']
    
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def parse_python_file(file_path: str) -> Dict[str, List[str]]:
    """
    Parse a Python file and extract its structure.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Dictionary containing classes and functions in the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        classes = []
        functions = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    imports.append(f"{module}.{name.name}")
        
        return {
            "classes": classes,
            "functions": functions,
            "imports": imports
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
    with open(mini_librarian_path, 'w', encoding='utf-8') as f:
        json.dump(mini_librarian, f, indent=2)
    
    return os.path.relpath(mini_librarian_path, output_dir)

def generate_script_index(files_info: Dict[str, Dict], output_file: str) -> None:
    """
    Generate the script index file.
    
    Args:
        files_info: Dictionary containing information about all files
        output_file: Path where the script index should be saved
    """
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
    
    Args:
        files_info: Dictionary containing information about all files
        output_file: Path where the component registry should be saved
    """
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
    
    Args:
        project_path: Path to the project root
        
    Returns:
        Tuple containing (status message, file count, component count)
    """
    # Create the .ai_reference directory
    ai_ref_path = os.path.join(project_path, ".ai_reference")
    os.makedirs(ai_ref_path, exist_ok=True)
    
    # Create subdirectories
    scripts_path = os.path.join(ai_ref_path, "scripts")
    diagnostics_path = os.path.join(ai_ref_path, "diagnostics")
    os.makedirs(scripts_path, exist_ok=True)
    os.makedirs(diagnostics_path, exist_ok=True)
    
    # Scan Python files
    python_files = scan_directory(project_path)
    
    # Parse Python files
    files_info = {}
    component_count = 0
    
    for file_path in python_files:
        file_info = parse_python_file(file_path)
        
        # Generate mini-librarian
        mini_librarian_path = generate_mini_librarian(
            file_path, 
            file_info, 
            scripts_path
        )
        
        files_info[file_path] = {
            "file_info": file_info,
            "mini_librarian_path": mini_librarian_path
        }
        
        # Count components
        component_count += len(file_info["classes"]) + len(file_info["functions"])
    
    # Generate script index
    generate_script_index(
        files_info,
        os.path.join(ai_ref_path, "script_index.json")
    )
    
    # Generate component registry
    generate_component_registry(
        files_info,
        os.path.join(ai_ref_path, "component_registry.json")
    )
    
    return f"AI Librarian generated for {len(files_info)} files", len(files_info), component_count

if __name__ == "__main__":
    # Simple example usage
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        message, file_count, component_count = initialize_librarian(project_path)
        print(message)
        print(f"Found {component_count} components in {file_count} files")
    else:
        print("Usage: python indexer.py <project_path>")
