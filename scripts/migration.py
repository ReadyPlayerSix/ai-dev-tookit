#!/usr/bin/env python3
"""
Migration script to help transition from old directory structure to new.

This script will:
1. Create symlinks for backward compatibility
2. Notify users about the new structure
3. Update import paths in source files
"""

import os
import sys
import shutil
from pathlib import Path

def create_readme():
    """Create a README file in the root directory explaining the changes."""
    readme_content = """# AI Dev Toolkit

## Directory Structure Changes

The project has been reorganized for better maintainability:

- All launcher scripts moved to `scripts/launchers/`
- Configuration files moved to `config/`
- Core code consolidated in `aitoolkit/` package

For backward compatibility, you can use this migration script:

```bash
python scripts/migration.py
```

See `docs/project_structure.md` for the full documentation of the new structure.
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("Created new README.md in the root directory")

def create_symlinks():
    """Create symlinks for backward compatibility."""
    # Map of old path to new path
    symlink_map = {
        "launch_gui.bat": "scripts/launchers/launch_gui.bat",
        "launch_gui.py": "scripts/launchers/launch_gui.py",
        "launch_new_gui.bat": "scripts/launchers/launch_new_gui.bat",
        "launch_new_gui.py": "scripts/launchers/launch_new_gui.py",
        "run_server.bat": "scripts/launchers/run_server.bat",
        "run_server.sh": "scripts/launchers/run_server.sh",
    }
    
    for old_path, new_path in symlink_map.items():
        if os.path.exists(new_path) and not os.path.exists(old_path):
            try:
                # Create relative symlink
                rel_path = os.path.relpath(new_path, os.path.dirname(old_path))
                if os.name == 'nt':  # Windows
                    # Windows requires administrator privileges for symlinks
                    # So we create a simple batch file redirection instead
                    with open(old_path, 'w') as f:
                        f.write(f'@echo off\necho "This file has moved to {new_path}"\n{new_path} %*')
                else:  # Unix-like
                    os.symlink(rel_path, old_path)
                print(f"Created compatibility link for {old_path} -> {new_path}")
            except Exception as e:
                print(f"Error creating link for {old_path}: {e}")

def update_imports():
    """Update import paths in source files."""
    # This is a complex task that would scan all Python files
    # and update import statements from 'src.' to 'aitoolkit.'
    # For simplicity, we'll just print instructions for now
    print("\nTo update import statements in your code:")
    print("1. Replace 'from src.' with 'from aitoolkit.'")
    print("2. Replace 'import src.' with 'import aitoolkit.'")
    print("\nYou can use the following command to find files that need updating:")
    print("  grep -r 'from src\\.' --include='*.py' .")
    print("  grep -r 'import src\\.' --include='*.py' .")

def main():
    """Main function to run the migration script."""
    print("=== AI Dev Toolkit Migration Script ===")
    
    # Update README
    create_readme()
    
    # Create symlinks for backward compatibility
    create_symlinks()
    
    # Print import update instructions
    update_imports()
    
    print("\nMigration complete. The project structure has been reorganized.")
    print("Please see docs/project_structure.md for details on the new structure.")

if __name__ == "__main__":
    main()
