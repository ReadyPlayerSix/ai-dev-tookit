#!/usr/bin/env python3
"""
AI Dev Toolkit MCP Server

This is the main server implementation for the AI Dev Toolkit MCP server.
It combines file system tools, AI Librarian capabilities, project starter tools,
and the think tool to create a comprehensive development assistant.

Key Features:
- Persistent AI Librarian context across conversations
- File system access and manipulation
- Project generation and scaffolding
- Structured reasoning tools

Usage:
    python server.py

Requirements:
    pip install "mcp[cli]"
"""

import os
import sys
import json
import time
import atexit
import shutil
import logging
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Set

from mcp.server.fastmcp import FastMCP, Context, Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_dev_toolkit.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ai-dev-toolkit")

# Create the MCP server
mcp = FastMCP("AI Dev Toolkit")

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
        from src.librarian.indexer import initialize_librarian
        
        # Update the librarian files
        message, file_count, component_count = initialize_librarian(project_path)
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
    logger.info("Shutting down AI Dev Toolkit server")
    
    # Save any persistent state if needed
    state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.ai_toolkit_state.json")
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
state_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.ai_toolkit_state.json")
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

#-----------------------------------------------------------------
# File System Tools
#-----------------------------------------------------------------

@mcp.tool()
def read_file(path: str) -> str:
    """
    Read the complete contents of a file from the file system.
    
    Args:
        path: The path to the file to read
        
    Returns:
        The contents of the file as a string
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with binary mode for non-text files
        with open(path, 'rb') as f:
            return f"[Binary file content - {len(f.read())} bytes]"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
def read_multiple_files(paths: List[str]) -> Dict[str, str]:
    """
    Read the contents of multiple files simultaneously.
    
    Args:
        paths: List of file paths to read
        
    Returns:
        Dictionary mapping file paths to their contents
    """
    results = {}
    for path in paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                results[path] = f.read()
        except UnicodeDecodeError:
            # Try with binary mode for non-text files
            with open(path, 'rb') as f:
                results[path] = f"[Binary file content - {len(f.read())} bytes]"
        except Exception as e:
            results[path] = f"Error reading file: {str(e)}"
    return results


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """
    Create a new file or completely overwrite an existing file with new content.
    
    Args:
        path: The path where the file should be written
        content: The content to write to the file
        
    Returns:
        A success message or error information
    """
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        
        # Write the file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@mcp.tool()
def edit_file(path: str, edits: List[Dict[str, str]], dry_run: bool = False) -> str:
    """
    Make line-based edits to a text file.
    
    Args:
        path: The path to the file to edit
        edits: List of edit operations, each containing 'oldText' and 'newText'
        dry_run: Whether to preview changes without making them
        
    Returns:
        A diff showing the changes made or error information
    """
    try:
        # Read the file
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply the edits
        new_content = content
        for edit in edits:
            if 'oldText' not in edit or 'newText' not in edit:
                return "Error: Each edit must contain 'oldText' and 'newText'"
            
            old_text = edit['oldText']
            new_text = edit['newText']
            
            # Make sure the old text exists exactly once in the file
            if old_text not in new_content:
                return f"Error: Could not find text to replace: {old_text}"
            
            if new_content.count(old_text) > 1:
                return f"Error: Found multiple instances of text to replace: {old_text}"
            
            new_content = new_content.replace(old_text, new_text)
        
        # Generate a simple diff
        diff = []
        old_lines = content.splitlines()
        new_lines = new_content.splitlines()
        
        for i, (old_line, new_line) in enumerate(zip(old_lines, new_lines)):
            if old_line != new_line:
                diff.append(f"Line {i+1}:")
                diff.append(f"- {old_line}")
                diff.append(f"+ {new_line}")
                diff.append("")
        
        # Handle different number of lines
        if len(old_lines) > len(new_lines):
            for i in range(len(new_lines), len(old_lines)):
                diff.append(f"Line {i+1}:")
                diff.append(f"- {old_lines[i]}")
                diff.append("")
        elif len(new_lines) > len(old_lines):
            for i in range(len(old_lines), len(new_lines)):
                diff.append(f"Line {i+1}:")
                diff.append(f"+ {new_lines[i]}")
                diff.append("")
        
        # If not a dry run, write the changes
        if not dry_run:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return f"Changes applied to {path}:\n\n" + "\n".join(diff)
        else:
            return f"Dry run changes for {path}:\n\n" + "\n".join(diff)
    except Exception as e:
        return f"Error editing file: {str(e)}"


@mcp.tool()
def create_directory(path: str) -> str:
    """
    Create a new directory or ensure a directory exists.
    
    Args:
        path: The path where the directory should be created
        
    Returns:
        A success message or error information
    """
    try:
        os.makedirs(path, exist_ok=True)
        return f"Successfully created directory {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"


@mcp.tool()
def list_directory(path: str) -> str:
    """
    Get a detailed listing of all files and directories in a specified path.
    
    Args:
        path: The directory path to list
        
    Returns:
        A formatted listing of files and directories
    """
    try:
        items = os.listdir(path)
        result = []
        
        for item in sorted(items):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                result.append(f"[DIR] {item}")
            else:
                result.append(f"[FILE] {item}")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@mcp.tool()
def directory_tree(path: str) -> str:
    """
    Get a recursive tree view of files and directories as a structured output.
    
    Args:
        path: The directory path to create a tree for
        
    Returns:
        A formatted tree view of the directory structure
    """
    def _build_tree(p, level=0):
        result = []
        prefix = "│   " * (level - 1) + "├── " if level > 0 else ""
        
        try:
            p = Path(p)
            name = p.name
            
            if p.is_dir():
                result.append(f"{prefix}{name}/")
                
                # Get sorted directory contents
                contents = sorted(list(p.iterdir()), key=lambda x: (not x.is_dir(), x.name))
                
                # Process each item
                for i, item in enumerate(contents):
                    # Skip __pycache__ directories
                    if item.name == "__pycache__" or item.name.startswith("."):
                        continue
                    
                    # Add items to the tree
                    result.extend(_build_tree(item, level + 1))
                
            else:
                result.append(f"{prefix}{name}")
                
            return result
            
        except Exception as e:
            return [f"{prefix}Error: {str(e)}"]
    
    try:
        tree = _build_tree(path)
        return "\n".join(tree)
    except Exception as e:
        return f"Error generating directory tree: {str(e)}"


@mcp.tool()
def move_file(source: str, destination: str) -> str:
    """
    Move or rename files and directories.
    
    Args:
        source: The source file or directory path
        destination: The destination file or directory path
        
    Returns:
        A success message or error information
    """
    try:
        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(destination)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)
        
        # Move the file or directory
        shutil.move(source, destination)
        return f"Successfully moved {source} to {destination}"
    except Exception as e:
        return f"Error moving file: {str(e)}"


@mcp.tool()
def search_files(path: str, pattern: str, exclude_patterns: List[str] = None) -> str:
    """
    Recursively search for files and directories matching a pattern.
    
    Args:
        path: The starting directory path
        pattern: The search pattern to match
        exclude_patterns: Optional list of patterns to exclude
        
    Returns:
        A list of matching file paths
    """
    if exclude_patterns is None:
        exclude_patterns = []
    
    try:
        matches = []
        pattern = pattern.lower()
        
        for root, dirnames, filenames in os.walk(path):
            # Check if the current directory should be excluded
            should_skip = False
            for exclude in exclude_patterns:
                if exclude.lower() in root.lower():
                    should_skip = True
                    break
            
            if should_skip:
                continue
            
            # Filter directories in-place
            dirnames[:] = [d for d in dirnames if not any(
                exclude.lower() in d.lower() for exclude in exclude_patterns
            )]
            
            # Check files
            for filename in filenames:
                if pattern.lower() in filename.lower() and not any(
                    exclude.lower() in filename.lower() for exclude in exclude_patterns
                ):
                    matches.append(os.path.join(root, filename))
        
        return "\n".join(matches) if matches else "No matches found"
    except Exception as e:
        return f"Error searching files: {str(e)}"


@mcp.tool()
def get_file_info(path: str) -> str:
    """
    Retrieve detailed metadata about a file or directory.
    
    Args:
        path: The file or directory path
        
    Returns:
        Detailed information about the file or directory
    """
    try:
        # Get file/directory stats
        stats = os.stat(path)
        
        # Determine if it's a file or directory
        is_dir = os.path.isdir(path)
        file_type = "Directory" if is_dir else "File"
        
        # Get file size in human-readable format
        size_bytes = stats.st_size
        size_display = size_bytes
        
        for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if size_display < 1024.0 or unit == 'TB':
                break
            size_display /= 1024.0
        
        size = f"{size_display:.2f} {unit}" if unit != 'bytes' else f"{size_display} bytes"
        
        # Format timestamps
        import datetime
        created = datetime.datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        modified = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        accessed = datetime.datetime.fromtimestamp(stats.st_atime).strftime('%Y-%m-%d %H:%M:%S')
        
        # Construct the result
        info = [
            f"Path: {path}",
            f"Type: {file_type}",
            f"Size: {size}",
            f"Created: {created}",
            f"Modified: {modified}",
            f"Accessed: {accessed}",
            f"Permissions: {oct(stats.st_mode)[-3:]}"
        ]
        
        return "\n".join(info)
    except Exception as e:
        return f"Error getting file info: {str(e)}"


# Dictionary to store permission status of directories
permission_status = {}

@mcp.tool()
def list_allowed_directories() -> str:
    """
    Returns the list of directories that this server is allowed to access.
    
    Returns:
        A list of allowed directory paths
    """
    # These would be configured or determined at runtime in a real implementation
    allowed_dirs = [
        "D:\Projects\isekaiZen\ai-dev-toolkit",
        "D:\Projects\isekaiZen\machine-learning-optimizer"
    ]
    
    # Update our permission status tracker
    for dir_path in allowed_dirs:
        permission_status[dir_path] = True
    
    return "Allowed directories:\n" + "\n".join(allowed_dirs)

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
                   "5. Grant access to {project_path}"
    except Exception as e:
        logger.error(f"Error checking project access: {str(e)}")
        return f"❌ Error checking access: {str(e)}"

#-----------------------------------------------------------------
# AI Librarian Tools
#-----------------------------------------------------------------

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
- `generate_mini_librarians.py` - Script to generate mini-librarians
- `library_generator.py` - Main library generator
- `run_generator.py` - Runner script for the generator

## Usage

The AI Librarian is automatically maintained by the AI Dev Toolkit MCP server.
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
        
        # Create a simple generator script
        generator_script = """#!/usr/bin/env python3
\"\"\"
Library Generator

This script generates the AI Librarian files for the project.
\"\"\"

import os
import json
import ast
from pathlib import Path

def scan_directory(directory, exclude_dirs=None):
    \"\"\"Scan a directory for Python files.\"\"\"
    if exclude_dirs is None:
        exclude_dirs = []
    
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def parse_python_file(file_path):
    \"\"\"Parse a Python file and extract its structure.\"\"\"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        return {
            "classes": classes,
            "functions": functions
        }
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return {
            "classes": [],
            "functions": []
        }

def generate_mini_librarian(file_path, file_info, output_dir):
    \"\"\"Generate a mini-librarian for a Python file.\"\"\"
    # Create a relative path for the mini-librarian
    rel_path = os.path.relpath(file_path, os.path.dirname(output_dir))
    rel_path = rel_path.replace('\\\\', '/')
    
    # Create output path
    mini_librarian_path = os.path.join(
        output_dir, 
        f"{rel_path.replace('/', '_').replace('.', '_')}.json"
    )
    
    # Create the mini-librarian content
    mini_librarian = {
        "file_path": rel_path,
        "classes": file_info["classes"],
        "functions": file_info["functions"],
        "imports": [],
        "description": f"Mini-librarian for {rel_path}"
    }
    
    # Write the mini-librarian
    os.makedirs(os.path.dirname(mini_librarian_path), exist_ok=True)
    with open(mini_librarian_path, 'w', encoding='utf-8') as f:
        json.dump(mini_librarian, f, indent=2)
    
    return os.path.relpath(mini_librarian_path, output_dir)

def generate_script_index(files_info, output_file):
    \"\"\"Generate the script index file.\"\"\"
    script_index = {"files": {}}
    
    for file_path, info in files_info.items():
        rel_path = file_path.replace('\\\\', '/')
        script_index["files"][rel_path] = {
            "path": rel_path,
            "classes": info["file_info"]["classes"],
            "functions": info["file_info"]["functions"],
            "mini_librarian": info["mini_librarian_path"]
        }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(script_index, f, indent=2)

def main():
    \"\"\"Main entry point for the library generator.\"\"\"
    # Find the project root (parent directory of .ai_reference)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Directories to exclude
    exclude_dirs = ['venv', 'env', '.venv', '.env', '__pycache__', 'node_modules', '.git']
    
    # Scan for Python files
    python_files = scan_directory(project_root, exclude_dirs)
    
    # Parse Python files
    files_info = {}
    for file_path in python_files:
        file_info = parse_python_file(file_path)
        
        # Generate mini-librarian
        mini_librarian_path = generate_mini_librarian(
            file_path, 
            file_info, 
            os.path.join(script_dir, "scripts")
        )
        
        files_info[file_path] = {
            "file_info": file_info,
            "mini_librarian_path": mini_librarian_path
        }
    
    # Generate script index
    generate_script_index(
        files_info,
        os.path.join(script_dir, "script_index.json")
    )
    
    print(f"AI Librarian generated for {len(files_info)} files")

if __name__ == "__main__":
    main()
"""
        with open(os.path.join(ai_ref_path, "library_generator.py"), 'w', encoding='utf-8') as f:
            f.write(generator_script)
        
        # Create a simple generator script runner
        runner_script = """#!/usr/bin/env python3
\"\"\"
Run the library generator.
\"\"\"

import os
import sys
import subprocess

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run the library generator
    generator_path = os.path.join(script_dir, "library_generator.py")
    
    print(f"Running library generator from {generator_path}")
    subprocess.run([sys.executable, generator_path])
    print("Library generator finished")

if __name__ == "__main__":
    main()
"""
        with open(os.path.join(ai_ref_path, "run_generator.py"), 'w', encoding='utf-8') as f:
            f.write(runner_script)
        
        # Create a mini-librarian generator script
        mini_gen_script = """#!/usr/bin/env python3
\"\"\"
Generate mini-librarians for Python files.
\"\"\"

import os
import json
import ast
from pathlib import Path

def parse_python_file(file_path):
    \"\"\"Parse a Python file and extract its structure.\"\"\"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        return {
            "classes": classes,
            "functions": functions
        }
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return {
            "classes": [],
            "functions": []
        }

def generate_mini_librarian(file_path, output_dir=None):
    \"\"\"Generate a mini-librarian for a Python file.\"\"\"
    # Determine output directory
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "scripts")
    
    # Parse the file
    file_info = parse_python_file(file_path)
    
    # Create a relative path for the mini-librarian
    rel_path = os.path.relpath(file_path, os.path.dirname(output_dir))
    rel_path = rel_path.replace('\\\\', '/')
    
    # Create output path
    mini_librarian_path = os.path.join(
        output_dir, 
        f"{rel_path.replace('/', '_').replace('.', '_')}.json"
    )
    
    # Create the mini-librarian content
    mini_librarian = {
        "file_path": rel_path,
        "classes": file_info["classes"],
        "functions": file_info["functions"],
        "imports": [],
        "description": f"Mini-librarian for {rel_path}"
    }
    
    # Write the mini-librarian
    os.makedirs(os.path.dirname(mini_librarian_path), exist_ok=True)
    with open(mini_librarian_path, 'w', encoding='utf-8') as f:
        json.dump(mini_librarian, f, indent=2)
    
    return mini_librarian_path

def main():
    \"\"\"Main entry point for the mini-librarian generator.\"\"\"
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_mini_librarians.py <file_path> [output_dir]")
        return
    
    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    mini_librarian_path = generate_mini_librarian(file_path, output_dir)
    print(f"Generated mini-librarian at {mini_librarian_path}")

if __name__ == "__main__":
    main()
"""
        with open(os.path.join(ai_ref_path, "generate_mini_librarians.py"), 'w', encoding='utf-8') as f:
            f.write(mini_gen_script)
        
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
# Project Starter Tools
#-----------------------------------------------------------------

@mcp.tool()
def create_project_plan(
    project_name: str,
    project_description: str,
    project_type: str,
    key_features: List[str]
) -> str:
    """
    Generate a detailed project plan based on the provided information.
    
    Args:
        project_name: The name of the project
        project_description: A brief description of the project
        project_type: The type of project (e.g., "web", "cli", "library", "api")
        key_features: List of key features for the project
        
    Returns:
        A markdown-formatted project plan
    """
    try:
        project_type = project_type.lower()
        
        # Determine project structure based on type
        structure = []
        
        if project_type == "web":
            structure = [
                "project-name/",
                "├── src/",
                "│   ├── components/",
                "│   ├── pages/",
                "│   ├── utils/",
                "│   └── styles/",
                "├── public/",
                "│   ├── images/",
                "│   └── favicon.ico",
                "├── tests/",
                "├── package.json",
                "├── README.md",
                "└── .gitignore"
            ]
        elif project_type == "cli":
            structure = [
                "project-name/",
                "├── src/",
                "│   ├── commands/",
                "│   ├── utils/",
                "│   └── main.py",
                "├── tests/",
                "├── setup.py",
                "├── README.md",
                "└── .gitignore"
            ]
        elif project_type == "library":
            structure = [
                "project-name/",
                "├── src/",
                "│   └── project_name/",
                "│       ├── __init__.py",
                "│       └── core.py",
                "├── tests/",
                "├── docs/",
                "├── setup.py",
                "├── README.md",
                "└── .gitignore"
            ]
        elif project_type == "api":
            structure = [
                "project-name/",
                "├── src/",
                "│   ├── api/",
                "│   │   ├── __init__.py",
                "│   │   ├── routes.py",
                "│   │   └── models.py",
                "│   ├── utils/",
                "│   └── main.py",
                "├── tests/",
                "├── docs/",
                "├── setup.py",
                "├── README.md",
                "└── .gitignore"
            ]
        else:
            structure = [
                "project-name/",
                "├── src/",
                "├── tests/",
                "├── docs/",
                "├── README.md",
                "└── .gitignore"
            ]
        
        # Replace project-name in structure
        slug = project_name.lower().replace(' ', '-')
        structure = [line.replace('project-name', slug) for line in structure]
        
        # Generate the project plan
        plan = f"""# {project_name} Project Plan

## Project Overview

**Name**: {project_name}
**Description**: {project_description}
**Type**: {project_type.capitalize()}

## Key Features

"""
        
        for i, feature in enumerate(key_features):
            plan += f"{i+1}. {feature}\n"
        
        plan += """
## Project Structure

```
"""
        
        plan += "\n".join(structure)
        
        plan += """
```

## Development Roadmap

### Phase 1: Setup and Foundation
- Initialize project structure
- Set up version control
- Configure development environment
- Create basic documentation

### Phase 2: Core Implementation
- Implement core functionality
- Create basic tests
- Establish CI/CD pipeline

### Phase 3: Feature Development
- Implement key features
- Develop comprehensive tests
- Enhance documentation

### Phase 4: Refinement and Launch
- Performance optimization
- User testing and feedback
- Final polish and launch preparation

## Technical Requirements

### Development Tools
- Version control: Git
- Issue tracking: GitHub Issues
- Documentation: Markdown

### Dependencies
"""
        
        # Add dependencies based on project type
        if project_type == "web":
            plan += """- React or Vue.js
- CSS framework (e.g., Tailwind, Bootstrap)
- Jest for testing
"""
        elif project_type == "cli":
            plan += """- Click or Argparse for CLI commands
- Pytest for testing
"""
        elif project_type == "library":
            plan += """- Core libraries as needed
- Pytest for testing
- Sphinx for documentation
"""
        elif project_type == "api":
            plan += """- FastAPI or Flask
- SQLAlchemy (if using databases)
- Pytest for testing
"""
        
        plan += """
## Next Steps

1. Create GitHub repository
2. Set up development environment
3. Create initial project structure
4. Implement basic functionality
"""
        
        return plan
    except Exception as e:
        return f"Error creating project plan: {str(e)}"


@mcp.tool()
def generate_project_structure(
    structure_text: str,
    output_directory: str
) -> str:
    """
    Generate a project directory structure based on the provided text.
    
    Args:
        structure_text: Text representation of the directory structure (as in create_project_plan)
        output_directory: Directory where the structure should be created
        
    Returns:
        Success message or error information
    """
    try:
        # Parse the structure text
        lines = structure_text.strip().split('\n')
        
        # Create the base directory
        os.makedirs(output_directory, exist_ok=True)
        
        # Track created directories
        created_dirs = []
        created_files = []
        
        # Process each line
        for line in lines:
            line = line.strip()
            if not line or line.startswith('project-name') or line == '```':
                continue
            
            # Extract the path
            path = line
            for prefix in ['├──', '│   ├──', '│   │   ├──', '│   │   │   ├──',
                          '└──', '│   └──', '│   │   └──', '│   │   │   └──']:
                if path.startswith(prefix):
                    path = path[len(prefix):].strip()
                    break
            
            # Create the full path
            full_path = os.path.join(output_directory, path)
            
            # Create directory or file
            if path.endswith('/'):
                # It's a directory
                os.makedirs(full_path, exist_ok=True)
                created_dirs.append(path)
            else:
                # It's a file
                # Create parent directory if it doesn't exist
                parent_dir = os.path.dirname(full_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)
                
                # Create an empty file
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {os.path.basename(path)}\n")
                created_files.append(path)
        
        return f"Successfully created project structure at {output_directory}:\n- {len(created_dirs)} directories\n- {len(created_files)} files"
    except Exception as e:
        return f"Error generating project structure: {str(e)}"


@mcp.tool()
def create_starter_files(
    project_directory: str,
    project_name: str,
    project_type: str
) -> str:
    """
    Create starter files for a project with appropriate templates.
    
    Args:
        project_directory: The root directory of the project
        project_name: The name of the project
        project_type: The type of project (e.g., "web", "cli", "library", "api")
        
    Returns:
        Success message or error information
    """
    try:
        project_type = project_type.lower()
        package_name = project_name.lower().replace(' ', '_').replace('-', '_')
        
        # Create README.md
        readme_content = f"""# {project_name}

## Overview

A {project_type} project.

## Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/{project_name.lower().replace(' ', '-')}.git
cd {project_name.lower().replace(' ', '-')}

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

[Usage instructions will go here]

## Development

[Development instructions will go here]

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"""
        readme_path = os.path.join(project_directory, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Create .gitignore
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE specific files
.idea/
.vscode/
*.swp
*.swo

# Project specific
*.log
.DS_Store
"""
        gitignore_path = os.path.join(project_directory, ".gitignore")
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        # Create setup.py for Python projects
        if project_type in ["cli", "library", "api"]:
            setup_content = f"""from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    install_requires=[
        # Add your dependencies here
    ],
    entry_points={{
        'console_scripts': [
            '{package_name}=src.{package_name}.main:main',
        ],
    }},
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="{project_name} - a {project_type} project",
    keywords="{project_name.lower().replace(' ', ', ')}",
    url="https://github.com/yourusername/{project_name.lower().replace(' ', '-')}",
    project_urls={{
        "Bug Tracker": "https://github.com/yourusername/{project_name.lower().replace(' ', '-')}/issues",
    }},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
"""
            setup_path = os.path.join(project_directory, "setup.py")
            with open(setup_path, 'w', encoding='utf-8') as f:
                f.write(setup_content)
        
        # Create package directory and __init__.py
        src_dir = os.path.join(project_directory, "src")
        package_dir = os.path.join(src_dir, package_name)
        os.makedirs(package_dir, exist_ok=True)
        
        init_content = f'''"""
{project_name} package.
"""

__version__ = "0.1.0"
'''
        init_path = os.path.join(package_dir, "__init__.py")
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write(init_content)
        
        # Create type-specific files
        if project_type == "cli":
            main_content = '''"""
Command-line interface main entry point.
"""

import argparse
import sys

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Command-line interface")
    parser.add_argument("--version", action="store_true", help="Show version information")
    
    args = parser.parse_args()
    
    if args.version:
        from . import __version__
        print(f"Version: {__version__}")
        return 0
    
    print("Hello from the CLI!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
            main_path = os.path.join(package_dir, "main.py")
            with open(main_path, 'w', encoding='utf-8') as f:
                f.write(main_content)
            
            # Create commands directory with examples
            commands_dir = os.path.join(package_dir, "commands")
            os.makedirs(commands_dir, exist_ok=True)
            
            commands_init = '''"""
Command implementations.
"""
'''
            commands_init_path = os.path.join(commands_dir, "__init__.py")
            with open(commands_init_path, 'w', encoding='utf-8') as f:
                f.write(commands_init)
            
        elif project_type == "library":
            core_content = '''"""
Core functionality for the library.
"""

def example_function():
    """An example function."""
    return "Hello from the library!"

class ExampleClass:
    """An example class."""
    
    def __init__(self, name):
        """Initialize the class."""
        self.name = name
    
    def greet(self):
        """Return a greeting."""
        return f"Hello, {self.name}!"
'''
            core_path = os.path.join(package_dir, "core.py")
            with open(core_path, 'w', encoding='utf-8') as f:
                f.write(core_content)
            
        elif project_type == "api":
            main_content = '''"""
API main entry point.
"""

from fastapi import FastAPI

app = FastAPI(title="API", description="API description")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello World"}

def main():
    """Run the API with uvicorn."""
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
'''
            main_path = os.path.join(package_dir, "main.py")
            with open(main_path, 'w', encoding='utf-8') as f:
                f.write(main_content)
            
            # Create API directory with examples
            api_dir = os.path.join(package_dir, "api")
            os.makedirs(api_dir, exist_ok=True)
            
            api_init = '''"""
API package.
"""
'''
            api_init_path = os.path.join(api_dir, "__init__.py")
            with open(api_init_path, 'w', encoding='utf-8') as f:
                f.write(api_init)
            
            routes_content = '''"""
API routes.
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/items/")
async def list_items():
    """List items."""
    return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    """Get an item by ID."""
    return {"id": item_id, "name": f"Item {item_id}"}
'''
            routes_path = os.path.join(api_dir, "routes.py")
            with open(routes_path, 'w', encoding='utf-8') as f:
                f.write(routes_content)
            
            models_content = '''"""
API data models.
"""

from pydantic import BaseModel

class Item(BaseModel):
    """Item model."""
    id: int
    name: str
    description: str = None
'''
            models_path = os.path.join(api_dir, "models.py")
            with open(models_path, 'w', encoding='utf-8') as f:
                f.write(models_content)
            
        elif project_type == "web":
            # Create a simple package.json
            package_json_content = f'''{{
  "name": "{package_name}",
  "version": "0.1.0",
  "description": "{project_name} - a web project",
  "main": "index.js",
  "scripts": {{
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }},
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  }},
  "devDependencies": {{
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^13.5.0"
  }},
  "author": "Your Name",
  "license": "MIT"
}}
'''
            package_json_path = os.path.join(project_directory, "package.json")
            with open(package_json_path, 'w', encoding='utf-8') as f:
                f.write(package_json_content)
            
            # Create basic index.js
            index_content = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
            index_path = os.path.join(src_dir, "index.js")
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            # Create basic App.js
            app_content = f'''import React from 'react';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>{project_name}</h1>
        <p>Welcome to {project_name}</p>
      </header>
    </div>
  );
}}

export default App;
'''
            app_path = os.path.join(src_dir, "App.js")
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(app_content)
            
            # Create components directory with example
            components_dir = os.path.join(src_dir, "components")
            os.makedirs(components_dir, exist_ok=True)
            
            example_component = '''import React from 'react';

function ExampleComponent(props) {
  return (
    <div className="example-component">
      <h2>{props.title}</h2>
      <p>{props.content}</p>
    </div>
  );
}

export default ExampleComponent;
'''
            component_path = os.path.join(components_dir, "ExampleComponent.js")
            with open(component_path, 'w', encoding='utf-8') as f:
                f.write(example_component)
            
            # Create pages directory with example
            pages_dir = os.path.join(src_dir, "pages")
            os.makedirs(pages_dir, exist_ok=True)
            
            example_page = '''import React from 'react';
import ExampleComponent from '../components/ExampleComponent';

function HomePage() {
  return (
    <div className="home-page">
      <h1>Home Page</h1>
      <ExampleComponent 
        title="Welcome" 
        content="This is an example component on the home page." 
      />
    </div>
  );
}

export default HomePage;
'''
            page_path = os.path.join(pages_dir, "HomePage.js")
            with open(page_path, 'w', encoding='utf-8') as f:
                f.write(example_page)
            
            # Create public directory with index.html
            public_dir = os.path.join(project_directory, "public")
            os.makedirs(public_dir, exist_ok=True)
            
            html_content = f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="{project_name} - a web project" />
    <title>{project_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
'''
            html_path = os.path.join(public_dir, "index.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return f"Successfully created starter files for {project_name} ({project_type} project) at {project_directory}"
    except Exception as e:
        return f"Error creating starter files: {str(e)}"


@mcp.tool()
def setup_github_repo(project_name: str, project_description: str) -> str:
    """
    Generate instructions for setting up a GitHub repository for the project.
    
    Args:
        project_name: The name of the project
        project_description: A brief description of the project
        
    Returns:
        Markdown-formatted instructions for setting up a GitHub repository
    """
    try:
        # Generate GitHub setup instructions
        repo_slug = project_name.lower().replace(' ', '-')
        
        instructions = f"""# GitHub Repository Setup for {project_name}

Follow these steps to set up a GitHub repository for your project:

## 1. Create a New Repository

1. Go to [GitHub](https://github.com) and sign in to your account.
2. Click the "+" icon in the top right corner and select "New repository".
3. Enter "{repo_slug}" as the repository name.
4. Add the description: "{project_description}"
5. Choose visibility (public or private).
6. Check "Add a README file" if you haven't created one locally.
7. Check "Add .gitignore" and select the appropriate template (e.g., Python, Node).
8. Check "Choose a license" and select an appropriate license (e.g., MIT).
9. Click "Create repository".

## 2. Clone the Repository Locally

If you created the repository on GitHub first:

```bash
git clone https://github.com/yourusername/{repo_slug}.git
cd {repo_slug}
```

## 3. Initialize Local Repository and Push

If you've already created your project locally:

```bash
cd /path/to/your/{repo_slug}
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/{repo_slug}.git
git push -u origin main
```

## 4. Set Up GitHub Actions (Optional)

Create a `.github/workflows` directory in your repository:

```bash
mkdir -p .github/workflows
```

Add a CI workflow file (e.g., `.github/workflows/ci.yml`):

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Test with pytest
      run: |
        pytest
```

## 5. Protect the Main Branch (Optional)

1. Go to the repository settings on GitHub.
2. Under "Branches", click "Add rule".
3. Enter "main" as the branch name pattern.
4. Configure protection rules as needed (e.g., require pull request reviews).
5. Click "Create".

## 6. Next Steps

- Create project issues for key features
- Set up project boards for task tracking
- Add collaborators if working with a team
- Configure repository integrations as needed
"""
        
        return instructions
    except Exception as e:
        return f"Error generating GitHub setup instructions: {str(e)}"

#-----------------------------------------------------------------
# Think Tool
#-----------------------------------------------------------------

@mcp.tool()
def think(thought: str) -> str:
    """
    Use this tool to think through a problem or plan an approach.
    
    This tool provides a scratchpad for organizing thoughts, reasoning
    about problems, and planning implementations. It doesn't make any
    changes to files or perform any actions.
    
    Args:
        thought: The thought process to record
        
    Returns:
        A confirmation that the thought was processed
    """
    # The think tool simply returns the thought with a confirmation
    # It doesn't perform any actions, it's just a scratchpad
    return f"Thought recorded: {thought}"

#-----------------------------------------------------------------
# Main Function
#-----------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
