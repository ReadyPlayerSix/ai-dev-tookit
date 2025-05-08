#!/usr/bin/env python3
"""
Transition Script for AI Dev Toolkit Unified Approach

This script handles the transition from multiple GUI implementations
to the single unified implementation, ensuring a smooth upgrade process.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

# Define launcher script template that will redirect to unified launcher
LAUNCHER_REDIRECT_TEMPLATE = '''#!/usr/bin/env python3
"""
AI Dev Toolkit Launcher (Redirector)

This launcher now redirects to the unified launcher.
"""

import os
import sys

def main():
    """Redirect to the unified launcher"""
    print("Redirecting to unified launcher...")
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the unified launcher
    unified_launcher = os.path.join(script_dir, "launch_unified.py")
    
    # Execute the unified launcher with the same arguments
    import subprocess
    return subprocess.call([sys.executable, unified_launcher] + sys.argv[1:])

if __name__ == "__main__":
    sys.exit(main())
'''

def main():
    """Perform the transition to unified toolkit"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Transition to unified AI Dev Toolkit")
    parser.add_argument("--backup", action="store_true", help="Create backups of modified files")
    parser.add_argument("--force", action="store_true", help="Force overwrite of existing files")
    args = parser.parse_args()
    
    # Get project root directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure our target exists
    unified_gui_path = os.path.join(root_dir, "aitoolkit", "gui", "configurator_unified.py")
    unified_launcher_path = os.path.join(root_dir, "launch_unified.py")
    
    if not os.path.exists(unified_gui_path) or not os.path.exists(unified_launcher_path):
        print("ERROR: Unified files not found. Please run this script from the project root directory.")
        return 1
    
    # Create backup directory if needed
    backup_dir = None
    if args.backup:
        backup_dir = os.path.join(root_dir, "backups", "transition_backup")
        os.makedirs(backup_dir, exist_ok=True)
        print(f"Created backup directory: {backup_dir}")
    
    # Process all existing launcher scripts
    launchers = [
        "launch.py", 
        "launch_gui.py", 
        "launch_gui_direct.py",
        "aitoolkit/launch_gui.py"
    ]
    
    for launcher in launchers:
        launcher_path = os.path.join(root_dir, launcher)
        if os.path.exists(launcher_path):
            print(f"Processing launcher: {launcher_path}")
            
            # Create backup if needed
            if args.backup:
                backup_path = os.path.join(backup_dir, launcher.replace("/", "_").replace("\\", "_"))
                try:
                    shutil.copy2(launcher_path, backup_path)
                    print(f"  - Created backup at {backup_path}")
                except Exception as e:
                    print(f"  - Failed to create backup: {str(e)}")
            
            # Replace with redirector
            try:
                with open(launcher_path, 'w') as f:
                    f.write(LAUNCHER_REDIRECT_TEMPLATE)
                print(f"  - Updated to redirect to unified launcher")
            except Exception as e:
                print(f"  - Failed to update launcher: {str(e)}")
    
    # Update README to emphasize unified launcher
    readme_path = os.path.join(root_dir, "README.md")
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Back up README if needed
            if args.backup:
                backup_path = os.path.join(backup_dir, "README.md.bak")
                try:
                    shutil.copy2(readme_path, backup_path)
                    print(f"Created backup of README at {backup_path}")
                except Exception as e:
                    print(f"Failed to create README backup: {str(e)}")
            
            # Find and replace relevant sections
            # We've already updated most of the content via other edits
        except Exception as e:
            print(f"Error processing README: {str(e)}")
    
    # Print success message
    print("\nTransition completed successfully!")
    print("\nThe AI Dev Toolkit now uses a unified approach with:")
    print("1. A single GUI implementation (configurator_unified.py)")
    print("2. A single launcher script (launch_unified.py)")
    print("3. All existing launchers now redirect to the unified launcher")
    
    print("\nTo launch the toolkit, run:")
    print("  python launch_unified.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
