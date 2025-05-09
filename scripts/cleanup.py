#!/usr/bin/env python3
"""
AI Dev Toolkit Project Cleanup Script

This script cleans up the project directory by removing unnecessary files,
moving legacy files to the legacy directory, and organizing the codebase.
"""

import os
import sys
import shutil
from pathlib import Path

def print_colored(text, color="green"):
    """Print colored text to the console."""
    colors = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "reset": "\033[0m"
    }
    
    # Check if we're in a terminal that supports colors
    if sys.stdout.isatty():
        print(f"{colors.get(color, '')}{text}{colors['reset']}")
    else:
        print(text)

def cleanup_project():
    """Clean up the project directory."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.absolute()
    legacy_dir = project_root / "legacy"
    
    # Ensure the legacy directory exists
    os.makedirs(legacy_dir, exist_ok=True)
    
    # Files to delete
    files_to_delete = [
        # Backup/temporary files
        "aitoolkit/librarian/server.py.bak",
        "aitoolkit/gui/configurator.py.backup",
        "aitoolkit/gui/configurator.py.fixed",
        "aitoolkit/gui/configurator_new.py.fixed",
        "aitoolkit/gui/__init__.py.old",
        "aitoolkit/gui/configurator.py.updated",
        # Test files
        "aitoolkit/test_file.txt",
        # The gitStatus.txt file
        "gitStatus.txt",
    ]
    
    # Files to move to legacy
    files_to_legacy = [
        # Deprecated configurator files
        "aitoolkit/gui/configurator_fixed.py",
        "aitoolkit/gui/configurator_legacy.py",
        "aitoolkit/gui/configurator_test.py",
    ]
    
    # Directories to delete
    dirs_to_delete = [
        "aitoolkit/librarian/filesystem_old",
    ]
    
    # Directories to move to legacy
    dirs_to_legacy = [
        "test_directory",
    ]
    
    # Process files to delete
    print_colored("\nDeleting unnecessary files:", "blue")
    for file_path in files_to_delete:
        full_path = project_root / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print_colored(f"✓ Deleted: {file_path}", "green")
            except Exception as e:
                print_colored(f"✗ Error deleting {file_path}: {e}", "red")
        else:
            print_colored(f"! File not found: {file_path}", "yellow")
    
    # Process files to move to legacy
    print_colored("\nMoving files to legacy directory:", "blue")
    for file_path in files_to_legacy:
        full_path = project_root / file_path
        if full_path.exists():
            legacy_path = legacy_dir / file_path
            try:
                # Create the destination directory
                os.makedirs(os.path.dirname(legacy_path), exist_ok=True)
                # Move the file
                shutil.move(full_path, legacy_path)
                print_colored(f"✓ Moved to legacy: {file_path}", "green")
            except Exception as e:
                print_colored(f"✗ Error moving {file_path}: {e}", "red")
        else:
            print_colored(f"! File not found: {file_path}", "yellow")
    
    # Process directories to delete
    print_colored("\nDeleting unnecessary directories:", "blue")
    for dir_path in dirs_to_delete:
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            try:
                shutil.rmtree(full_path)
                print_colored(f"✓ Deleted directory: {dir_path}", "green")
            except Exception as e:
                print_colored(f"✗ Error deleting directory {dir_path}: {e}", "red")
        else:
            print_colored(f"! Directory not found: {dir_path}", "yellow")
    
    # Process directories to move to legacy
    print_colored("\nMoving directories to legacy:", "blue")
    for dir_path in dirs_to_legacy:
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            legacy_path = legacy_dir / dir_path
            try:
                # Create the destination directory parent if needed
                os.makedirs(os.path.dirname(legacy_path) if os.path.dirname(legacy_path) else legacy_dir, exist_ok=True)
                # Move the directory
                shutil.move(full_path, legacy_path)
                print_colored(f"✓ Moved directory to legacy: {dir_path}", "green")
            except Exception as e:
                print_colored(f"✗ Error moving directory {dir_path}: {e}", "red")
        else:
            print_colored(f"! Directory not found: {dir_path}", "yellow")

    # Print summary
    print_colored("\nCleanup complete!", "green")
    print_colored("The project directory has been cleaned up and organized.", "green")
    print_colored("Legacy files and directories have been moved to the legacy directory.", "green")

if __name__ == "__main__":
    # Confirm before proceeding
    print("AI Dev Toolkit Project Cleanup")
    print("==============================")
    print("This script will clean up the project directory by removing unnecessary files,")
    print("moving legacy files to the legacy directory, and organizing the codebase.")
    print()
    proceed = input("Do you want to proceed? (y/n): ").lower() == 'y'
    
    if proceed:
        cleanup_project()
    else:
        print("Cleanup cancelled.")
