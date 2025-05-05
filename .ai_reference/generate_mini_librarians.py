#!/usr/bin/env python
import os
import ast
import json
import re
from datetime import datetime
from pathlib import Path

def analyze_python_file(file_path):
    """
    Analyze a Python file to extract classes, methods, and functions with line numbers.
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            
        # Parse the AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {
                "error": f"Syntax error in file: {str(e)}",
                "path": str(file_path)
            }
        
        # Initialize the result dictionary
        result = {
            "path": str(file_path),
            "imports": [],
            "classes": {},
            "functions": {},
            "constants": {}
        }
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    result["imports"].append({"name": name.name, "line": node.lineno})
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    result["imports"].append({
                        "name": f"{module}.{name.name}" if module else name.name,
                        "line": node.lineno
                    })
        
        # Extract classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "start_line": node.lineno,
                    "end_line": find_end_line(node, content),
                    "methods": {},
                    "class_variables": [],
                    "bases": []
                }
                
                # Extract bases (parent classes)
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        class_info["bases"].append(base.id)
                    else:
                        class_info["bases"].append("...")
                
                # Extract docstring
                if (len(node.body) > 0 and 
                    isinstance(node.body[0], ast.Expr)):
                    if hasattr(node.body[0].value, 'value') and isinstance(node.body[0].value.value, str):
                        class_info["docstring"] = node.body[0].value.value
                    elif hasattr(node.body[0].value, 's') and isinstance(node.body[0].value.s, str):
                        class_info["docstring"] = node.body[0].value.s
                
                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = extract_function_info(item, content)
                        class_info["methods"][item.name] = method_info
                    elif isinstance(item, ast.Assign):
                        # Class variables
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                class_info["class_variables"].append({
                                    "name": target.id,
                                    "line": item.lineno
                                })
                
                result["classes"][node.name] = class_info
        
        # Extract standalone functions
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                result["functions"][node.name] = extract_function_info(node, content)
        
        # Extract constants
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        result["constants"][target.id] = {
                            "line": node.lineno
                        }
        
        return result
    except Exception as e:
        return {
            "error": f"Error analyzing file: {str(e)}",
            "path": str(file_path)
        }

def extract_function_info(node, content):
    """Extract information about a function or method."""
    func_info = {
        "start_line": node.lineno,
        "end_line": find_end_line(node, content),
        "parameters": [],
        "return_type": None,
        "calls": []
    }
    
    # Extract docstring
    if (len(node.body) > 0 and isinstance(node.body[0], ast.Expr)):
        if hasattr(node.body[0].value, 'value') and isinstance(node.body[0].value.value, str):
            func_info["docstring"] = node.body[0].value.value
        elif hasattr(node.body[0].value, 's') and isinstance(node.body[0].value.s, str):
            func_info["docstring"] = node.body[0].value.s
    
    # Extract parameters
    for arg in node.args.args:
        param = {"name": arg.arg}
        if hasattr(arg, 'annotation') and arg.annotation is not None:
            if isinstance(arg.annotation, ast.Name):
                param["type"] = arg.annotation.id
        func_info["parameters"].append(param)
    
    # Extract return type annotation
    if node.returns:
        if isinstance(node.returns, ast.Name):
            func_info["return_type"] = node.returns.id
        elif isinstance(node.returns, ast.Subscript):
            # Handle more complex return types like List[str]
            func_info["return_type"] = "complex_type"
    
    # Extract function/method calls
    for child_node in ast.walk(node):
        if isinstance(child_node, ast.Call):
            if isinstance(child_node.func, ast.Name):
                func_info["calls"].append({
                    "name": child_node.func.id,
                    "line": child_node.lineno
                })
            elif isinstance(child_node.func, ast.Attribute):
                func_info["calls"].append({
                    "name": extract_attribute_path(child_node.func),
                    "line": child_node.lineno
                })
    
    # Extract code snippet (actual source code)
    func_info["code_snippet"] = extract_code_snippet(content, node.lineno, func_info["end_line"])
    
    return func_info

def extract_attribute_path(node):
    """Get the full path of an attribute (e.g., self.pattern_tracker.update)."""
    if isinstance(node, ast.Attribute):
        value_path = "..."
        if isinstance(node.value, ast.Name):
            value_path = node.value.id
        elif isinstance(node.value, ast.Attribute):
            value_path = extract_attribute_path(node.value)
        return f"{value_path}.{node.attr}"
    elif isinstance(node, ast.Name):
        return node.id
    return "..."

def find_end_line(node, content):
    """Find the end line number of a node."""
    # This is a simplification - for a more accurate end line,
    # we need to analyze the source code more carefully
    max_line = node.lineno
    for child in ast.walk(node):
        if hasattr(child, 'lineno'):
            max_line = max(max_line, child.lineno)
    
    # Add a few lines for closing brackets, etc.
    return max_line + 2  # Simple heuristic

def extract_code_snippet(content, start_line, end_line, context_lines=2):
    """Extract a code snippet with a few lines of context."""
    lines = content.splitlines()
    
    # Adjust for list indexing (0-based)
    start_idx = max(0, start_line - 1 - context_lines)
    end_idx = min(len(lines), end_line + context_lines)
    
    return "\n".join(lines[start_idx:end_idx])

def generate_mini_librarians():
    """Generate mini-librarians for all Python files in the project."""
    project_root = Path(__file__).parent.parent
    output_dir = Path(__file__).parent
    scripts_dir = output_dir / "scripts"
    
    # Clean up existing files before generation
    if scripts_dir.exists():
        print(f"Cleaning up existing librarian files in: {scripts_dir}")
        for old_file in scripts_dir.glob("*.json"):
            try:
                old_file.unlink()
            except Exception as e:
                print(f"Warning: Could not delete {old_file}: {e}")
    else:
        scripts_dir.mkdir(exist_ok=True)
    
    print(f"Generating mini-librarians for project at: {project_root}")
    print(f"Output directory: {scripts_dir}")
    
    # Maximum size for script_index.json in bytes (500KB)
    MAX_INDEX_SIZE = 500 * 1024
    
    # Collect all Python files
    python_files = list(project_root.glob("**/*.py"))
    
    # Dictionary to store metadata about all analyzed files
    central_index = {
        "files": {},
        "classes": {},
        "functions": {},
        "methods": {},
        "updated": datetime.now().isoformat()
    }
    
    # Process each file
    file_count = 0
    print(f"Found {len(python_files)} Python files")
    
    for file_path in python_files:
        relative_path = file_path.relative_to(project_root)
        
        # Skip files in certain directories
        if any(part.startswith('.') for part in relative_path.parts):
            continue
        if any(part in ('venv', 'env', '.git', '__pycache__') for part in relative_path.parts):
            continue
            
        try:
            # Analyze the file
            file_info = analyze_python_file(file_path)
            
            # Skip files with errors
            if "error" in file_info:
                print(f"Skipping file with error: {file_path} - {file_info['error']}")
                continue
                
            # Save mini-librarian for this file
            safe_filename = str(relative_path).replace('/', '_').replace('\\', '_').replace('.py', '.json')
            output_file = scripts_dir / safe_filename
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(file_info, f, indent=2)
            
            # Update central index
            relative_path_str = str(relative_path).replace('\\', '/')
            central_index["files"][relative_path_str] = {
                "path": relative_path_str,
                "classes": list(file_info["classes"].keys()),
                "functions": list(file_info["functions"].keys()),
                "mini_librarian": f"scripts/{safe_filename}"
            }
            
            # Map classes to files
            for class_name in file_info["classes"]:
                central_index["classes"][class_name] = {
                    "file": relative_path_str,
                    "start_line": file_info["classes"][class_name]["start_line"],
                    "end_line": file_info["classes"][class_name]["end_line"]
                }
                
                # Map methods to classes and files
                for method_name in file_info["classes"][class_name]["methods"]:
                    method_key = f"{class_name}.{method_name}"
                    central_index["methods"][method_key] = {
                        "file": relative_path_str,
                        "class": class_name,
                        "start_line": file_info["classes"][class_name]["methods"][method_name]["start_line"],
                        "end_line": file_info["classes"][class_name]["methods"][method_name]["end_line"]
                    }
            
            # Map functions to files
            for func_name in file_info["functions"]:
                central_index["functions"][func_name] = {
                    "file": relative_path_str,
                    "start_line": file_info["functions"][func_name]["start_line"],
                    "end_line": file_info["functions"][func_name]["end_line"]
                }
            
            file_count += 1
            if file_count % 50 == 0:
                print(f"Processed {file_count} files...")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Check index size before saving
    index_json = json.dumps(central_index, indent=2)
    index_size = len(index_json.encode('utf-8'))
    
    if index_size > MAX_INDEX_SIZE:
        print(f"Warning: script_index.json size ({index_size/1024:.1f}KB) exceeds limit of {MAX_INDEX_SIZE/1024:.1f}KB")
        print("Removing code_snippet fields to reduce size...")
        
        # Create reduced index with less verbose information
        reduced_index = {
            "files": central_index["files"],
            "classes": central_index["classes"],
            "functions": central_index["functions"],
            "methods": central_index["methods"],
            "updated": central_index["updated"],
            "size_reduced": True
        }
        
        # Check reduced size
        reduced_json = json.dumps(reduced_index, indent=2)
        reduced_size = len(reduced_json.encode('utf-8'))
        
        if reduced_size <= MAX_INDEX_SIZE:
            print(f"Reduced size to {reduced_size/1024:.1f}KB")
            # Save reduced index
            with open(output_dir / "script_index.json", 'w', encoding='utf-8') as f:
                f.write(reduced_json)
        else:
            # Still too large, save without indentation
            compact_json = json.dumps(reduced_index)
            compact_size = len(compact_json.encode('utf-8'))
            print(f"Further reduced size to {compact_size/1024:.1f}KB by removing indentation")
            with open(output_dir / "script_index.json", 'w', encoding='utf-8') as f:
                f.write(compact_json)
    else:
        # Save full index
        with open(output_dir / "script_index.json", 'w', encoding='utf-8') as f:
            f.write(index_json)
        print(f"Central index saved ({index_size/1024:.1f}KB)")
    
    print(f"Generated librarians for {file_count} files")
    print(f"Indexed {len(central_index['classes'])} classes and {len(central_index['functions'])} functions")
    print(f"Central index saved to: {output_dir / 'script_index.json'}")

if __name__ == "__main__":
    generate_mini_librarians()
