"""
AI Librarian Filesystem Enhancement Module

This module implements enhanced filesystem operations for the AI Librarian.
Functions here are adapted from src/librarian/filesystem.py.
"""
import os
import sys
import glob
import json
import shutil
import fnmatch
import tempfile
import mimetypes
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any, Set, Union

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

def create_directory(path: str, allowed_directories: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Create a new directory or ensure a directory exists.
    
    Can create multiple nested directories in one operation. If the directory already
    exists, this operation will succeed silently. Perfect for setting up directory
    structures for projects or ensuring required paths exist.
    
    Args:
        path: Directory path to create
        allowed_directories: Optional list of allowed directories (uses defaults if None)
        
    Returns:
        Dictionary with result information
    """
    try:
        # Normalize the path
        dir_path = os.path.abspath(path)
        
        # Validate path against allowed directories
        if not any(dir_path.startswith(allowed_dir) for allowed_dir in allowed_directories):
            return {
                "status": "error",
                "message": f"Access denied: {path} is not within allowed directories"
            }
        
        # Create the directory
        os.makedirs(dir_path, exist_ok=True)
        
        # Return information about the operation
        return {
            "status": "success",
            "message": f"Directory created or already exists: {path}",
            "path": path,
            "absolute_path": dir_path
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating directory: {str(e)}"
        }

def directory_tree(path: str, allowed_directories: List[str]) -> Dict[str, Any]:
    """
    Get a recursive tree view of files and directories as a JSON structure.
    
    Each entry includes 'name', 'type' (file/directory), and 'children' for directories.
    Files have no children array, while directories always have a children array
    (which may be empty).
    
    Args:
        path: Base directory path
        allowed_directories: List of allowed directories
        
    Returns:
        Dictionary with tree structure or error information
    """
    try:
        # Normalize path
        base_path = os.path.abspath(path)
        
        # Validate path
        if not any(base_path.startswith(allowed_dir) for allowed_dir in allowed_directories):
            return {
                "status": "error",
                "message": f"Access denied: {path} is not within allowed directories"
            }
        
        # Check if directory exists
        if not os.path.isdir(base_path):
            return {
                "status": "error",
                "message": f"Directory not found: {path}"
            }
        
        # Build the tree structure
        def build_tree(dir_path):
            """Recursively build the tree structure"""
            name = os.path.basename(dir_path) or dir_path
            result = {
                "name": name,
                "type": "directory",
                "children": []
            }
            
            try:
                # Sort entries by name, directories first
                entries = sorted(os.scandir(dir_path), 
                                key=lambda e: (not e.is_dir(), e.name))
                
                for entry in entries:
                    # Skip hidden files and special directories
                    if entry.name.startswith('.') or entry.name in ['__pycache__', 'node_modules']:
                        continue
                        
                    if entry.is_dir():
                        # Add subdirectory
                        result["children"].append(build_tree(entry.path))
                    else:
                        # Add file (no children property for files)
                        result["children"].append({
                            "name": entry.name,
                            "type": "file"
                        })
            except Exception as e:
                result["error"] = str(e)
            
            return result
        
        # Build the tree starting from the base path
        tree = build_tree(base_path)
        
        return {
            "status": "success",
            "path": path,
            "tree": tree
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating directory tree: {str(e)}"
        }

def get_file_info(path: str, allowed_directories: List[str]) -> Dict[str, Any]:
    """
    Retrieve detailed metadata about a file or directory.
    
    Returns comprehensive information including size, creation time, last modified time,
    permissions, and type.
    
    Args:
        path: Path to the file or directory
        allowed_directories: List of allowed directories
        
    Returns:
        Dictionary with file/directory information or error
    """
    try:
        # Normalize path
        file_path = os.path.abspath(path)
        
        # Validate path
        if not any(file_path.startswith(allowed_dir) for allowed_dir in allowed_directories):
            return {
                "status": "error",
                "message": f"Access denied: {path} is not within allowed directories"
            }
        
        # Check if path exists
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "message": f"Path not found: {path}"
            }
        
        # Get basic file information
        is_dir = os.path.isdir(file_path)
        stat_info = os.stat(file_path)
        
        # Build the information dictionary
        info = {
            "status": "success",
            "path": path,
            "absolute_path": file_path,
            "name": os.path.basename(file_path),
            "type": "directory" if is_dir else "file",
            "size": stat_info.st_size,
            "created": stat_info.st_ctime,
            "modified": stat_info.st_mtime,
            "accessed": stat_info.st_atime,
            "permissions": {
                "read": os.access(file_path, os.R_OK),
                "write": os.access(file_path, os.W_OK),
                "execute": os.access(file_path, os.X_OK)
            }
        }
        
        # Add file-specific information
        if not is_dir:
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = "application/octet-stream"
                
            # Add file extension
            _, ext = os.path.splitext(file_path)
            extension = ext.lstrip(".") if ext else ""
            
            # Add to info
            info.update({
                "mime_type": mime_type,
                "extension": extension
            })
        
        # Add directory-specific information
        if is_dir:
            try:
                files_count = 0
                dirs_count = 0
                for entry in os.scandir(file_path):
                    if entry.is_dir():
                        dirs_count += 1
                    else:
                        files_count += 1
                
                info["contents"] = {
                    "files": files_count,
                    "directories": dirs_count,
                    "total": files_count + dirs_count
                }
            except Exception as e:
                info["contents_error"] = str(e)
        
        return info
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting file info: {str(e)}"
        }

def enhanced_search_files(path: str, pattern: str, excludePatterns: List[str] = None, 
                         allowed_directories: List[str] = None) -> Dict[str, Any]:
    """
    Recursively search for files and directories matching a pattern.
    
    Enhanced version that includes the ability to exclude specific patterns from results.
    
    Args:
        path: The starting directory path to search in
        pattern: The search pattern to match (case-insensitive)
        excludePatterns: Optional list of patterns to exclude from results
        allowed_directories: List of allowed directory paths
        
    Returns:
        Dictionary with search results or error
    """
    try:
        # Normalize path
        search_path = os.path.abspath(path)
        
        # Validate path
        if not any(search_path.startswith(allowed_dir) for allowed_dir in allowed_directories):
            return {
                "status": "error",
                "message": f"Access denied: {path} is not within allowed directories"
            }
        
        # Check if directory exists
        if not os.path.exists(search_path):
            return {
                "status": "error",
                "message": f"Directory not found: {path}"
            }
        
        # Check if path is a directory
        if not os.path.isdir(search_path):
            return {
                "status": "error",
                "message": f"Not a directory: {path}"
            }
        
        # Ensure excludePatterns is a list
        exclude_patterns = excludePatterns or []
        
        # Convert pattern to lowercase for case-insensitive matching
        pattern_lower = pattern.lower()
        
        # Define function to check if a path should be excluded
        def should_exclude(item_path):
            base_name = os.path.basename(item_path)
            # Check if matches any exclude patterns
            for exclude in exclude_patterns:
                if fnmatch.fnmatch(base_name.lower(), exclude.lower()):
                    return True
                # Also check if parent directory matches exclude pattern
                if any(fnmatch.fnmatch(part.lower(), exclude.lower()) 
                       for part in Path(item_path).parts):
                    return True
            # Skip common directories and hidden files/dirs by default
            if base_name.startswith('.') or base_name in ['__pycache__', 'node_modules', '.git', 'venv', 'env']:
                return True
            return False
        
        # Collect matching files
        matches = []
        
        for root, dirs, files in os.walk(search_path):
            # Filter out directories that should be excluded
            # This modifies dirs in-place to avoid traversing excluded dirs
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
            
            # Check files that match the pattern
            for file in files:
                file_path = os.path.join(root, file)
                if pattern_lower in file.lower() and not should_exclude(file_path):
                    # Return path relative to the search directory
                    rel_path = os.path.relpath(file_path, search_path)
                    matches.append(rel_path)
        
        # Return the results
        return {
            "status": "success",
            "path": path,
            "pattern": pattern,
            "excludePatterns": exclude_patterns,
            "matches": matches,
            "count": len(matches),
            "message": f"Found {len(matches)} matching files in {path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error searching files: {str(e)}"
        }
