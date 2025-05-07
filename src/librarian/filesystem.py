"""
AI Librarian Filesystem Module

This module implements filesystem operations for the AI Librarian,
replacing the need for a separate filesystem MCP server.
"""
import os
import sys
import glob
import json
import shutil
import fnmatch
import tempfile
import mimetypes
import pathlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any, Set, Union, BinaryIO


def validate_path(path: str, allowed_directories: List[str]) -> bool:
    """
    Validate that a path is within allowed directories.
    
    Args:
        path: Path to validate
        allowed_directories: List of allowed directory paths
        
    Returns:
        True if path is valid, False otherwise
    """
    # Convert to absolute path
    abs_path = os.path.abspath(path)
    
    # Convert all allowed directories to absolute paths
    abs_allowed = [os.path.abspath(d) for d in allowed_directories]
    
    # Check if the path is within any allowed directory
    for allowed_dir in abs_allowed:
        # Use pathlib for safer path comparison
        path_obj = Path(abs_path)
        allowed_obj = Path(allowed_dir)
        
        try:
            # Use relative_to to check if the path is inside the allowed dir
            # This will raise ValueError if path is not within allowed_dir
            path_obj.relative_to(allowed_obj)
            return True
        except ValueError:
            # Path is not within this allowed dir, try the next one
            continue
    
    # If we get here, the path is not within any allowed directory
    return False


def get_allowed_directories() -> List[str]:
    """
    Get the list of directories that the server is allowed to access.
    
    Returns:
        List of allowed directory paths
    """
    # Return built-in default directories (would be configured in a real implementation)
    # Or environment variable / config settings in a real implementation
    env_dirs = os.environ.get("AI_LIBRARIAN_ALLOWED_DIRS", "")
    
    if env_dirs:
        return [d.strip() for d in env_dirs.split(",")]
    
    # Fallback to the current working directory if no env var is specified
    return [os.getcwd()]


def detect_encoding(file_path: str) -> str:
    """
    Detect the encoding of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Detected encoding, defaults to utf-8
    """
    # In a real implementation, this would use chardet or similar
    # For now, we'll just default to utf-8
    return "utf-8"


def guess_mimetype(file_path: str) -> str:
    """
    Guess the MIME type of a file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type string
    """
    # Initialize mimetypes if not already done
    if not mimetypes.inited:
        mimetypes.init()
    
    # Guess type based on file extension
    mime_type, encoding = mimetypes.guess_type(file_path)
    
    # Default to application/octet-stream if type couldn't be determined
    if mime_type is None:
        mime_type = "application/octet-stream"
    
    return mime_type


def read_file(path: str, encoding: Optional[str] = None, 
              allowed_directories: Optional[List[str]] = None) -> Tuple[str, str]:
    """
    Read file content with auto-detection of encoding if not specified.
    
    Args:
        path: Path to the file
        encoding: Optional file encoding (auto-detected if None)
        allowed_directories: Optional list of allowed directories (uses defaults if None)
        
    Returns:
        Tuple of (file content as string, mime type)
    
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file can't be accessed
        ValueError: If path is outside allowed directories
    """
    # Use default allowed directories if none provided
    if allowed_directories is None:
        allowed_directories = get_allowed_directories()
    
    # Validate path
    if not validate_path(path, allowed_directories):
        raise ValueError(f"Access denied - path outside allowed directories: {path} not in {', '.join(allowed_directories)}")
    
    # Check if file exists
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    # Check if we have read permission
    if not os.access(path, os.R_OK):
        raise PermissionError(f"Permission denied: Cannot read {path}")
    
    # Detect encoding if not specified
    if encoding is None:
        encoding = detect_encoding(path)
    
    # Read file content
    try:
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
    except UnicodeDecodeError:
        # If text decoding fails, try reading as binary
        try:
            with open(path, 'rb') as f:
                content = f.read().decode('utf-8', errors='replace')
        except Exception as e:
            raise ValueError(f"Error decoding file {path}: {str(e)}")
    
    # Determine mime type
    mime_type = guess_mimetype(path)
    
    return content, mime_type


def write_file(path: str, content: str, encoding: str = "utf-8",
               allowed_directories: Optional[List[str]] = None) -> None:
    """
    Write content to a file.
    
    Args:
        path: Path to the file
        content: Content to write
        encoding: File encoding (default: utf-8)
        allowed_directories: Optional list of allowed directories (uses defaults if None)
        
    Raises:
        PermissionError: If file can't be written
        ValueError: If path is outside allowed directories
    """
    # Use default allowed directories if none provided
    if allowed_directories is None:
        allowed_directories = get_allowed_directories()
    
    # Validate path
    if not validate_path(path, allowed_directories):
        raise ValueError(f"Access denied - path outside allowed directories: {path} not in {', '.join(allowed_directories)}")
    
    # Make sure the directory exists
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            raise PermissionError(f"Cannot create directory {directory}: {str(e)}")
    
    # Check if we have write permission to the directory
    if directory and not os.access(directory, os.W_OK):
        raise PermissionError(f"Permission denied: Cannot write to directory {directory}")
    
    # Check if the file exists and we have write permission
    if os.path.exists(path) and not os.access(path, os.W_OK):
        raise PermissionError(f"Permission denied: Cannot write to {path}")
    
    # Write the content to the file
    try:
        # Use atomic write pattern for better safety
        dir_name = os.path.dirname(path) or "."
        with tempfile.NamedTemporaryFile(mode='w', encoding=encoding, 
                                         dir=dir_name, delete=False) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Rename the temporary file to the target path (atomic operation)
        shutil.move(temp_path, path)
        
    except Exception as e:
        # Clean up the temporary file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
        
        raise ValueError(f"Error writing to {path}: {str(e)}")


def list_directory(path: str, allowed_directories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    List files and directories in a given path.
    
    Args:
        path: Directory path
        allowed_directories: Optional list of allowed directories (uses defaults if None)
        
    Returns:
        List of items with name, type (file/directory), and basic metadata
        
    Raises:
        FileNotFoundError: If directory doesn't exist
        PermissionError: If directory can't be accessed
        ValueError: If path is outside allowed directories
    """
    # Use default allowed directories if none provided
    if allowed_directories is None:
        allowed_directories = get_allowed_directories()
    
    # Validate path
    if not validate_path(path, allowed_directories):
        raise ValueError(f"Access denied - path outside allowed directories: {path} not in {', '.join(allowed_directories)}")
    
    # Check if directory exists
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Directory not found: {path}")
    
    # Check if we have read permission
    if not os.access(path, os.R_OK):
        raise PermissionError(f"Permission denied: Cannot read directory {path}")
    
    # List directory contents
    items = []
    
    try:
        for entry in os.scandir(path):
            item = {
                "name": entry.name,
                "type": "directory" if entry.is_dir() else "file",
                "path": os.path.abspath(entry.path)
            }
            
            try:
                stat_info = entry.stat()
                item.update({
                    "size": stat_info.st_size,
                    "created": stat_info.st_ctime,
                    "modified": stat_info.st_mtime,
                    "accessed": stat_info.st_atime,
                })
                
                if entry.is_file():
                    item["mime_type"] = guess_mimetype(entry.path)
            except:
                # Ignore errors in getting detailed stats
                pass
            
            items.append(item)
    except Exception as e:
        raise ValueError(f"Error listing directory {path}: {str(e)}")
    
    return items


def create_directory(path: str, allowed_directories: Optional[List[str]] = None) -> None:
    """
    Create a new directory.
    
    Args:
        path: Directory path to create
        allowed_directories: Optional list of allowed directories (uses defaults if None)
        
    Raises:
        PermissionError: If directory can't be created
        ValueError: If path is outside allowed directories
    """
    # Use default allowed directories if none provided
    if allowed_directories is None:
        allowed_directories = get_allowed_directories()
    
    # Validate path
    if not validate_path(path, allowed_directories):
        raise ValueError(f"Access denied - path outside allowed directories: {path} not in {', '.join(allowed_directories)}")
    
    # Create directory
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        raise PermissionError(f"Cannot create directory {path}: {str(e)}")


def search_files(path: str, pattern: str, 
                exclude_patterns: Optional[List[str]] = None, 
                recursive: bool = True,
                allowed_directories: Optional[List[str]] = None) -> List[str]:
    """
    Search for files matching a pattern.
    
    Args:
        path: Base directory for search
        pattern: Glob pattern for matching files
        exclude_patterns: Patterns to exclude
        recursive: Whether to search recursively
        allowed_directories: Optional list of allowed directories (uses defaults if None)
        
    Returns:
        List of matching file paths
        
    Raises:
        FileNotFoundError: If base directory doesn't exist
        PermissionError: If directories can't be accessed
        ValueError: If path is outside allowed directories
    """
    # Use default allowed directories if none provided
    if allowed_directories is None:
        allowed_directories = get_allowed_directories()
    
    # Validate path
    if not validate_path(path, allowed_directories):
        raise ValueError(f"Access denied - path outside allowed directories: {path} not in {', '.join(allowed_directories)}")
    
    # Check if directory exists
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Directory not found: {path}")
    
    # Check if we have read permission
    if not os.access(path, os.R_OK):
        raise PermissionError(f"Permission denied: Cannot read directory {path}")
    
    # Handle exclude patterns
    exclude_patterns = exclude_patterns or []
    
    # Prepare results list
    results = []
    
    # Define a function to check if a path should be excluded
    def should_exclude(check_path: str) -> bool:
        for exclude in exclude_patterns:
            if fnmatch.fnmatch(os.path.basename(check_path), exclude):
                return True
        return False
    
    try:
        # Handle recursive vs non-recursive search
        if recursive:
            for root, dirs, files in os.walk(path):
                # Remove directories that match exclude patterns
                dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
                
                # Add matching files
                for name in files:
                    file_path = os.path.join(root, name)
                    if fnmatch.fnmatch(name, pattern) and not should_exclude(file_path):
                        results.append(os.path.abspath(file_path))
        else:
            # Non-recursive search (just the specified directory)
            for entry in os.scandir(path):
                if entry.is_file() and fnmatch.fnmatch(entry.name, pattern) and not should_exclude(entry.path):
                    results.append(os.path.abspath(entry.path))
    
    except Exception as e:
        raise ValueError(f"Error searching in {path}: {str(e)}")
    
    return results


def get_file_info(path: str, allowed_directories: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get detailed information about a file or directory.
    
    Args:
        path: Path to the file or directory
        allowed_directories: Optional list of allowed directories (uses defaults if None)
        
    Returns:
        Dictionary with file/directory information
        
    Raises:
        FileNotFoundError: If file/directory doesn't exist
        PermissionError: If file/directory can't be accessed
        ValueError: If path is outside allowed directories
    """
    # Use default allowed directories if none provided
    if allowed_directories is None:
        allowed_directories = get_allowed_directories()
    
    # Validate path
    if not validate_path(path, allowed_directories):
        raise ValueError(f"Access denied - path outside allowed directories: {path} not in {', '.join(allowed_directories)}")
    
    # Check if path exists
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path not found: {path}")
    
    # Check if we have read permission
    if not os.access(path, os.R_OK):
        raise PermissionError(f"Permission denied: Cannot read {path}")
    
    # Get basic file info
    is_dir = os.path.isdir(path)
    stat_info = os.stat(path)
    
    # Build info dictionary
    info = {
        "name": os.path.basename(path),
        "path": os.path.abspath(path),
        "type": "directory" if is_dir else "file",
        "size": stat_info.st_size,
        "created": stat_info.st_ctime,
        "modified": stat_info.st_mtime,
        "accessed": stat_info.st_atime,
        "permissions": {
            "read": os.access(path, os.R_OK),
            "write": os.access(path, os.W_OK),
            "execute": os.access(path, os.X_OK)
        }
    }
    
    # Add file-specific information
    if not is_dir:
        info["mime_type"] = guess_mimetype(path)
        info["extension"] = os.path.splitext(path)[1].lstrip(".")
    
    # Add directory-specific information
    if is_dir:
        try:
            info["contents"] = {
                "files": sum(1 for entry in os.scandir(path) if entry.is_file()),
                "directories": sum(1 for entry in os.scandir(path) if entry.is_dir())
            }
        except:
            # Ignore errors in counting contents
            pass
    
    return info


def directory_tree(path: str, allowed_directories: Optional[List[str]] = None, 
                  max_depth: int = 10) -> Dict[str, Any]:
    """
    Get a recursive tree view of files and directories.
    
    Args:
        path: Base directory path
        allowed_directories: Optional list of allowed directories (uses defaults if None)
        max_depth: Maximum recursion depth
        
    Returns:
        Tree structure as nested dictionaries
        
    Raises:
        FileNotFoundError: If directory doesn't exist
        PermissionError: If directory can't be accessed
        ValueError: If path is outside allowed directories
    """
    # Use default allowed directories if none provided
    if allowed_directories is None:
        allowed_directories = get_allowed_directories()
    
    # Validate path
    if not validate_path(path, allowed_directories):
        raise ValueError(f"Access denied - path outside allowed directories: {path} not in {', '.join(allowed_directories)}")
    
    # Check if directory exists
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Directory not found: {path}")
    
    # Check if we have read permission
    if not os.access(path, os.R_OK):
        raise PermissionError(f"Permission denied: Cannot read directory {path}")
    
    def build_tree(current_path: str, current_depth: int = 0) -> Dict[str, Any]:
        """Recursively build tree structure"""
        if current_depth > max_depth:
            return {"name": os.path.basename(current_path), "type": "directory", "children": [{"name": "...", "type": "truncated"}]}
        
        result = {
            "name": os.path.basename(current_path),
            "type": "directory",
            "children": []
        }
        
        try:
            for entry in sorted(os.scandir(current_path), key=lambda e: e.name):
                if entry.is_dir():
                    result["children"].append(build_tree(entry.path, current_depth + 1))
                else:
                    result["children"].append({
                        "name": entry.name,
                        "type": "file"
                    })
        except Exception as e:
            # Handle any errors in reading directory contents
            result["error"] = str(e)
        
        return result
    
    return build_tree(path)


# MCP Tool Functions

def read_file_tool(path: str, encoding: Optional[str] = None) -> str:
    """
    MCP Tool: Read file content with proper encoding detection.
    
    Args:
        path: Path to the file
        encoding: Optional file encoding (auto-detected if None)
        
    Returns:
        File content as string
    """
    try:
        content, mime_type = read_file(path, encoding)
        return content
    except Exception as e:
        return f"Error: {str(e)}"


def write_file_tool(path: str, content: str, encoding: str = "utf-8") -> str:
    """
    MCP Tool: Write content to a file.
    
    Args:
        path: Path to the file
        content: Content to write
        encoding: File encoding (default: utf-8)
        
    Returns:
        Success message or error
    """
    try:
        write_file(path, content, encoding)
        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error: {str(e)}"


def list_directory_tool(path: str) -> str:
    """
    MCP Tool: List files and directories in a given path.
    
    Args:
        path: Directory path
        
    Returns:
        Formatted list of files and directories
    """
    try:
        items = list_directory(path)
        
        # Format output for readability
        result = []
        for item in sorted(items, key=lambda x: (x["type"] != "directory", x["name"])):
            prefix = "[DIR] " if item["type"] == "directory" else "[FILE] "
            result.append(f"{prefix}{item['name']}")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error: {str(e)}"


def create_directory_tool(path: str) -> str:
    """
    MCP Tool: Create a new directory.
    
    Args:
        path: Directory path to create
        
    Returns:
        Success message or error
    """
    try:
        create_directory(path)
        return f"Successfully created directory: {path}"
    except Exception as e:
        return f"Error: {str(e)}"


def search_files_tool(path: str, pattern: str, 
                     exclude_patterns: Optional[str] = None,
                     recursive: bool = True) -> str:
    """
    MCP Tool: Search for files matching a pattern.
    
    Args:
        path: Base directory for search
        pattern: Glob pattern for matching files
        exclude_patterns: Comma-separated patterns to exclude
        recursive: Whether to search recursively
        
    Returns:
        Formatted list of matching files
    """
    try:
        exclude_list = None
        if exclude_patterns:
            exclude_list = [p.strip() for p in exclude_patterns.split(",")]
        
        files = search_files(path, pattern, exclude_list, recursive)
        
        if not files:
            return f"No files matching '{pattern}' found in {path}"
        
        return "\n".join(files)
    except Exception as e:
        return f"Error: {str(e)}"


def get_file_info_tool(path: str) -> str:
    """
    MCP Tool: Get detailed information about a file or directory.
    
    Args:
        path: Path to the file or directory
        
    Returns:
        Formatted file/directory information
    """
    try:
        info = get_file_info(path)
        
        # Format output for readability
        result = [
            f"Name: {info['name']}",
            f"Path: {info['path']}",
            f"Type: {info['type'].capitalize()}",
            f"Size: {info['size']} bytes",
            f"Created: {info['created']}",
            f"Modified: {info['modified']}",
            f"Permissions: {'r' if info['permissions']['read'] else '-'}"
                        f"{'w' if info['permissions']['write'] else '-'}"
                        f"{'x' if info['permissions']['execute'] else '-'}"
        ]
        
        if info["type"] == "file":
            result.append(f"MIME Type: {info['mime_type']}")
            result.append(f"Extension: {info['extension']}")
        
        if info["type"] == "directory" and "contents" in info:
            result.append(f"Contents: {info['contents']['files']} files, {info['contents']['directories']} directories")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error: {str(e)}"


def directory_tree_tool(path: str, max_depth: int = 5) -> str:
    """
    MCP Tool: Get a recursive tree view of files and directories.
    
    Args:
        path: Base directory path
        max_depth: Maximum recursion depth
        
    Returns:
        Formatted tree structure
    """
    try:
        tree = directory_tree(path, max_depth=max_depth)
        
        # Convert tree to text representation
        lines = []
        
        def format_tree(node, prefix=""):
            # Add current node
            type_marker = "📂" if node["type"] == "directory" else "📄"
            if node["type"] == "truncated":
                type_marker = "..."
            
            lines.append(f"{prefix}{type_marker} {node['name']}")
            
            # Add children with appropriate indentation
            if "children" in node:
                last_index = len(node["children"]) - 1
                for i, child in enumerate(node["children"]):
                    if i == last_index:
                        # Last item gets a different prefix
                        format_tree(child, prefix + "    ")
                    else:
                        # Not the last item
                        format_tree(child, prefix + "│   ")
        
        format_tree(tree)
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"


def list_allowed_directories_tool() -> str:
    """
    MCP Tool: List directories that are allowed to be accessed.
    
    Returns:
        List of allowed directories
    """
    allowed_dirs = get_allowed_directories()
    if not allowed_dirs:
        return "No allowed directories configured."
    
    return "Allowed directories:\n" + "\n".join(allowed_dirs)


# Register these functions as MCP tools when setting up the server
def register_filesystem_tools(mcp_server) -> None:
    """Register filesystem tools with the MCP server"""
    mcp_server.tool()(read_file_tool)
    mcp_server.tool()(write_file_tool)
    mcp_server.tool()(list_directory_tool)
    mcp_server.tool()(create_directory_tool)
    mcp_server.tool()(search_files_tool)
    mcp_server.tool()(get_file_info_tool)
    mcp_server.tool()(directory_tree_tool)
    mcp_server.tool()(list_allowed_directories_tool)
