#!/usr/bin/env python3
"""
Unified MCP Server (AI Librarian + Filesystem)

This is a single unified MCP server that combines all capabilities:
- AI Librarian code understanding and context maintenance
- Complete filesystem operations
- AI-optimized todo system

It uses a module-level FastMCP instance and follows the pattern 
of the working AI Librarian server.
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
from typing import List, Dict, Any, Optional, Union, Set, Tuple, cast

# Add the project root to the path for proper imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try different import paths for FastMCP
try:
    # First try direct import from our connector module
    from aitoolkit.mcp.connector import FastMCP, Context
except ImportError:
    try:
        # Next try the pip-installed mcp package
        from mcp.server.fastmcp import FastMCP, Context
    except ImportError:
        # Finally try to install the package
        import subprocess
        print("Attempting to install mcp package...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp[cli]"])
            from mcp.server.fastmcp import FastMCP, Context
            print("Successfully installed and imported mcp package")
        except Exception as e:
            print(f"Error installing mcp package: {e}")
            # Create fallback classes as a last resort
            print("Using fallback FastMCP implementation")
            class Context:
                def __init__(self, request_context=None):
                    self.request_context = request_context or {}
            
            class FastMCP:
                def __init__(self, name, **kwargs):
                    self.name = name
                    self.version = kwargs.get('version', '0.1.0')
                    self.capabilities = kwargs.get('capabilities', {})
                
                def tool(self, **kwargs):
                    def decorator(func):
                        return func
                    return decorator
                
                def resource(self, pattern):
                    def decorator(func):
                        return func
                    return decorator
                
                def prompt(self, **kwargs):
                    def decorator(func):
                        return func
                    return decorator
                
                def run(self):
                    print(f"Starting fallback MCP server: {self.name}")

# Import our modules directly
# Create our own filesystem functions since this is integrated
# We will define them inline directly in this file

def read_file_tool(path: str) -> str:
    """Read the complete contents of a file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file_tool(path: str, content: str) -> str:
    """Write content to a file."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def list_directory_tool(path: str) -> str:
    """List the contents of a directory."""
    try:
        results = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            prefix = "[DIR]" if os.path.isdir(full_path) else "[FILE]"
            results.append(f"{prefix} {item}")
        return "\n".join(results)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def create_directory_tool(path: str) -> str:
    """Create a new directory."""
    try:
        os.makedirs(path, exist_ok=True)
        return f"Directory created: {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

def search_files_tool(path: str, pattern: str) -> str:
    """Search for files matching a pattern."""
    try:
        results = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if pattern.lower() in file.lower():
                    full_path = os.path.join(root, file)
                    results.append(full_path)
        return "\n".join(results) if results else f"No files found matching '{pattern}'"
    except Exception as e:
        return f"Error searching files: {str(e)}"

def get_file_info_tool(path: str) -> str:
    """Get detailed information about a file or directory."""
    try:
        if not os.path.exists(path):
            return f"Path does not exist: {path}"
            
        stat_info = os.stat(path)
        info = [
            f"Path: {path}",
            f"Type: {'Directory' if os.path.isdir(path) else 'File'}",
            f"Size: {stat_info.st_size} bytes",
            f"Created: {time.ctime(stat_info.st_ctime)}",
            f"Modified: {time.ctime(stat_info.st_mtime)}",
            f"Accessed: {time.ctime(stat_info.st_atime)}"
        ]
        return "\n".join(info)
    except Exception as e:
        return f"Error getting file info: {str(e)}"

def directory_tree_tool(path: str) -> str:
    """Generate a tree view of a directory."""
    try:
        result = []
        
        def generate_tree(dir_path, prefix=""):
            items = os.listdir(dir_path)
            items = sorted(items, key=lambda x: (os.path.isfile(os.path.join(dir_path, x)), x))
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                full_path = os.path.join(dir_path, item)
                
                # Add the current item
                marker = "└── " if is_last else "├── "
                type_prefix = "" if os.path.isdir(full_path) else ""
                result.append(f"{prefix}{marker}{type_prefix}{item}")
                
                # Recursively process directories
                if os.path.isdir(full_path):
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    generate_tree(full_path, next_prefix)
        
        result.append(os.path.basename(path))
        generate_tree(path, prefix="")
        return "\n".join(result)
    except Exception as e:
        return f"Error generating directory tree: {str(e)}"

from aitoolkit.librarian.todos import TodoManager
from aitoolkit.librarian.sanity_check import run_sanity_check
from aitoolkit.librarian.enhanced_indexer import initialize_enhanced_librarian

# Configure logging with separate handlers for file and console
logger = logging.getLogger("unified-server")
logger.setLevel(logging.INFO)
# Clear any existing handlers
if logger.handlers:
    logger.handlers.clear()

# File handler - all levels
file_handler = logging.FileHandler("unified_server.log")
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Console handler - only warnings and errors
console_handler = logging.StreamHandler(sys.stderr)  # Explicitly use stderr
console_handler.setLevel(logging.WARNING)  # Only show warnings and errors
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Create the MCP server at the module level - this is critical for proper operation
mcp = FastMCP(
    "AI Dev Toolkit",
    capabilities={
        "resources": {"subscribe": True, "listChanged": True},
        "tools": {"listChanged": True},
        "prompts": {"listChanged": True}
    }
)

# Thread synchronization lock
state_lock = threading.Lock()

# Global context for AI Librarian - using the same structure as the working server
librarian_context = {
    "projects": {},  # Map of project paths to their librarian info
    "active_projects": set(),  # Set of currently monitored projects
    "last_update": {},  # Map of project paths to last update timestamp
    "indexed_files": {},  # Map of project paths to their indexed files
    "components": {},  # Map of project paths to their component registries
    "paused": False   # Flag to temporarily pause monitoring
}

# Dictionary to store permission status of directories
permission_status = {}

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
            # Check if monitoring is paused
            with state_lock:
                if librarian_context["paused"]:
                    time.sleep(1)  # Short sleep when paused
                    continue
                
                current_time = time.time()
                # Make a copy of active projects to avoid modification during iteration
                active_projects = list(librarian_context["active_projects"])
            
            # Check each active project for changes
            for project_path in active_projects:
                if not os.path.exists(project_path):
                    with state_lock:
                        logger.warning(f"Project path no longer exists: {project_path}")
                        librarian_context["active_projects"].remove(project_path)
                    continue
                    
                # Only check every 30 seconds per project to avoid excessive file system operations
                with state_lock:
                    last_check = librarian_context["last_update"].get(project_path, 0)
                    
                if current_time - last_check < 30:
                    continue
                    
                # Check for file changes
                has_changes = check_project_changes(project_path)
                if has_changes:
                    with state_lock:
                        logger.info(f"Changes detected in project: {project_path}")
                        update_librarian_for_project(project_path)
                        librarian_context["last_update"][project_path] = current_time
                else:
                    with state_lock:
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
        with state_lock:
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
        # Use the enhanced_indexer module to update the librarian
        message, file_count, component_count = initialize_enhanced_librarian(project_path)
        logger.info(f"Updated librarian for {project_path}: {message}")
        
        # Update our in-memory representation
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        
        # Read script index
        script_index_path = os.path.join(ai_ref_path, "script_index.json")
        if os.path.exists(script_index_path):
            with open(script_index_path, 'r', encoding='utf-8') as f:
                script_index = json.load(f)
                with state_lock:
                    librarian_context["projects"][project_path] = script_index
        
        # Read component registry
        component_registry_path = os.path.join(ai_ref_path, "component_registry.json")
        if os.path.exists(component_registry_path):
            with open(component_registry_path, 'r', encoding='utf-8') as f:
                component_registry = json.load(f)
                with state_lock:
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
        
        with state_lock:
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
    logger.info("Shutting down unified server")
    
    # Save any persistent state if needed
    state_file = os.path.join(script_dir, "unified_server_state.json")
    try:
        with state_lock:
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
state_file = os.path.join(script_dir, "unified_server_state.json")
if os.path.exists(state_file):
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
            with state_lock:
                librarian_context["active_projects"] = set(state.get("active_projects", []))
                librarian_context["last_update"] = state.get("last_update", {})
            
        # Reload active projects
        for project_path in list(librarian_context["active_projects"]):
            if os.path.exists(project_path):
                logger.info(f"Reloading project: {project_path}")
                update_librarian_for_project(project_path)
            else:
                logger.warning(f"Previously active project not found: {project_path}")
                with state_lock:
                    librarian_context["active_projects"].remove(project_path)
    except Exception as e:
        logger.error(f"Error loading state: {str(e)}")

# Parse directories from command line args
def initialize_allowed_directories():
    allowed_dirs = []
    
    # Check for directories in environment variables
    if "AI_LIBRARIAN_ALLOWED_DIRS" in os.environ:
        env_dirs = os.environ["AI_LIBRARIAN_ALLOWED_DIRS"].split(",")
        for dir_path in env_dirs:
            if dir_path and os.path.exists(dir_path):
                allowed_dirs.append(os.path.abspath(dir_path))
                logger.info(f"Added allowed directory from environment: {dir_path}")
    
    # Check for directories in command line args
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if os.path.exists(arg) and arg not in allowed_dirs:
                allowed_dirs.append(os.path.abspath(arg))
                logger.info(f"Added allowed directory from command line: {arg}")
    
    # Add the current directory as a fallback
    if not allowed_dirs:
        current_dir = os.getcwd()
        allowed_dirs.append(current_dir)
        logger.info(f"Added current directory: {current_dir}")
    
    # Update our permission status tracker
    for dir_path in allowed_dirs:
        permission_status[dir_path] = True
    
    logger.info(f"Allowed directories: {allowed_dirs}")
    
    return allowed_dirs

# Get allowed directories
ALLOWED_DIRECTORIES = initialize_allowed_directories()

# Utility function to pause/resume monitoring during operations
def pause_monitoring():
    with state_lock:
        librarian_context["paused"] = True
        logger.debug("Monitoring paused")

def resume_monitoring():
    with state_lock:
        librarian_context["paused"] = False
        logger.debug("Monitoring resumed")

# Context manager for pausing monitoring
class MonitoringPauser:
    def __enter__(self):
        pause_monitoring()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        resume_monitoring()

#-----------------------------------------------------------------
# Tool Implementations - following module-level registration pattern
#-----------------------------------------------------------------

@mcp.tool()
def list_allowed_directories() -> List[str]:
    """
    Returns the list of directories that this server is allowed to access.
    
    Returns:
        A list of allowed directory paths
    """
    return ALLOWED_DIRECTORIES

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
                   "3. Find 'AI Dev Toolkit'\n" + \
                   "4. Click 'Edit Permissions'\n" + \
                   f"5. Grant access to {project_path}"
    except Exception as e:
        logger.error(f"Error checking project access: {str(e)}")
        return f"❌ Error checking access: {str(e)}"

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
    # Pause monitoring during this operation
    with MonitoringPauser():
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
            todos_path = os.path.join(ai_ref_path, "todos")
            os.makedirs(scripts_path, exist_ok=True)
            os.makedirs(diagnostics_path, exist_ok=True)
            os.makedirs(todos_path, exist_ok=True)
            
            # Create README.md
            readme_content = """# AI Librarian

This directory contains the AI Librarian reference system for this project.
It helps AI assistants understand and navigate the codebase.

## Structure

- `component_registry.json` - Registry of all code components
- `script_index.json` - Index of all script files
- `scripts/` - Mini-librarians for individual scripts
- `diagnostics/` - Diagnostic information and troubleshooting
- `todos/` - AI-optimized task tracking system

## Usage

The AI Librarian is automatically maintained by the AI Dev Toolkit server.
Changes to your codebase will be tracked in real-time, maintaining context across conversations.
"""
            with open(os.path.join(ai_ref_path, "README.md"), 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # Create component_registry.json
            component_registry = {
                "components": {},
                "version": "0.1.0",
                "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
            with open(os.path.join(ai_ref_path, "component_registry.json"), 'w', encoding='utf-8') as f:
                json.dump(component_registry, f, indent=2)
            
            # Create script_index.json
            script_index = {
                "files": {},
                "version": "0.1.0",
                "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S")
            }
            with open(os.path.join(ai_ref_path, "script_index.json"), 'w', encoding='utf-8') as f:
                json.dump(script_index, f, indent=2)
            
            # Create a diagnostic README
            diag_readme = """# Diagnostics

This directory contains diagnostic information for the AI Librarian.
Diagnostic files help troubleshoot issues with code understanding and navigation.
"""
            with open(os.path.join(diagnostics_path, "README.md"), 'w', encoding='utf-8') as f:
                f.write(diag_readme)
            
            # Create a todos README
            todos_readme = """# AI-Optimized Todo System

This directory contains the AI-optimized todo tracking system.
Todo items are stored in JSON format with rich metadata to help AI assistants
track and manage tasks across conversations.
"""
            with open(os.path.join(todos_path, "README.md"), 'w', encoding='utf-8') as f:
                f.write(todos_readme)
            
            # Initialize the todo manager
            todo_manager = TodoManager(project_path)
            # Check if todo_manager has setup method
            if hasattr(todo_manager, 'setup') and callable(getattr(todo_manager, 'setup')):
                todo_manager.setup()
            # If not, make sure the todos directory exists and create a basic todo list file if needed
            elif not os.path.exists(os.path.join(todos_path, "todo_list.json")):
                with open(os.path.join(todos_path, "todo_list.json"), 'w', encoding='utf-8') as f:
                    json.dump({
                        "version": "0.1.0",
                        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "items": []
                    }, f, indent=2)
            
            # Add project to active monitoring list
            with state_lock:
                librarian_context["active_projects"].add(project_path)
                librarian_context["last_update"][project_path] = time.time()
            
            # Run initial generation
            update_librarian_for_project(project_path)
            
            logger.info(f"Added project to active monitoring: {project_path}")
            
            # Run diagnostic checks to verify librarian functionality
            diagnostic_results = run_librarian_diagnostics(project_path)
            
            return f"Successfully initialized AI Librarian at {ai_ref_path}\n\n" + \
                   "Project is now being actively monitored for changes. Any updates to the codebase " + \
                   "will be automatically detected and processed. Claude will maintain context awareness " + \
                   "across conversations, allowing for more effective assistance with this project.\n\n" + \
                   diagnostic_results
        except Exception as e:
            logger.error(f"Error initializing AI Librarian: {str(e)}")
            return f"Error initializing AI Librarian: {str(e)}"

@mcp.tool()
def query_component(project_path: str, component_name: str) -> Dict[str, Any]:
    """
    Query information about a specific component in the project.
    
    Args:
        project_path: The root directory of the project
        component_name: The name of the component to query
        
    Returns:
        Detailed information about the component
    """
    # Pause monitoring during this operation
    with MonitoringPauser():
        try:
            # Check if project is in our active monitoring
            with state_lock:
                is_active = project_path in librarian_context["active_projects"]
                
            if is_active:
                logger.info(f"Using in-memory context for querying component: {component_name}")
            else:
                logger.info(f"Project not in active monitoring, checking disk: {project_path}")
                
            # Check if the AI Librarian exists
            ai_ref_path = os.path.join(project_path, ".ai_reference")
            if not os.path.exists(ai_ref_path):
                return {
                    "status": "error",
                    "message": f"AI Librarian not initialized at {project_path}. Run initialize_librarian first."
                }
            
            # Get script index - first check in-memory, then fallback to file
            script_index = None
            with state_lock:
                if project_path in librarian_context["projects"]:
                    script_index = librarian_context["projects"][project_path]
                    logger.info("Using in-memory script index")
            
            if script_index is None:
                script_index_path = os.path.join(ai_ref_path, "script_index.json")
                if not os.path.exists(script_index_path):
                    return {
                        "status": "error",
                        "message": f"Script index not found at {script_index_path}."
                    }
                
                with open(script_index_path, 'r', encoding='utf-8') as f:
                    script_index = json.load(f)
                    # Cache it for future use
                    with state_lock:
                        librarian_context["projects"][project_path] = script_index
            
            # Search for the component in all files
            results = []
            
            for file_path, file_info in script_index.get("files", {}).items():
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
                            try:
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
                                    logger.error(f"Error parsing file {full_file_path}: {str(e)}")
                                    results.append({
                                        "file_path": file_path,
                                        "error": f"Error parsing file: {str(e)}"
                                    })
                            except Exception as e:
                                logger.error(f"Error reading file {full_file_path}: {str(e)}")
                                results.append({
                                    "file_path": file_path,
                                    "error": f"Error reading file: {str(e)}"
                                })
            
            if not results:
                return {
                    "status": "error",
                    "message": f"Component '{component_name}' not found in the project."
                }
            
            # Return structured results
            return {
                "status": "success",
                "component_name": component_name,
                "found": True,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Error querying component: {str(e)}")
            return {
                "status": "error",
                "message": f"Error querying component: {str(e)}"
            }

@mcp.tool()
def find_implementation(project_path: str, search_text: str, file_pattern: str = None) -> Dict[str, Any]:
    """
    Find implementations containing the specified search text.
    
    Args:
        project_path: The root directory of the project
        search_text: The text to search for
        file_pattern: Optional pattern to filter files (e.g., "*.py")
        
    Returns:
        List of matching implementations with context
    """
    # Pause monitoring during this operation
    with MonitoringPauser():
        try:
            # Check if project is in active monitoring
            with state_lock:
                is_active = project_path in librarian_context["active_projects"]
                
            if is_active:
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
                            logger.error(f"Error searching file {file_path}: {str(e)}")
                            # Don't include errors in results to avoid strange output
            
            # Return structured results
            if not results:
                return {
                    "status": "success",
                    "found": False,
                    "message": f"No matches found for '{search_text}'"
                }
            
            return {
                "status": "success",
                "found": True,
                "search_text": search_text,
                "file_pattern": file_pattern,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Error finding implementation: {str(e)}")
            return {
                "status": "error",
                "message": f"Error finding implementation: {str(e)}"
            }

@mcp.tool()
def generate_librarian(project_path: str) -> str:
    """
    Generate or update the AI Librarian for a project.
    
    Args:
        project_path: The root directory of the project
        
    Returns:
        A success message with statistics or error information
    """
    # Pause monitoring during this operation
    with MonitoringPauser():
        try:
            # Check if the AI Librarian exists
            ai_ref_path = os.path.join(project_path, ".ai_reference")
            if not os.path.exists(ai_ref_path):
                return {
                    "status": "error",
                    "message": f"AI Librarian not initialized at {project_path}. Run initialize_librarian first."
                }
                
            # If project is not in active monitoring, add it
            with state_lock:
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
            with state_lock:
                if project_path in librarian_context["components"]:
                    component_registry = librarian_context["components"][project_path]
                    component_count = len(component_registry.get("components", {}))
                
                # Count files from in-memory representation
                if project_path in librarian_context["indexed_files"]:
                    file_count = len(librarian_context["indexed_files"][project_path])
            
            # Run diagnostic checks to verify librarian functionality
            diagnostic_results = run_librarian_diagnostics(project_path)
            
            return f"Successfully generated AI Librarian for {project_path}:\n" + \
                   f"- {file_count} files indexed\n" + \
                   f"- {component_count} components identified\n\n" + \
                   "Project is now being actively monitored for changes. Claude will maintain " + \
                   "context awareness across conversations.\n\n" + \
                   diagnostic_results
        except Exception as e:
            logger.error(f"Error generating librarian: {str(e)}")
            return f"Error generating librarian: {str(e)}"

@mcp.tool()
def sanity_check(project_path: str) -> str:
    """
    Run a comprehensive code quality check on the project.
    
    This tool performs a series of checks on the codebase to identify potential issues,
    inconsistencies, and path problems. It helps maintain code quality and catch
    configuration problems before they cause issues.
    
    Checks include:
    - Critical path verification
    - Import validation
    - Path reference analysis
    - Deprecated function detection
    - Duplicate functionality identification
    - Misplaced files detection
    - Static analysis with pylint (if available)
    
    Args:
        project_path: The root directory of the project to check
        
    Returns:
        A detailed report of the sanity check results
    """
    # Pause monitoring during this operation
    with MonitoringPauser():
        try:
            # Check if project is accessible
            if project_path not in permission_status or not permission_status[project_path]:
                access_check = check_project_access(project_path)
                if "Permission denied" in access_check or "Error checking access" in access_check:
                    return access_check
            
            # Use the run_sanity_check function imported at the top of the file
            return run_sanity_check(project_path)
        except Exception as e:
            logger.error(f"Error running sanity check: {str(e)}")
            return f"Error running sanity check: {str(e)}"

def run_librarian_diagnostics(project_path: str) -> str:
    """
    Run diagnostic checks on the AI Librarian to verify proper functionality.
    
    Args:
        project_path: The root directory of the project
        
    Returns:
        A diagnostic report message
    """
    try:
        logger.info(f"Running diagnostic checks for AI Librarian in {project_path}")
        results = ["🔍 AI Librarian Diagnostic Report:"]
        
        # 1. Check AI Reference Directory
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        if os.path.exists(ai_ref_path):
            results.append("✓ .ai_reference directory exists")
        else:
            results.append("✗ .ai_reference directory not found")
            return "\n".join(results)
        
        # 2. Check Script Index
        script_index_path = os.path.join(ai_ref_path, "script_index.json")
        script_index = None
        
        if os.path.exists(script_index_path):
            try:
                with open(script_index_path, 'r', encoding='utf-8') as f:
                    script_index = json.load(f)
                file_count = len(script_index.get('files', {}))
                results.append(f"✓ Script index found with {file_count} files")
            except Exception as e:
                logger.error(f"Error reading script index: {str(e)}")
                results.append(f"✗ Error reading script index: {str(e)}")
                script_index = None
        else:
            results.append("✗ Script index not found")
        
        # 3. Check Component Registry
        component_registry_path = os.path.join(ai_ref_path, "component_registry.json")
        component_registry = None
        
        if os.path.exists(component_registry_path):
            try:
                with open(component_registry_path, 'r', encoding='utf-8') as f:
                    component_registry = json.load(f)
                component_count = len(component_registry.get('components', {}))
                results.append(f"✓ Component registry found with {component_count} components")
            except Exception as e:
                logger.error(f"Error reading component registry: {str(e)}")
                results.append(f"✗ Error reading component registry: {str(e)}")
                component_registry = None
        else:
            results.append("✗ Component registry not found")
        
        # 4. Test Component Query - Try to find a random component if registry exists
        if component_registry and component_registry.get('components'):
            try:
                # Get a random component from the registry
                components = list(component_registry.get('components', {}).keys())
                if components:
                    test_component = components[0]  # Take the first component for testing
                    results.append(f"✓ Test component found: {test_component}")
                    
                    # Don't actually perform the search here to prevent potential output issues
                    results.append(f"✓ Component testing skipped (but component is available)")
                else:
                    results.append(f"⚠ No components found in registry to test")
            except Exception as e:
                logger.error(f"Error testing component query: {str(e)}")
                results.append(f"✗ Error testing component query: {str(e)}")
        else:
            results.append("⚠ Skipping component query test - no components available")
        
        # 5. Verify scripts directory
        scripts_dir = os.path.join(ai_ref_path, "scripts")
        if os.path.exists(scripts_dir):
            script_files = [f for f in os.listdir(scripts_dir) if f.endswith('.json')]
            results.append(f"✓ Scripts directory contains {len(script_files)} mini-librarian files")
        else:
            results.append("✗ Scripts directory not found")
            
        # 6. Check active monitoring status
        with state_lock:
            is_monitored = project_path in librarian_context["active_projects"]
            
        if is_monitored:
            results.append("✓ Project is actively monitored for changes")
        else:
            results.append("✗ Project is not in active monitoring list")
        
        # 7. Summary
        success_count = len([line for line in results if line.startswith("✓")])
        warning_count = len([line for line in results if line.startswith("⚠")])
        error_count = len([line for line in results if line.startswith("✗")])
        
        results.append(f"\nDiagnostic Summary: {success_count} checks passed, {warning_count} warnings, {error_count} errors")
        
        if error_count > 0:
            results.append("⚠ Some diagnostics failed. The librarian may have limited functionality.")
        else:
            results.append("✅ AI Librarian is fully operational!")
        
        # Save diagnostic report
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        report_path = os.path.join(ai_ref_path, "diagnostics", f"diagnostic-report-{timestamp}.txt")
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(results))
        except Exception as e:
            logger.error(f"Error saving diagnostic report: {str(e)}")
            # Don't add to results to avoid corruption
        
        return "\n".join(results)
    except Exception as e:
        logger.error(f"Error during diagnostics: {str(e)}")
        return f"Error running diagnostics: {str(e)}"

#-----------------------------------------------------------------
# Todo Management Tools
#-----------------------------------------------------------------

@mcp.tool()
def add_todo(project_path: str, title: str, description: str = "", priority: str = "medium", tags: str = "") -> Dict[str, str]:
    """
    Add a new to-do item to the project's persistent to-do list.
    
    The to-do list is stored with the project's AI Librarian data and persists across
    conversations, allowing tasks to be remembered and tracked over time.
    
    Args:
        project_path: The root directory of the project
        title: Title of the to-do item
        description: Detailed description of the task
        priority: Priority level (low, medium, high)
        tags: Comma-separated list of tags
        
    Returns:
        Success message with the ID of the created to-do item
    """
    # Use monitoring pauser to prevent output corruption
    with MonitoringPauser():
        try:
            # Check if the AI Librarian exists
            ai_ref_path = os.path.join(project_path, ".ai_reference")
            if not os.path.exists(ai_ref_path):
                return {
                    "status": "error",
                    "message": f"AI Librarian not initialized at {project_path}. Run initialize_librarian first."
                }
            
            # Create the todo manager
            todo_manager = TodoManager(project_path)
            
            # Parse tags
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            
            # Add the to-do item
            todo_id = todo_manager.add_todo(
                title=title,
                description=description,
                priority=priority,
                tags=tag_list
            )
            
            return {
                "status": "success",
                "todo_id": todo_id,
                "title": title,
                "priority": priority,
                "message": f"To-do item added with ID: {todo_id}"
            }
        except Exception as e:
            logger.error(f"Error adding to-do item: {str(e)}")
            return {
                "status": "error",
                "message": f"Error adding to-do item: {str(e)}"
            }

@mcp.tool()
def list_todos(project_path: str, status: str = "active", priority: str = None, tag: str = None) -> Dict[str, Any]:
    """
    List to-do items for the project with optional filtering.
    
    Args:
        project_path: The root directory of the project
        status: Filter by status (active, completed, etc.)
        priority: Filter by priority (low, medium, high)
        tag: Filter by a specific tag
        
    Returns:
        Formatted list of matching to-do items
    """
    # Use monitoring pauser to prevent output corruption
    with MonitoringPauser():
        try:
            # Check if the AI Librarian exists
            ai_ref_path = os.path.join(project_path, ".ai_reference")
            if not os.path.exists(ai_ref_path):
                return {
                    "status": "error",
                    "message": f"AI Librarian not initialized at {project_path}. Run initialize_librarian first."
                }
            
            # Create the todo manager
            todo_manager = TodoManager(project_path)
            
            # Get the to-do items
            todos = todo_manager.get_todos(status=status, priority=priority, tag=tag)
            
            if not todos:
                return {
                    "status": "success",
                    "found": False,
                    "message": f"No to-do items found with the specified filters.",
                    "filters": {
                        "status": status,
                        "priority": priority or "any",
                        "tag": tag or "any"
                    }
                }
            
            # Return structured results
            return {
                "status": "success",
                "found": True,
                "count": len(todos),
                "todos": todos,
                "filters": {
                    "status": status,
                    "priority": priority or "any",
                    "tag": tag or "any"
                }
            }
        except Exception as e:
            logger.error(f"Error listing to-do items: {str(e)}")
            return {
                "status": "error",
                "message": f"Error listing to-do items: {str(e)}"
            }

@mcp.tool()
def update_todo_status(project_path: str, todo_id: str, status: str) -> Dict[str, Any]:
    """
    Update the status of a to-do item.
    
    Args:
        project_path: The root directory of the project
        todo_id: ID of the to-do item to update
        status: New status (active, completed, etc.)
        
    Returns:
        Success message or error information
    """
    # Use monitoring pauser to prevent output corruption
    with MonitoringPauser():
        try:
            # Check if the AI Librarian exists
            ai_ref_path = os.path.join(project_path, ".ai_reference")
            if not os.path.exists(ai_ref_path):
                return {
                    "status": "error",
                    "message": f"AI Librarian not initialized at {project_path}. Run initialize_librarian first."
                }
            
            # Create the todo manager
            todo_manager = TodoManager(project_path)
            
            # Update the to-do item
            success = todo_manager.update_todo(todo_id, status=status)
            
            if success:
                return {
                    "status": "success",
                    "todo_id": todo_id,
                    "updated_status": status,
                    "message": f"Updated status of to-do item {todo_id} to '{status}'"
                }
            else:
                return {
                    "status": "error",
                    "message": f"To-do item with ID {todo_id} not found"
                }
        except Exception as e:
            logger.error(f"Error updating to-do item: {str(e)}")
            return {
                "status": "error",
                "message": f"Error updating to-do item: {str(e)}"
            }

@mcp.tool()
def add_subtask(project_path: str, todo_id: str, title: str) -> Dict[str, Any]:
    """
    Add a subtask to an existing to-do item.
    
    Args:
        project_path: The root directory of the project
        todo_id: ID of the parent to-do item
        title: Title of the subtask
        
    Returns:
        Success message or error information
    """
    # Use monitoring pauser to prevent output corruption
    with MonitoringPauser():
        try:
            # Check if the AI Librarian exists
            ai_ref_path = os.path.join(project_path, ".ai_reference")
            if not os.path.exists(ai_ref_path):
                return {
                    "status": "error",
                    "message": f"AI Librarian not initialized at {project_path}. Run initialize_librarian first."
                }
            
            # Create the todo manager
            todo_manager = TodoManager(project_path)
            
            # Add the subtask
            subtask_id = todo_manager.add_subtask(todo_id, title)
            
            if subtask_id:
                return {
                    "status": "success",
                    "todo_id": todo_id,
                    "subtask_id": subtask_id,
                    "title": title,
                    "message": f"Added subtask to to-do item {todo_id}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"To-do item with ID {todo_id} not found"
                }
        except Exception as e:
            logger.error(f"Error adding subtask: {str(e)}")
            return {
                "status": "error",
                "message": f"Error adding subtask: {str(e)}"
            }

@mcp.tool()
def search_todos(project_path: str, query: str) -> Dict[str, Any]:
    """
    Search for to-do items by text in title or description.
    
    Args:
        project_path: The root directory of the project
        query: Search text
        
    Returns:
        Formatted list of matching to-do items
    """
    # Use monitoring pauser to prevent output corruption
    with MonitoringPauser():
        try:
            # Check if the AI Librarian exists
            ai_ref_path = os.path.join(project_path, ".ai_reference")
            if not os.path.exists(ai_ref_path):
                return {
                    "status": "error",
                    "message": f"AI Librarian not initialized at {project_path}. Run initialize_librarian first."
                }
            
            # Create the todo manager
            todo_manager = TodoManager(project_path)
            
            # Search for to-do items
            todos = todo_manager.search_todos(query)
            
            if not todos:
                return {
                    "status": "success",
                    "found": False,
                    "query": query,
                    "message": f"No to-do items found matching '{query}'"
                }
            
            # Return structured results
            return {
                "status": "success",
                "found": True,
                "query": query,
                "count": len(todos),
                "todos": todos
            }
        except Exception as e:
            logger.error(f"Error searching to-do items: {str(e)}")
            return {
                "status": "error",
                "message": f"Error searching to-do items: {str(e)}"
            }

@mcp.tool()
def infer_todos(project_path: str, text: str) -> Dict[str, Any]:
    """
    Analyze text and extract potential to-do items, adding them to the list.
    
    This tool looks for common patterns that indicate tasks or reminders in conversation
    text and automatically adds them to the to-do list.
    
    Args:
        project_path: The root directory of the project
        text: Text to analyze for potential to-do items
        
    Returns:
        Message about extracted to-do items
    """
    # Use monitoring pauser to prevent output corruption
    with MonitoringPauser():
        try:
            # Check if the AI Librarian exists
            ai_ref_path = os.path.join(project_path, ".ai_reference")
            if not os.path.exists(ai_ref_path):
                return {
                    "status": "error",
                    "message": f"AI Librarian not initialized at {project_path}. Run initialize_librarian first."
                }
            
            # Create the todo manager
            todo_manager = TodoManager(project_path)
            
            # Infer to-do items
            todo_items = todo_manager.infer_todos(text)
            
            if not todo_items:
                return {
                    "status": "success",
                    "found": False,
                    "message": "No potential to-do items found in the text."
                }
            
            # Add the inferred to-do items
            added_items = []
            for item in todo_items:
                todo_id = todo_manager.add_todo(
                    title=item['title'],
                    description=item.get('description', ''),
                    priority="medium"
                )
                added_items.append({
                    "todo_id": todo_id,
                    "title": item['title'],
                })
            
            return {
                "status": "success",
                "found": True,
                "count": len(added_items),
                "todos": added_items,
                "message": f"Extracted and added {len(added_items)} to-do items."
            }
        except Exception as e:
            logger.error(f"Error inferring to-do items: {str(e)}")
            return {
                "status": "error",
                "message": f"Error inferring to-do items: {str(e)}"
            }

#-----------------------------------------------------------------
# File System Tools - Register directly from imported module
#-----------------------------------------------------------------

# Register all the filesystem tools directly
@mcp.tool()
def read_file(path: str) -> str:
    """Read the complete contents of a file from the file system."""
    return read_file_tool(path)

@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write content to a file in the file system."""
    return write_file_tool(path, content)

@mcp.tool()
def list_directory(path: str) -> str:
    """List the contents of a directory in the file system."""
    return list_directory_tool(path)

@mcp.tool()
def create_directory(path: str) -> str:
    """Create a new directory in the file system."""
    return create_directory_tool(path)

@mcp.tool()
def search_files(path: str, pattern: str) -> str:
    """Search for files matching a pattern in the file system."""
    return search_files_tool(path, pattern)

@mcp.tool()
def get_file_info(path: str) -> str:
    """Get detailed information about a file or directory."""
    return get_file_info_tool(path)

@mcp.tool()
def directory_tree(path: str) -> str:
    """Generate a tree view of a directory structure."""
    return directory_tree_tool(path)

#-----------------------------------------------------------------
# Prompts
#-----------------------------------------------------------------

@mcp.prompt()
def ai_librarian_help() -> str:
    """
    Provide help with AI Librarian functionality.
    """
    return """
    The AI Dev Toolkit helps me understand your codebase better. Here's how to use it:
    
    1. Initialize: `initialize_librarian("path/to/project")`
    2. Query a component: `query_component("path/to/project", "ComponentName")`
    3. Find implementations: `find_implementation("path/to/project", "search text")`
    4. Manage to-dos: `add_todo("path/to/project", "Task title")` and `list_todos("path/to/project")`
    5. Work with files: `read_file("path/to/file")`, `write_file("path/to/file", "content")`
    
    This creates metadata that persists across conversations, so I can better understand your code
    and remember tasks that need to be completed.
    """

@mcp.prompt()
def todo_list_help() -> str:
    """
    Provide help with the to-do list functionality and respond to casual inquiries.
    """
    return """
    When you ask me questions like "what's next?", "what's on the agenda?", "what are we working on?", 
    "I forgot what we were doing", or similar phrases, I'll interpret these as requests to show your 
    active to-do items.
    
    I'll prioritize items by importance and relevance to the current conversation.
    
    You can also explicitly use these commands:
    
    - `list_todos("path/to/project")` - Show all active tasks
    - `add_todo("path/to/project", "Task title")` - Add a new task
    - `update_todo_status("path/to/project", "todo-id", "completed")` - Mark a task as done
    - `search_todos("path/to/project", "keyword")` - Find specific tasks
    
    I'll also automatically detect when you mention new tasks during our conversation and can add them 
    to your to-do list if you'd like.
    """

#-----------------------------------------------------------------
# Main Entry Point
#-----------------------------------------------------------------

def main():
    """Entry point for running the server directly"""
    print("=" * 80)
    print("AI Dev Toolkit Unified Server")
    print("=" * 80)
    print(f"Server version: {mcp.version}")
    print(f"Allowed directories: {', '.join(ALLOWED_DIRECTORIES)}")
    print("=" * 80)
    print("Starting server...")
    
    # Run the server (this will block until server exits)
    mcp.run()


if __name__ == "__main__":
    main()
