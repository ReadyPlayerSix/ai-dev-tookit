#!/usr/bin/env python3
"""
Clear all __pycache__ directories in the project.

This script helps resolve issues with cached Python modules by removing
all __pycache__ directories and .pyc files from the project.
"""

import os
import shutil
import sys

def clear_pycache(directory):
    """Clear all __pycache__ directories and .pyc files in the given directory."""
    # Count of removed items
    removed_dirs = 0
    removed_files = 0
    
    # Walk the directory tree
    for root, dirs, files in os.walk(directory):
        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                print(f"Removing {pycache_path}")
                shutil.rmtree(pycache_path)
                removed_dirs += 1
                # Remove '__pycache__' from dirs to avoid os.walk going into it before it's deleted
                dirs.remove('__pycache__')
            except Exception as e:
                print(f"Error removing {pycache_path}: {e}")
        
        # Remove .pyc files
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                try:
                    print(f"Removing {pyc_path}")
                    os.remove(pyc_path)
                    removed_files += 1
                except Exception as e:
                    print(f"Error removing {pyc_path}: {e}")
    
    return removed_dirs, removed_files

def main():
    """Main function."""
    # Get the project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Clearing __pycache__ directories in {script_dir}")
    print("-" * 50)
    
    removed_dirs, removed_files = clear_pycache(script_dir)
    
    print("-" * 50)
    print(f"Removed {removed_dirs} __pycache__ directories and {removed_files} .pyc files")
    
    # Clear Python's import cache
    print("Clearing Python's import cache...")
    import importlib
    for module_name in list(sys.modules.keys()):
        if module_name.startswith('aitoolkit'):
            try:
                del sys.modules[module_name]
                print(f"Removed module from sys.modules: {module_name}")
            except:
                pass
    
    return 0

if __name__ == '__main__':
    sys.exit(main())