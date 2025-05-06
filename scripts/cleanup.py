#!/usr/bin/env python3
"""
Cleanup script to remove empty directories after migration.

This script will:
1. Check if directories are empty (except for __pycache__)
2. Remove empty directories
3. Print a summary of changes
"""

import os
import shutil
import sys
from pathlib import Path

def is_empty_dir(path):
    """
    Check if a directory is empty (ignoring __pycache__).
    
    Args:
        path: Directory path to check
        
    Returns:
        bool: True if directory is empty (except for __pycache__), False otherwise
    """
    # List all items in the directory
    items = os.listdir(path)
    
    # Filter out __pycache__ directories
    non_cache_items = [item for item in items if item != "__pycache__"]
    
    # If there are no non-cache items, the directory is considered empty
    return len(non_cache_items) == 0

def remove_empty_dirs():
    """
    Remove empty directories from the project.
    
    Returns:
        list: List of removed directories
    """
    # Directories to check
    dirs_to_check = [
        "ai-librarian-server",
        "gui",
        "src"
    ]
    
    removed_dirs = []
    
    for dir_name in dirs_to_check:
        dir_path = Path(dir_name)
        
        if not dir_path.exists():
            print(f"Directory {dir_name} does not exist, skipping...")
            continue
            
        if not dir_path.is_dir():
            print(f"{dir_name} is not a directory, skipping...")
            continue
            
        if is_empty_dir(dir_path):
            # Remove __pycache__ directory if it exists
            pycache_path = dir_path / "__pycache__"
            if pycache_path.exists():
                shutil.rmtree(pycache_path)
                print(f"Removed {pycache_path}")
                
            # Remove the empty directory
            os.rmdir(dir_path)
            removed_dirs.append(str(dir_path))
            print(f"Removed empty directory {dir_path}")
        else:
            print(f"Directory {dir_path} is not empty, skipping...")
            
    return removed_dirs

def main():
    """Main function to run the cleanup script."""
    print("=== AI Dev Toolkit Cleanup Script ===")
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to project root directory
    os.chdir(os.path.dirname(script_dir))
    
    print(f"Working directory: {os.getcwd()}")
    
    # Remove empty directories
    removed_dirs = remove_empty_dirs()
    
    # Print summary
    if removed_dirs:
        print("\nRemoved directories:")
        for dir_path in removed_dirs:
            print(f"- {dir_path}")
        print("\nCleanup complete.")
    else:
        print("\nNo directories were removed.")

if __name__ == "__main__":
    main()
