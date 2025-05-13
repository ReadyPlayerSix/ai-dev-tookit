#!/usr/bin/env python3
"""
Install Tool Index

This script installs the AI-optimized Tool Index into a project.
It copies the necessary scripts to the project and runs the builder.

Usage:
    python install_tool_index.py [--project-path PATH] [--clean]
"""

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path

# List of scripts to install
SCRIPTS = [
    "tool_index_builder.py",
    "tool_index_generator.py",
    "tool_profiles_generator.py",
    "tool_relationships_generator.py",
    "context_validation_generator.py"
]

def copy_scripts(source_dir, target_dir):
    """Copy the Tool Index scripts to the target directory."""
    os.makedirs(target_dir, exist_ok=True)
    
    for script in SCRIPTS:
        source_path = os.path.join(source_dir, script)
        target_path = os.path.join(target_dir, script)
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, target_path)
            print(f"✅ Copied {script} to {target_dir}")
        else:
            print(f"⚠️ Script not found: {source_path}")
    
    # Make scripts executable on Unix
    if os.name == 'posix':
        for script in SCRIPTS:
            script_path = os.path.join(target_dir, script)
            if os.path.exists(script_path):
                os.chmod(script_path, 0o755)

def main():
    """Main function to install the Tool Index."""
    parser = argparse.ArgumentParser(description="Install the AI-optimized Tool Index")
    parser.add_argument(
        "--project-path", 
        type=str, 
        default=".",
        help="Path to the project directory (default: current directory)"
    )
    parser.add_argument(
        "--scripts-dir",
        type=str,
        default="scripts/tool_index",
        help="Directory to install the scripts in (default: scripts/tool_index)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean up existing .tool_reference directory"
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Don't run the builder after installation"
    )
    
    args = parser.parse_args()
    project_path = os.path.abspath(args.project_path)
    scripts_dir = os.path.join(project_path, args.scripts_dir)
    
    # Print banner
    print("\n" + "=" * 80)
    print("              AI-Optimized Tool Index Installer")
    print("=" * 80)
    print(f"Project path: {project_path}")
    print(f"Scripts directory: {scripts_dir}")
    print("")
    
    # Copy scripts to the project
    copy_scripts(os.path.dirname(os.path.abspath(__file__)), scripts_dir)
    
    # Run the builder
    if not args.no_build:
        builder_script = os.path.join(scripts_dir, "tool_index_builder.py")
        if os.path.exists(builder_script):
            print("\nRunning Tool Index Builder...")
            build_cmd = [sys.executable, builder_script, "--project-path", project_path]
            
            if args.clean:
                build_cmd.append("--clean")
            
            try:
                subprocess.run(build_cmd, check=True)
                print("\n✅ Tool Index successfully installed and built!")
            except subprocess.CalledProcessError:
                print("\n⚠️ Tool Index installation completed, but build failed.")
                return 1
        else:
            print(f"\n⚠️ Builder script not found at {builder_script}")
            return 1
    else:
        print("\n✅ Tool Index scripts installed successfully!")
        print("\nTo build the Tool Index, run:")
        print(f"  python {os.path.join(args.scripts_dir, 'tool_index_builder.py')} --all")
    
    # Print next steps
    print("\nNext steps:")
    print("1. Review the Tool Index at: " + os.path.join(project_path, ".tool_reference"))
    print("2. Test the context validator: python context_validator.py --check all")
    print("3. Explore the tool profiles to understand how Claude will use tools")
    print("")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
