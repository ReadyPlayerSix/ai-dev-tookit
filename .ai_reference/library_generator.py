import os
import ast
import json
import re
from datetime import datetime
from pathlib import Path

def analyze_python_file(file_path):
    """
    Analyze a Python file to extract classes, methods, and functions with line numbers.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        dict: Structured information about the file contents
    """
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
                "end_line": get_end_line(node, content),
                "methods": {},
                "class_variables": [],
                "bases": [get_base_name(base) for base in node.bases]
            }
            
            # Extract docstring
            if (len(node.body) > 0 and 
                isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and
                isinstance(node.body[0].value.value, str)):
                class_info["docstring"] = node.body[0].value.value
            
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

def get_base_name(node):
    """Get the name of a base class from its AST node."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{get_attribute_path(node)}"
    else:
        return "..."

def extract_function_info(node, content):
    """Extract information about a function or method."""
    func_info = {
        "start_line": node.lineno,
        "end_line": get_end_line(node, content),
        "parameters": [],
        "return_type": None,
        "calls": []
    }
    
    # Extract docstring
    if (len(node.body) > 0 and 
        isinstance(node.body[0], ast.Expr) and 
        ((hasattr(node.body[0].value, 'value') and isinstance(node.body[0].value.value, str)) or
         (hasattr(node.body[0].value, 's') and isinstance(node.body[0].value.s, str)))):
        # Handle both Python 3.8+ (Constant) and older (Str)
        if hasattr(node.body[0].value, 'value'):
            func_info["docstring"] = node.body[0].value.value
        else:
            func_info["docstring"] = node.body[0].value.s
    
    # Extract parameters
    for arg in node.args.args:
        param = {"name": arg.arg}
        if hasattr(arg, 'annotation') and arg.annotation is not None:
            if isinstance(arg.annotation, ast.Name):
                param["type"] = arg.annotation.id
            elif isinstance(arg.annotation, ast.Attribute):
                param["type"] = get_attribute_path(arg.annotation)
        func_info["parameters"].append(param)
    
    # Extract return type annotation
    if node.returns:
        if isinstance(node.returns, ast.Name):
            func_info["return_type"] = node.returns.id
        elif isinstance(node.returns, ast.Attribute):
            func_info["return_type"] = get_attribute_path(node.returns)
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
                    "name": f"{get_attribute_path(child_node.func)}",
                    "line": child_node.lineno
                })
    
    # Extract code snippet (actual source code)
    func_info["code_snippet"] = extract_code_snippet(content, node.lineno, get_end_line(node, content))
    
    return func_info

def get_attribute_path(node):
    """Get the full path of an attribute (e.g., self.pattern_tracker.update)."""
    if isinstance(node, ast.Attribute):
        return f"{get_attribute_path(node.value)}.{node.attr}"
    elif isinstance(node, ast.Name):
        return node.id
    return "..."

def get_end_line(node, content):
    """Get the end line number of a node."""
    # This is a simplification - for a more accurate end line,
    # we need to analyze the source code more carefully
    max_line = node.lineno
    for child in ast.walk(node):
        if hasattr(child, 'lineno'):
            max_line = max(max_line, child.lineno)
    
    # Add a few lines for closing brackets, etc.
    content_lines = content.splitlines()
    current_line = max_line
    if current_line < len(content_lines):
        # Get the indentation of the current node
        node_line = content_lines[node.lineno - 1]
        node_indent = len(node_line) - len(node_line.lstrip())
        
        # Look for lines with same or less indentation to find the end
        while current_line < len(content_lines):
            line = content_lines[current_line]
            if line.strip() and len(line) - len(line.lstrip()) <= node_indent:
                break
            current_line += 1
        
        max_line = current_line
    
    return max_line

def extract_code_snippet(content, start_line, end_line, context_lines=2):
    """Extract a code snippet with a few lines of context."""
    lines = content.splitlines()
    
    # Adjust for list indexing (0-based)
    start_idx = max(0, start_line - 1 - context_lines)
    end_idx = min(len(lines), end_line + context_lines)
    
    return "\n".join(lines[start_idx:end_idx])

def generate_library(project_root, output_dir=".ai_reference"):
    """
    Generate mini-librarians for all Python files in the project.
    
    Args:
        project_root: Root directory of the project
        output_dir: Directory to store librarian files
    """
    project_path = Path(project_root)
    output_path = project_path / output_dir / "scripts"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Collect all Python files
    python_files = list(project_path.glob("**/*.py"))
    
    # Dictionary to store metadata about all analyzed files
    central_index = {
        "files": {},
        "classes": {},
        "functions": {},
        "methods": {},
        "cross_references": {},
        "updated": datetime.now().isoformat()
    }
    
    # Process each file
    total_files = len(python_files)
    print(f"Found {total_files} Python files to process")
    
    for i, file_path in enumerate(python_files, 1):
        if i % 50 == 0:
            print(f"Processing file {i}/{total_files}: {file_path}")
            
        relative_path = file_path.relative_to(project_path)
        
        # Skip files in certain directories
        if any(part.startswith('.') for part in relative_path.parts):
            continue
        if any(part in ('venv', 'env', '.git', '__pycache__') for part in relative_path.parts):
            continue
            
        try:
            # Analyze the file
            file_info = analyze_python_file(file_path)
            
            # Save mini-librarian for this file
            output_file = output_path / f"{str(relative_path).replace('/', '_').replace('\\', '_').replace('.py', '.json')}"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(file_info, f, indent=2)
            
            # Update central index
            relative_path_str = str(relative_path).replace("\\", "/")
            central_index["files"][relative_path_str] = {
                "path": relative_path_str,
                "classes": list(file_info["classes"].keys()),
                "functions": list(file_info["functions"].keys()),
                "mini_librarian": str(output_file.relative_to(project_path)).replace("\\", "/")
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
                
            # Process cross-references
            # We'll build these by analyzing the calls in a second pass
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Second pass to build cross-references
    print("Building cross-references...")
    for file_path in output_path.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_info = json.load(f)
                
            # Process functions
            for func_name, func_data in file_info.get("functions", {}).items():
                for call in func_data.get("calls", []):
                    call_name = call["name"]
                    if call_name not in central_index.get("cross_references", {}):
                        central_index["cross_references"][call_name] = []
                    
                    central_index["cross_references"][call_name].append({
                        "file": file_info["path"],
                        "line": call["line"],
                        "caller": func_name
                    })
            
            # Process methods
            for class_name, class_data in file_info.get("classes", {}).items():
                for method_name, method_data in class_data.get("methods", {}).items():
                    for call in method_data.get("calls", []):
                        call_name = call["name"]
                        if call_name not in central_index.get("cross_references", {}):
                            central_index["cross_references"][call_name] = []
                        
                        central_index["cross_references"][call_name].append({
                            "file": file_info["path"],
                            "line": call["line"],
                            "caller": f"{class_name}.{method_name}"
                        })
        except Exception as e:
            print(f"Error processing cross-references for {file_path}: {e}")
    
    # Save central index
    with open(project_path / output_dir / "script_index.json", 'w', encoding='utf-8') as f:
        json.dump(central_index, f, indent=2)
    
    print(f"Generated librarians for {len(central_index['files'])} files")
    print(f"Indexed {len(central_index['classes'])} classes and {len(central_index['functions'])} functions")
    
    # Update README to document the librarian system
    readme_path = project_path / output_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(f"""# AI Librarian System for isekaiZen

This directory contains the AI Librarian system, which helps the AI assistant efficiently navigate and understand the isekaiZen codebase.

## Components

1. **component_registry.json** - High-level component relationships and project overview
2. **script_index.json** - Central index of all Python files, classes, functions, and their relationships
3. **scripts/** - Directory containing detailed mini-librarians for each Python file
4. **library_generator.py** - Script to regenerate the librarian system when the codebase changes

## Usage

To update the librarian system after code changes:

```bash
cd {project_root}
python .ai_reference/library_generator.py
```

## Data Structure

- **script_index.json**: Contains mappings for files, classes, functions, methods, and cross-references
- **Mini-librarians**: Contain detailed information about each file, including code snippets

Last updated: {datetime.now().isoformat()}
""")

# Example usage
if __name__ == "__main__":
    import sys
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    generate_library(project_root)
