#!/usr/bin/env python3
"""
AI Librarian MCP Server

This is a standalone MCP server that implements the AI Librarian functionality,
providing code understanding and context maintenance across conversations.

Key Features:
- Code parsing and component tracking
- Project monitoring for changes
- Persistent context across conversations

Usage:
    python server.py [project_dir1] [project_dir2] ...
"""

import os
import sys
import json
import time
import atexit
import logging
import threading
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Set, Tuple

from mcp.server.fastmcp import FastMCP, Context

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_librarian.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ai-librarian")

# Create the MCP server with proper initialization
mcp = FastMCP(
    "ai-librarian",
    capabilities={
        "resources": {"subscribe": True, "listChanged": True},
        "tools": {"listChanged": True},
        "prompts": {"listChanged": True}
    }
)

# Global context for AI Librarian
librarian_context = {
    "projects": {},  # Map of project paths to their librarian info
    "active_projects": set(),  # Set of currently monitored projects
    "last_update": {},  # Map of project paths to last update timestamp
    "indexed_files": {},  # Map of project paths to their indexed files
    "components": {}  # Map of project paths to their component registries
}

# File change monitoring thread
monitoring_active = True

def monitor_projects():
    """
    Monitor active projects for file changes and update the AI Librarian context.
    This runs in a separate thread to provide real-time updates.
    """
    logger.info("Starting project monitoring thread")
    
    while monitoring_active:
        try:
            current_time = time.time()
            
            # Check each active project for changes
            for project_path in list(librarian_context["active_projects"]):
                if not os.path.exists(project_path):
                    logger.warning(f"Project path no longer exists: {project_path}")
                    librarian_context["active_projects"].remove(project_path)
                    continue
                    
                # Only check every 30 seconds per project to avoid excessive file system operations
                last_check = librarian_context["last_update"].get(project_path, 0)
                if current_time - last_check < 30:
                    continue
                    
                # Check for file changes
                has_changes = check_project_changes(project_path)
                if has_changes:
                    logger.info(f"Changes detected in project: {project_path}")
                    update_librarian_for_project(project_path)
                    
                librarian_context["last_update"][project_path] = current_time
                
            # Sleep to avoid high CPU usage
            time.sleep(5)
        except Exception as e:
            logger.error(f"Error in monitoring thread: {str(e)}")
            time.sleep(10)  # Sleep longer on error

def check_project_changes(project_path):
    """
    Check if a project has changes since the last update.
    
    Args:
        project_path: Path to the project root
        
    Returns:
        bool: True if changes detected, False otherwise
    """
    try:
        # Get currently indexed files
        indexed_files = librarian_context["indexed_files"].get(project_path, {})
        
        # Scan for Python files
        current_files = {}
        for root, _, files in os.walk(project_path):
            # Skip hidden directories and common excluded dirs
            if any(part.startswith('.') for part in Path(root).parts) or \
               any(part in ['venv', 'env', '__pycache__', 'node_modules'] for part in Path(root).parts):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        current_files[file_path] = mtime
                    except OSError:
                        pass
        
        # Check for added, removed, or modified files
        if set(indexed_files.keys()) != set(current_files.keys()):
            return True
            
        # Check for modified files
        for file_path, mtime in current_files.items():
            if file_path in indexed_files and indexed_files[file_path] != mtime:
                return True
                
        return False
    except Exception as e:
        logger.error(f"Error checking project changes: {str(e)}")
        return False

def update_librarian_for_project(project_path):
    """
    Update the AI Librarian for a project.
    
    Args:
        project_path: Path to the project root
    """
    try:
        # Update the librarian files
        message, file_count, component_count = initialize_librarian_internal(project_path)
        logger.info(f"Updated librarian for {project_path}: {message}")
        
        # Update our in-memory representation
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        
        # Read script index
        script_index_path = os.path.join(ai_ref_path, "script_index.json")
        if os.path.exists(script_index_path):
            with open(script_index_path, 'r', encoding='utf-8') as f:
                script_index = json.load(f)
                librarian_context["projects"][project_path] = script_index
        
        # Read component registry
        component_registry_path = os.path.join(ai_ref_path, "component_registry.json")
        if os.path.exists(component_registry_path):
            with open(component_registry_path, 'r', encoding='utf-8') as f:
                component_registry = json.load(f)
                librarian_context["components"][project_path] = component_registry
        
        # Update indexed files
        current_files = {}
        for root, _, files in os.walk(project_path):
            if any(part.startswith('.') for part in Path(root).parts) or \
               any(part in ['venv', 'env', '__pycache__', 'node_modules'] for part in Path(root).parts):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(file_path)
                        current_files[file_path] = mtime
                    except OSError:
                        pass
        
        librarian_context["indexed_files"][project_path] = current_files
    except Exception as e:
        logger.error(f"Error updating librarian for {project_path}: {str(e)}")

# Start the monitoring thread
monitoring_thread = threading.Thread(target=monitor_projects, daemon=True)
monitoring_thread.start()

# Register cleanup handler
def cleanup():
    global monitoring_active
    monitoring_active = False
    logger.info("Shutting down AI Librarian server")
    
    # Save any persistent state if needed
    state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_librarian_state.json")
    try:
        state = {
            "active_projects": list(librarian_context["active_projects"]),
            "last_update": librarian_context["last_update"]
        }
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving state: {str(e)}")

atexit.register(cleanup)

# Load previous state if available
state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_librarian_state.json")
if os.path.exists(state_file):
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
            librarian_context["active_projects"] = set(state.get("active_projects", []))
            librarian_context["last_update"] = state.get("last_update", {})
            
        # Reload active projects
        for project_path in list(librarian_context["active_projects"]):
            if os.path.exists(project_path):
                logger.info(f"Reloading project: {project_path}")
                update_librarian_for_project(project_path)
            else:
                logger.warning(f"Previously active project not found: {project_path}")
                librarian_context["active_projects"].remove(project_path)
    except Exception as e:
        logger.error(f"Error loading state: {str(e)}")

# Dictionary to store permission status of directories
permission_status = {}

# Parse directories from command line args
def initialize_allowed_directories():
    allowed_dirs = []
    
    # Check for directories in command line args
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if os.path.exists(arg):
                allowed_dirs.append(os.path.abspath(arg))
                logger.info(f"Added allowed directory from command line: {arg}")
    
    # Add the current directory as a fallback
    if not allowed_dirs:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        allowed_dirs.append(parent_dir)
        logger.info(f"Added parent directory: {parent_dir}")
    
    # Update our permission status tracker
    for dir_path in allowed_dirs:
        permission_status[dir_path] = True
    
    return allowed_dirs

# Get allowed directories
ALLOWED_DIRECTORIES = initialize_allowed_directories()

@mcp.tool()
def list_allowed_directories() -> str:
    """
    Returns the list of directories that this server is allowed to access.
    
    Returns:
        A list of allowed directory paths
    """
    return "Allowed directories:\n" + "\n".join(ALLOWED_DIRECTORIES)

@mcp.tool()
def check_project_access(project_path: str) -> str:
    """
    Check if the server has permission to access a specific project directory.
    This is required before initializing the AI Librarian for a project.
    
    Args:
        project_path: The project directory to check
        
    Returns:
        Status message about directory access
    """
    try:
        # Normalize the path
        project_path = os.path.abspath(project_path)
        
        # First check our permission tracker
        if project_path in permission_status and permission_status[project_path]:
            return f"✅ The server has permission to access: {project_path}\n\nYou can initialize the AI Librarian for this project."
        
        # Check if the path is within any of the allowed directories
        for allowed_dir in ALLOWED_DIRECTORIES:
            if project_path.startswith(allowed_dir) or allowed_dir.startswith(project_path):
                permission_status[project_path] = True
                return f"✅ The server has permission to access: {project_path}\n\nYou can initialize the AI Librarian for this project."
        
        # Try to access the directory
        if not os.path.exists(project_path):
            return f"❌ Directory does not exist: {project_path}"
        
        # Try to list the directory contents as a basic access test
        try:
            os.listdir(project_path)
            # If we get here, we have access
            permission_status[project_path] = True
            return f"✅ The server has permission to access: {project_path}\n\nYou can initialize the AI Librarian for this project."
        except PermissionError:
            permission_status[project_path] = False
            return f"❌ Permission denied: {project_path}\n\nPlease grant access to this directory in Claude Desktop:\n" + \
                   "1. Open Claude Desktop settings\n" + \
                   "2. Go to MCP Servers\n" + \
                   "3. Find 'AI Librarian'\n" + \
                   "4. Click 'Edit Permissions'\n" + \
                   f"5. Grant access to {project_path}"
    except Exception as e:
        logger.error(f"Error checking project access: {str(e)}")
        return f"❌ Error checking access: {str(e)}"

#-----------------------------------------------------------------
# AI Librarian Core Implementation
#-----------------------------------------------------------------

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

def initialize_librarian_internal(project_path: str) -> Tuple[str, int, int]:
    """
    Internal implementation of librarian initialization.
    
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

@mcp.tool()
def initialize_librarian(project_path: str) -> str:
    """
    Initialize the AI Librarian for a project.
    
    This tool creates the .ai_reference directory structure and builds a persistent
    context that Claude can access across conversations. After initialization, the
    project will be actively monitored for changes, automatically updating the context.
    
    Args:
        project_path: The root directory of the project
        
    Returns:
        A success message or error information
    """
    try:
        # Check permission first
        project_path = os.path.abspath(project_path)
        if project_path not in permission_status or not permission_status[project_path]:
            # Try to check access
            try:
                if not os.path.exists(project_path):
                    return f"❌ Directory does not exist: {project_path}"
                
                # Try to list the directory contents as a basic access test
                os.listdir(project_path)
                # If we get here, we have access
                permission_status[project_path] = True
            except PermissionError:
                return f"❌ Permission denied: {project_path}\n\nPlease grant access to this directory in Claude Desktop first:\n" + \
                       "1. Use check_project_access(\"{project_path}\") to verify access\n" + \
                       "2. If needed, edit Claude Desktop permissions settings"
        
        # Create the .ai_reference directory
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        os.makedirs(ai_ref_path, exist_ok=True)
        
        # Create subdirectories
        scripts_path = os.path.join(ai_ref_path, "scripts")
        diagnostics_path = os.path.join(ai_ref_path, "diagnostics")
        os.makedirs(scripts_path, exist_ok=True)
        os.makedirs(diagnostics_path, exist_ok=True)
        
        # Create README.md
        readme_content = """# AI Librarian

This directory contains the AI Librarian reference system for this project.
It helps AI assistants understand and navigate the codebase.

## Structure

- `component_registry.json` - Registry of all code components
- `script_index.json` - Index of all script files
- `scripts/` - Mini-librarians for individual scripts
- `diagnostics/` - Diagnostic information and troubleshooting

## Usage

The AI Librarian is automatically maintained by the AI Librarian MCP server.
Changes to your codebase will be tracked in real-time, maintaining context across conversations.
"""
        with open(os.path.join(ai_ref_path, "README.md"), 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Create component_registry.json
        component_registry = {"components": {}, "version": "0.1.0"}
        with open(os.path.join(ai_ref_path, "component_registry.json"), 'w', encoding='utf-8') as f:
            json.dump(component_registry, f, indent=2)
        
        # Create script_index.json
        script_index = {"files": {}, "version": "0.1.0"}
        with open(os.path.join(ai_ref_path, "script_index.json"), 'w', encoding='utf-8') as f:
            json.dump(script_index, f, indent=2)
        
        # Create a diagnostic README
        diag_readme = """# Diagnostics

This directory contains diagnostic information for the AI Librarian.
Diagnostic files help troubleshoot issues with code understanding and navigation.
"""
        with open(os.path.join(diagnostics_path, "README.md"), 'w', encoding='utf-8') as f:
            f.write(diag_readme)
        
        # Add project to active monitoring list
        librarian_context["active_projects"].add(project_path)
        librarian_context["last_update"][project_path] = time.time()
        
        # Run initial generation
        update_librarian_for_project(project_path)
        
        logger.info(f"Added project to active monitoring: {project_path}")
        
        return f"Successfully initialized AI Librarian at {ai_ref_path}\n\n" + \
               "Project is now being actively monitored for changes. Any updates to the codebase " + \
               "will be automatically detected and processed. Claude will maintain context awareness " + \
               "across conversations, allowing for more effective assistance with this project."
    except Exception as e:
        return f"Error initializing AI Librarian: {str(e)}"

@mcp.tool()
def query_component(project_path: str, component_name: str) -> str:
    """
    Query information about a specific component in the project.
    
    Args:
        project_path: The root directory of the project
        component_name: The name of the component to query
        
    Returns:
        Detailed information about the component
    """
    try:
        # Check if project is in our active monitoring
        if project_path in librarian_context["active_projects"]:
            logger.info(f"Using in-memory context for querying component: {component_name}")
        else:
            logger.info(f"Project not in active monitoring, checking disk: {project_path}")
            
        # Check if the AI Librarian exists
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        if not os.path.exists(ai_ref_path):
            return f"AI Librarian not initialized at {project_path}. Run initialize_librarian first."
        
        # Get script index - first check in-memory, then fallback to file
        script_index = None
        if project_path in librarian_context["projects"]:
            script_index = librarian_context["projects"][project_path]
            logger.info("Using in-memory script index")
        else:
            script_index_path = os.path.join(ai_ref_path, "script_index.json")
            if not os.path.exists(script_index_path):
                return f"Script index not found at {script_index_path}."
            
            with open(script_index_path, 'r', encoding='utf-8') as f:
                script_index = json.load(f)
                # Cache it for future use
                librarian_context["projects"][project_path] = script_index
        
        # Search for the component in all files
        results = []
        
        for file_path, file_info in script_index["files"].items():
            if (component_name in file_info.get("classes", []) or 
                component_name in file_info.get("functions", [])):
                
                # Read the mini-librarian for more details
                mini_librarian_path = os.path.join(ai_ref_path, file_info["mini_librarian"])
                if os.path.exists(mini_librarian_path):
                    with open(mini_librarian_path, 'r', encoding='utf-8') as f:
                        mini_librarian = json.load(f)
                    
                    # Check if the file exists
                    full_file_path = os.path.join(project_path, file_path)
                    if os.path.exists(full_file_path):
                        with open(full_file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                        
                        # Extract the component's code
                        import ast
                        try:
                            tree = ast.parse(file_content)
                            for node in ast.walk(tree):
                                if ((isinstance(node, ast.ClassDef) or isinstance(node, ast.FunctionDef)) and 
                                    node.name == component_name):
                                    
                                    # Get the component's source code
                                    start_line = node.lineno
                                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                                    
                                    # Extract line numbers and code
                                    lines = file_content.splitlines()
                                    component_code = "\n".join(lines[start_line-1:end_line])
                                    
                                    # Add to results
                                    results.append({
                                        "file_path": file_path,
                                        "component_type": "class" if isinstance(node, ast.ClassDef) else "function",
                                        "line_range": f"{start_line}-{end_line}",
                                        "code": component_code
                                    })
                        except Exception as e:
                            results.append({
                                "file_path": file_path,
                                "error": f"Error parsing file: {str(e)}"
                            })
        
        if not results:
            return f"Component '{component_name}' not found in the project."
        
        # Format the results
        formatted_results = []
        for result in results:
            formatted_results.append(f"File: {result['file_path']}")
            if "component_type" in result:
                formatted_results.append(f"Type: {result['component_type']}")
                formatted_results.append(f"Lines: {result['line_range']}")
                formatted_results.append("\nCode:")
                formatted_results.append(f"```python\n{result['code']}\n```")
            else:
                formatted_results.append(f"Error: {result['error']}")
            formatted_results.append("\n")
        
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Error querying component: {str(e)}"

@mcp.tool()
def find_implementation(project_path: str, search_text: str, file_pattern: str = None) -> str:
    """
    Find implementations containing the specified search text.
    
    Args:
        project_path: The root directory of the project
        search_text: The text to search for
        file_pattern: Optional pattern to filter files (e.g., "*.py")
        
    Returns:
        List of matching implementations with context
    """
    try:
        # Check if project is in active monitoring
        if project_path in librarian_context["active_projects"]:
            logger.info(f"Using in-memory context for searching: {search_text}")
            
        results = []
        search_text = search_text.lower()
        
        # Determine which extensions to search based on file_pattern
        extensions = []
        if file_pattern:
            if "*." in file_pattern:
                ext = file_pattern.split("*.")[-1]
                extensions.append(f".{ext}")
            elif "." in file_pattern:
                extensions.append(file_pattern)
        else:
            # Default to common code files
            extensions = [".py", ".js", ".ts", ".java", ".c", ".cpp", ".cs", ".go", ".rb", ".php"]
        
        # Function to check if a file should be searched
        def should_search_file(filename):
            if not extensions:
                return True
            return any(filename.endswith(ext) for ext in extensions)
        
        # Walk the directory tree
        for root, dirs, files in os.walk(project_path):
            # Skip hidden directories and common excluded directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in ['venv', 'env', 'node_modules', '__pycache__', '.git']]
            
            # Search files
            for filename in files:
                if should_search_file(filename):
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, project_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Search for the text
                        if search_text in content.lower():
                            # Find matching lines with context
                            lines = content.splitlines()
                            matches = []
                            
                            for i, line in enumerate(lines):
                                if search_text in line.lower():
                                    # Get context (3 lines before and after)
                                    start = max(0, i - 3)
                                    end = min(len(lines), i + 4)
                                    
                                    # Format the context
                                    context = []
                                    for j in range(start, end):
                                        line_num = j + 1
                                        line_text = lines[j]
                                        # Highlight the matching line
                                        if j == i:
                                            context.append(f"{line_num:4d}* {line_text}")
                                        else:
                                            context.append(f"{line_num:4d}  {line_text}")
                                    
                                    matches.append("\n".join(context))
                            
                            if matches:
                                results.append({
                                    "file": rel_path,
                                    "matches": matches
                                })
                    except UnicodeDecodeError:
                        # Skip binary files
                        pass
                    except Exception as e:
                        results.append({
                            "file": rel_path,
                            "error": str(e)
                        })
        
        # Format the results
        if not results:
            return f"No matches found for '{search_text}'"
        
        formatted_results = []
        for result in results:
            formatted_results.append(f"File: {result['file']}")
            if "matches" in result:
                for i, match in enumerate(result["matches"]):
                    if i > 0:
                        formatted_results.append("---")
                    formatted_results.append(match)
            else:
                formatted_results.append(f"Error: {result['error']}")
            formatted_results.append("\n")
        
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Error finding implementation: {str(e)}"

@mcp.tool()
def generate_librarian(project_path: str) -> str:
    """
    Generate or update the AI Librarian for a project.
    
    Args:
        project_path: The root directory of the project
        
    Returns:
        A success message with statistics or error information
    """
    try:
        # Check if the AI Librarian exists
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        if not os.path.exists(ai_ref_path):
            return f"AI Librarian not initialized at {project_path}. Run initialize_librarian first."
            
        # If project is not in active monitoring, add it
        if project_path not in librarian_context["active_projects"]:
            librarian_context["active_projects"].add(project_path)
            librarian_context["last_update"][project_path] = time.time()
            logger.info(f"Added project to active monitoring: {project_path}")
        
        # Force update the librarian
        update_librarian_for_project(project_path)
        
        # Get stats
        file_count = 0
        component_count = 0
        
        # Count components from in-memory representation
        if project_path in librarian_context["components"]:
            component_registry = librarian_context["components"][project_path]
            component_count = len(component_registry.get("components", {}))
            
        # Count files from in-memory representation
        if project_path in librarian_context["indexed_files"]:
            file_count = len(librarian_context["indexed_files"][project_path])
        
        return f"Successfully generated AI Librarian for {project_path}:\n" + \
               f"- {file_count} files indexed\n" + \
               f"- {component_count} components identified\n\n" + \
               "Project is now being actively monitored for changes. Claude will maintain " + \
               "context awareness across conversations."
    except Exception as e:
        return f"Error generating librarian: {str(e)}"

#-----------------------------------------------------------------
# Prompts
#-----------------------------------------------------------------

@mcp.prompt()
def ai_librarian_help() -> str:
    """
    Provide help with AI Librarian functionality.
    """
    return """
    The AI Librarian helps me understand your codebase better. Here's how to use it:
    
    1. Initialize: `initialize_librarian("path/to/project")`
    2. Query a component: `query_component("path/to/project", "ComponentName")`
    3. Find implementations: `find_implementation("path/to/project", "search text")`
    
    This creates metadata that persists across conversations, so I can better understand your code.
    """

#-----------------------------------------------------------------
# Main Function
#-----------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
