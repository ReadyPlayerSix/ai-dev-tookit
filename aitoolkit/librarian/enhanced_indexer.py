"""
Enhanced AI Librarian Indexer

This module provides advanced utilities for indexing codebases and generating a comprehensive
AI Librarian reference system with rich component relationships and context.
"""

import os
import json
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Any, Optional, Tuple, Union

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

def parse_python_file(file_path: str) -> Dict[str, Any]:
    """
    Parse a Python file and extract its detailed structure.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Dictionary containing detailed information about classes, functions,
        docstrings, and relationships in the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        classes = {}
        functions = {}
        imports = []
        constants = {}
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({"name": name.name, "line": node.lineno})
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    imports.append({
                        "name": f"{module}.{name.name}" if module else name.name,
                        "line": node.lineno
                    })
        
        # Extract classes with detailed information
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = {}
                class_vars = []
                
                # Get docstring
                docstring = None
                if (len(node.body) > 0 and 
                    isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, (ast.Str, ast.Constant))):
                    
                    if hasattr(node.body[0].value, 's'):  # Python < 3.8
                        docstring = node.body[0].value.s
                    else:  # Python >= 3.8
                        docstring = node.body[0].value.value
                
                # Get base classes
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(extract_attribute_path(base))
                    else:
                        bases.append("unknown_base")
                
                # Extract methods and class variables
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = extract_function_info(item, content)
                        methods[item.name] = method_info
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                class_vars.append({
                                    "name": target.id,
                                    "line": item.lineno
                                })
                
                classes[node.name] = {
                    "start_line": node.lineno,
                    "end_line": find_end_line(node, content),
                    "docstring": docstring,
                    "bases": bases,
                    "methods": methods,
                    "class_variables": class_vars,
                    "code_snippet": extract_code_snippet(content, node.lineno, find_end_line(node, content))
                }
        
        # Extract standalone functions
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = extract_function_info(node, content)
        
        # Extract constants
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        constants[target.id] = {
                            "line": node.lineno,
                            "value": extract_assignment_value(node.value)
                        }
        
        return {
            "path": file_path,
            "classes": classes,
            "functions": functions,
            "imports": imports,
            "constants": constants
        }
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return {
            "path": file_path,
            "error": str(e),
            "classes": {},
            "functions": {},
            "imports": [],
            "constants": {}
        }

def extract_function_info(node: ast.FunctionDef, content: str) -> Dict[str, Any]:
    """
    Extract detailed information about a function or method.
    
    Args:
        node: AST node for the function
        content: Source code content
    
    Returns:
        Dictionary with function details
    """
    # Get docstring
    docstring = None
    if (len(node.body) > 0 and 
        isinstance(node.body[0], ast.Expr) and 
        isinstance(node.body[0].value, (ast.Str, ast.Constant))):
        
        if hasattr(node.body[0].value, 's'):  # Python < 3.8
            docstring = node.body[0].value.s
        else:  # Python >= 3.8
            docstring = node.body[0].value.value
    
    # Get parameters
    parameters = []
    for arg in node.args.args:
        param = {"name": arg.arg}
        if hasattr(arg, 'annotation') and arg.annotation is not None:
            if isinstance(arg.annotation, ast.Name):
                param["type"] = arg.annotation.id
            elif isinstance(arg.annotation, ast.Attribute):
                param["type"] = extract_attribute_path(arg.annotation)
            elif isinstance(arg.annotation, ast.Subscript):
                param["type"] = "complex_type"
        parameters.append(param)
    
    # Get return type
    return_type = None
    if node.returns:
        if isinstance(node.returns, ast.Name):
            return_type = node.returns.id
        elif isinstance(node.returns, ast.Attribute):
            return_type = extract_attribute_path(node.returns)
        elif isinstance(node.returns, ast.Subscript):
            return_type = "complex_type"
    
    # Get function calls
    calls = []
    for child_node in ast.walk(node):
        if isinstance(child_node, ast.Call):
            call_name = "unknown"
            if isinstance(child_node.func, ast.Name):
                call_name = child_node.func.id
            elif isinstance(child_node.func, ast.Attribute):
                call_name = extract_attribute_path(child_node.func)
            
            calls.append({
                "name": call_name,
                "line": child_node.lineno
            })
    
    start_line = node.lineno
    end_line = find_end_line(node, content)
    
    return {
        "start_line": start_line,
        "end_line": end_line,
        "docstring": docstring,
        "parameters": parameters,
        "return_type": return_type,
        "calls": calls,
        "code_snippet": extract_code_snippet(content, start_line, end_line)
    }

def extract_attribute_path(node: ast.Attribute) -> str:
    """
    Extract the full path of an attribute (e.g., self.pattern_tracker.update).
    
    Args:
        node: AST node for the attribute
    
    Returns:
        String representation of the attribute path
    """
    if isinstance(node, ast.Attribute):
        value_path = "unknown"
        if isinstance(node.value, ast.Name):
            value_path = node.value.id
        elif isinstance(node.value, ast.Attribute):
            value_path = extract_attribute_path(node.value)
        return f"{value_path}.{node.attr}"
    elif isinstance(node, ast.Name):
        return node.id
    return "unknown"

def extract_assignment_value(node: ast.AST) -> Any:
    """
    Extract a simple representation of a value from an AST node.
    
    Args:
        node: AST node representing a value
    
    Returns:
        String or primitive representing the value
    """
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.List):
        return "list_value"
    elif isinstance(node, ast.Dict):
        return "dict_value"
    elif isinstance(node, ast.Name):
        return f"variable:{node.id}"
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            return f"call:{node.func.id}()"
        return "function_call"
    return "complex_value"

def find_end_line(node: ast.AST, content: str) -> int:
    """
    Find the end line number of a node.
    
    Args:
        node: AST node
        content: Source code content
    
    Returns:
        End line number
    """
    # First check if the node has an end_lineno attribute (Python 3.8+)
    if hasattr(node, 'end_lineno'):
        return node.end_lineno
    
    # Fallback method for older Python versions
    max_line = node.lineno
    for child in ast.walk(node):
        if hasattr(child, 'lineno'):
            max_line = max(max_line, child.lineno)
    
    # Add extra lines based on the indentation pattern
    lines = content.splitlines()
    if max_line < len(lines):
        node_line = lines[node.lineno - 1]
        node_indent = len(node_line) - len(node_line.lstrip())
        
        # Look for the next line with the same or less indentation
        current_line = max_line
        while current_line < len(lines):
            if current_line >= len(lines):
                break
            
            line = lines[current_line]
            if line.strip() and len(line) - len(line.lstrip()) <= node_indent:
                break
                
            current_line += 1
            
        max_line = current_line
    
    return max_line

def extract_code_snippet(content: str, start_line: int, end_line: int, context_lines: int = 2) -> str:
    """
    Extract a code snippet with surrounding context.
    
    Args:
        content: Source code content
        start_line: Starting line number
        end_line: Ending line number
        context_lines: Number of context lines before and after
    
    Returns:
        Code snippet as a string
    """
    lines = content.splitlines()
    
    # Adjust for list indexing (0-based)
    start_idx = max(0, start_line - 1 - context_lines)
    end_idx = min(len(lines), end_line + context_lines)
    
    return "\n".join(lines[start_idx:end_idx])

def analyze_dependencies(files_info: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Analyze dependencies between components.
    
    Args:
        files_info: Dictionary containing information about all files
    
    Returns:
        Dictionary mapping components to their dependencies
    """
    dependencies = {}
    
    # First, build a map of all components
    all_components = {}
    for file_path, info in files_info.items():
        for class_name in info.get("classes", {}):
            all_components[class_name] = {"file": file_path, "type": "class"}
        
        for func_name in info.get("functions", {}):
            all_components[func_name] = {"file": file_path, "type": "function"}
    
    # Then analyze dependencies
    for file_path, info in files_info.items():
        # Analyze class dependencies
        for class_name, class_info in info.get("classes", {}).items():
            class_deps = []
            
            # Base classes are dependencies
            for base in class_info.get("bases", []):
                if base in all_components:
                    class_deps.append(base)
            
            # Function calls in methods may be dependencies
            for method_name, method_info in class_info.get("methods", {}).items():
                for call in method_info.get("calls", []):
                    call_name = call.get("name")
                    if call_name in all_components:
                        class_deps.append(call_name)
            
            dependencies[class_name] = list(set(class_deps))
        
        # Analyze function dependencies
        for func_name, func_info in info.get("functions", {}).items():
            func_deps = []
            
            # Function calls may be dependencies
            for call in func_info.get("calls", []):
                call_name = call.get("name")
                if call_name in all_components:
                    func_deps.append(call_name)
            
            dependencies[func_name] = list(set(func_deps))
    
    return dependencies

def generate_mini_librarians(files_info: Dict[str, Dict[str, Any]], scripts_dir: str) -> Dict[str, str]:
    """
    Generate mini-librarian JSON files for all Python files.
    
    Args:
        files_info: Dictionary containing information about all files
        scripts_dir: Directory to store mini-librarian files
    
    Returns:
        Dictionary mapping file paths to mini-librarian paths
    """
    mini_librarians = {}
    
    for file_path, info in files_info.items():
        # Create a safe filename
        rel_path = os.path.relpath(file_path, os.path.dirname(scripts_dir))
        safe_filename = rel_path.replace('\\', '_').replace('/', '_').replace('.', '_') + '.json'
        
        # Create the full path
        mini_librarian_path = os.path.join(scripts_dir, safe_filename)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(mini_librarian_path), exist_ok=True)
        
        # Write the mini-librarian
        with open(mini_librarian_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2)
        
        # Store the relative path
        mini_librarians[file_path] = os.path.relpath(mini_librarian_path, os.path.dirname(scripts_dir))
    
    return mini_librarians

def extract_project_info(project_path: str, files_info: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract high-level project information.
    
    Args:
        project_path: Path to the project root
        files_info: Dictionary containing information about all files
    
    Returns:
        Dictionary with project information
    """
    # Count components
    total_classes = 0
    total_functions = 0
    
    for info in files_info.values():
        total_classes += len(info.get("classes", {}))
        total_functions += len(info.get("functions", {}))
    
    # Detect project type
    project_type = "unknown"
    for file_path, info in files_info.items():
        filename = os.path.basename(file_path)
        if filename == "setup.py":
            project_type = "python_package"
        elif filename == "manage.py" and "django" in [imp.get("name") for imp in info.get("imports", [])]:
            project_type = "django"
        elif filename == "app.py" and "flask" in [imp.get("name") for imp in info.get("imports", [])]:
            project_type = "flask"
    
    # Detect main entry points
    entry_points = []
    for file_path, info in files_info.items():
        filename = os.path.basename(file_path)
        
        # Look for common entry point patterns
        if filename in ["main.py", "app.py", "run.py", "server.py"]:
            entry_points.append(file_path)
        
        # Check for __main__ block
        content = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '__name__ == "__main__"' in content or "__name__ == '__main__'" in content:
                entry_points.append(file_path)
        except:
            pass
    
    return {
        "project_name": os.path.basename(project_path),
        "project_type": project_type,
        "total_files": len(files_info),
        "total_classes": total_classes,
        "total_functions": total_functions,
        "entry_points": entry_points,
        "updated": datetime.now().isoformat()
    }

def generate_enhanced_component_registry(
    project_path: str, 
    files_info: Dict[str, Dict[str, Any]], 
    dependencies: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    Generate an enhanced component registry with relationships and responsibilities.
    
    Args:
        project_path: Path to the project root
        files_info: Dictionary containing information about all files
        dependencies: Dictionary mapping components to their dependencies
    
    Returns:
        Enhanced component registry
    """
    components = {}
    
    # Process all components
    for file_path, info in files_info.items():
        rel_path = os.path.relpath(file_path, project_path)
        rel_path = rel_path.replace('\\', '/')
        
        # Process classes
        for class_name, class_info in info.get("classes", {}).items():
            # Extract responsibility from docstring
            responsibilities = []
            if class_info.get("docstring"):
                docstring = class_info["docstring"]
                # Extract responsibilities using NLP-like heuristics
                responsibility_patterns = [
                    r"(?:responsible for|handles|manages|provides) ([^.]+)",
                    r"([^.]+(?:management|handling|processing))",
                ]
                
                for pattern in responsibility_patterns:
                    matches = re.findall(pattern, docstring, re.IGNORECASE)
                    responsibilities.extend(matches)
                
                # If no responsibility patterns matched, use the first sentence as a fallback
                if not responsibilities and "." in docstring:
                    first_sentence = docstring.split(".")[0].strip()
                    if first_sentence:
                        responsibilities.append(first_sentence)
            
            # If still no responsibilities, generate a generic one
            if not responsibilities:
                responsibilities = [f"Handles {class_name} operations"]
            
            components[class_name] = {
                "primary_file": os.path.join(project_path, rel_path),
                "description": class_info.get("docstring", "").split("\n")[0] if class_info.get("docstring") else f"{class_name} class",
                "responsibilities": responsibilities,
                "dependencies": dependencies.get(class_name, [])
            }
        
        # Process functions
        for func_name, func_info in info.get("functions", {}).items():
            # Extract responsibility from docstring
            description = ""
            if func_info.get("docstring"):
                docstring = func_info["docstring"]
                # Use the first line as description
                description = docstring.split("\n")[0].strip()
            
            components[func_name] = {
                "primary_file": os.path.join(project_path, rel_path),
                "description": description or f"{func_name} function",
                "dependencies": dependencies.get(func_name, [])
            }
    
    # Create workflow section
    workflow = {}
    
    # Look for entry points and main components
    for file_path, info in files_info.items():
        filename = os.path.basename(file_path)
        rel_path = os.path.relpath(file_path, project_path).replace('\\', '/')
        
        if filename in ["main.py", "app.py", "run.py", "server.py"]:
            workflow_name = filename.replace(".py", "")
            
            if "run" in workflow_name:
                workflow_name = "execution"
            elif "app" in workflow_name:
                workflow_name = "application"
            elif "server" in workflow_name:
                workflow_name = "server"
            
            workflow[workflow_name] = {
                "entry_point": rel_path,
                "description": f"Main {workflow_name} workflow"
            }
    
    # Add latest changes tracking
    latest_changes = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "Initial component registry generation",
        "changes": [
            "Created comprehensive component registry",
            "Identified component relationships and dependencies",
            "Analyzed component responsibilities from docstrings"
        ]
    }
    
    return {
        "components": components,
        "workflow": workflow,
        "latest_changes": latest_changes
    }

def generate_diagnostics(project_path: str, files_info: Dict[str, Dict[str, Any]], diagnostics_dir: str) -> None:
    """
    Generate diagnostic information for the project.
    
    Args:
        project_path: Path to the project root
        files_info: Dictionary containing information about all files
        diagnostics_dir: Directory to store diagnostic files
    """
    # Ensure the directory exists
    os.makedirs(diagnostics_dir, exist_ok=True)
    
    # Create a detailed README
    readme_path = os.path.join(diagnostics_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(f"""# Diagnostics Directory

This directory contains diagnostic information for the AI Librarian system.

## Purpose

The diagnostics system provides detailed information about the project structure,
component relationships, and potential issues in the codebase.

## Available Diagnostics

1. **Component Analysis** - Analysis of component relationships and dependencies
2. **Code Structure** - Overview of the project's structure and organization
3. **Potential Issues** - Documentation of potential code issues or improvements

## Usage

These diagnostic files are used by the AI Librarian to provide better context
and understanding of the codebase. They help Claude maintain awareness of the
project structure across conversations.

Last updated: {datetime.now().isoformat()}
""")
    
    # Create component analysis file
    component_analysis_path = os.path.join(diagnostics_dir, "component_analysis.md")
    with open(component_analysis_path, 'w', encoding='utf-8') as f:
        # Count component types
        class_count = 0
        function_count = 0
        
        for info in files_info.values():
            class_count += len(info.get("classes", {}))
            function_count += len(info.get("functions", {}))
        
        f.write(f"""# Component Analysis

## Overview

This project contains:
- {len(files_info)} Python files
- {class_count} classes
- {function_count} functions

## Key Components

""")
        
        # Add key components (those with many dependencies)
        component_deps = {}
        for file_path, info in files_info.items():
            for class_name in info.get("classes", {}):
                for method_info in info["classes"][class_name]["methods"].values():
                    for call in method_info.get("calls", []):
                        call_name = call.get("name")
                        if call_name not in component_deps:
                            component_deps[call_name] = 0
                        component_deps[call_name] += 1
            
            for func_info in info.get("functions", {}).values():
                for call in func_info.get("calls", []):
                    call_name = call.get("name")
                    if call_name not in component_deps:
                        component_deps[call_name] = 0
                    component_deps[call_name] += 1
        
        # Sort components by dependency count
        sorted_components = sorted(component_deps.items(), key=lambda x: x[1], reverse=True)
        
        # Write top 10 components
        for i, (component, count) in enumerate(sorted_components[:10]):
            f.write(f"{i+1}. **{component}** - Referenced {count} times\n")
    
    # Create code structure file
    code_structure_path = os.path.join(diagnostics_dir, "code_structure.md")
    with open(code_structure_path, 'w', encoding='utf-8') as f:
        f.write(f"""# Code Structure

## Project Organization

The project follows this general structure:

```
{os.path.basename(project_path)}/
""")
        
        # Build a simplified directory tree
        directories = set()
        for file_path in files_info.keys():
            rel_path = os.path.relpath(file_path, project_path)
            dir_path = os.path.dirname(rel_path)
            if dir_path:
                directories.add(dir_path)
        
        # Sort directories for consistent output
        sorted_dirs = sorted(directories)
        
        # Write directory tree
        for dir_path in sorted_dirs:
            # Calculate indentation level
            indent = "  " * len(dir_path.split(os.sep))
            f.write(f"{indent}├── {os.path.basename(dir_path)}/\n")
        
        f.write("```\n")

def initialize_enhanced_librarian(project_path: str) -> Tuple[str, int, int]:
    """
    Initialize or update an enhanced AI Librarian for a project.
    
    Args:
        project_path: Path to the project root
        
    Returns:
        Tuple containing (status message, file count, component count)
    """
    try:
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
        
        print(f"Scanning {len(python_files)} Python files...")
        for i, file_path in enumerate(python_files):
            if i % 20 == 0:
                print(f"Processed {i}/{len(python_files)} files...")
                
            file_info = parse_python_file(file_path)
            files_info[file_path] = file_info
            
            # Count components
            component_count += len(file_info.get("classes", {})) + len(file_info.get("functions", {}))
        
        # Analyze dependencies
        print("Analyzing component dependencies...")
        dependencies = analyze_dependencies(files_info)
        
        # Generate mini-librarians
        print("Generating mini-librarians...")
        mini_librarians = generate_mini_librarians(files_info, scripts_path)
        
        # Extract project info
        print("Extracting project information...")
        project_info = extract_project_info(project_path, files_info)
        
        # Generate enhanced component registry
        print("Generating enhanced component registry...")
        component_registry = generate_enhanced_component_registry(project_path, files_info, dependencies)
        
        # Write component registry
        registry_path = os.path.join(ai_ref_path, "component_registry.json")
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(component_registry, f, indent=2)
        
        # Generate script index
        script_index = {
            "files": {},
            "version": "0.2.0",
            "project_info": project_info
        }
        
        for file_path, mini_librarian_path in mini_librarians.items():
            rel_path = os.path.relpath(file_path, project_path).replace('\\', '/')
            
            # Extract classes and functions for quick reference
            file_info = files_info[file_path]
            script_index["files"][rel_path] = {
                "path": rel_path,
                "classes": list(file_info.get("classes", {}).keys()),
                "functions": list(file_info.get("functions", {}).keys()),
                "mini_librarian": mini_librarian_path
            }
        
        # Write script index
        script_index_path = os.path.join(ai_ref_path, "script_index.json")
        with open(script_index_path, 'w', encoding='utf-8') as f:
            json.dump(script_index, f, indent=2)
        
        # Generate diagnostics
        print("Generating diagnostics...")
        generate_diagnostics(project_path, files_info, diagnostics_path)
        
        # Create README
        readme_path = os.path.join(ai_ref_path, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"""# AI Librarian for {os.path.basename(project_path)}

This directory contains the AI Librarian reference system, which helps AI assistants 
understand and navigate the codebase effectively.

## Main Entry Points
{_format_entry_points(project_info.get("entry_points", []), project_path)}

## Key Components
{_format_key_components(component_registry)}

## Project Structure
- {len(files_info)} Python files
- {len(component_registry["components"])} components identified
- {project_info.get("total_classes", 0)} classes
- {project_info.get("total_functions", 0)} functions

## Recent Updates
- {component_registry["latest_changes"]["date"]}: {component_registry["latest_changes"]["description"]}
  {_format_changes(component_registry["latest_changes"]["changes"])}

Last updated: {datetime.now().isoformat()}
""")
        
        return (
            f"Enhanced AI Librarian generated for {len(files_info)} files",
            len(files_info),
            component_count
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error generating enhanced librarian: {str(e)}", 0, 0

def _format_entry_points(entry_points, project_path):
    """Format entry points for README."""
    if not entry_points:
        return "- No clear entry points identified"
    
    result = []
    for entry_point in entry_points:
        rel_path = os.path.relpath(entry_point, project_path).replace('\\', '/')
        result.append(f"- {rel_path}")
    
    return "\n".join(result)

def _format_key_components(component_registry):
    """Format key components for README."""
    components = component_registry.get("components", {})
    if not components:
        return "- No key components identified"
    
    # Sort components by number of dependencies
    sorted_components = sorted(
        components.items(),
        key=lambda x: len(x[1].get("dependencies", [])),
        reverse=True
    )
    
    result = []
    for name, info in sorted_components[:5]:  # Top 5 components
        description = info.get("description", "").split("\n")[0]
        result.append(f"- **{name}** - {description}")
    
    return "\n".join(result)

def _format_changes(changes):
    """Format changes for README."""
    if not changes:
        return ""
    
    return "\n  ".join(f"- {change}" for change in changes)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        print(f"Initializing enhanced AI Librarian for {project_path}")
        message, file_count, component_count = initialize_enhanced_librarian(project_path)
        print(message)
        print(f"Found {component_count} components in {file_count} files")
    else:
        print("Usage: python enhanced_indexer.py <project_path>")
