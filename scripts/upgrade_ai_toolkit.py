#!/usr/bin/env python3
"""
AI Development Toolkit Upgrade Script

This script provides a convenient way to upgrade AI Development Toolkit installations
for projects. It wraps the UpgradeManager functionality with a simplified interface.

Usage:
    python upgrade_ai_toolkit.py /path/to/project
    python upgrade_ai_toolkit.py --analyze /path/to/project
    python upgrade_ai_toolkit.py --force /path/to/project
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from aitoolkit.utils.upgrade_manager import UpgradeManager
except ImportError:
    print("Error: Could not import UpgradeManager. Make sure AI Development Toolkit is installed.")
    sys.exit(1)


def main():
    """Main function that parses arguments and runs the upgrade."""
    parser = argparse.ArgumentParser(
        description="Upgrade AI Development Toolkit installations for projects"
    )
    
    parser.add_argument(
        "project_path", 
        help="Path to the project to upgrade or analyze"
    )
    
    parser.add_argument(
        "--analyze", 
        action="store_true", 
        help="Analyze the project without making changes"
    )
    
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force upgrade even if not needed"
    )
    
    parser.add_argument(
        "--no-backup", 
        action="store_true", 
        help="Skip creating a backup of the .ai_reference directory"
    )
    
    parser.add_argument(
        "--no-claude-md", 
        action="store_true", 
        help="Skip creating or updating CLAUDE.md"
    )
    
    parser.add_argument(
        "--no-git", 
        action="store_true", 
        help="Skip setting up git tracking"
    )
    
    args = parser.parse_args()
    
    # Resolve path to absolute
    project_path = os.path.abspath(args.project_path)
    
    # Validate project path
    if not os.path.exists(project_path):
        print(f"Error: Project path '{project_path}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(project_path):
        print(f"Error: Project path '{project_path}' is not a directory.")
        sys.exit(1)
    
    # Run analysis or upgrade
    if args.analyze:
        print(f"Analyzing project at '{project_path}'...")
        results = UpgradeManager.analyze_project(project_path)
        
        # Print results in a readable format
        print("\nAnalysis Results:")
        print(f"Project Path: {results['recommendations']['project_path']}")
        print(f"Current Version: {results['current_version']}")
        print(f"Latest Version: {results['latest_version']}")
        print(f"Needs Upgrade: {results['needs_upgrade']}")
        
        print("\nProject Characteristics:")
        characteristics = results['recommendations']
        for key, value in characteristics.items():
            if key not in ['project_path', 'timestamp', 'recommendations'] and value:
                print(f"- {key.replace('_', ' ').title()}: {value}")
        
        print("\nRecommended Actions:")
        recommendations = results['recommendations']['recommendations']
        for key, value in recommendations.items():
            if value:
                print(f"- {key.replace('_', ' ').title()}")
    else:
        print(f"Upgrading project at '{project_path}'...")
        results = UpgradeManager.upgrade(
            project_path,
            backup=not args.no_backup,
            claude_md=not args.no_claude_md,
            git_tracking=not args.no_git,
            force=args.force
        )
        
        # Print results
        print("\nUpgrade Results:")
        print(f"Success: {results['success']}")
        print(f"Message: {results['message']}")
        
        # Print details of steps performed
        if 'steps' in results:
            print("\nSteps Performed:")
            for step, details in results['steps'].items():
                success = details.get('success', False)
                status = "✓" if success else "✗"
                print(f"- {step.replace('_', ' ').title()}: {status}")
                
                # Print additional details for backup
                if step == 'backup' and success and 'backup_path' in details:
                    print(f"  Backup created at: {details['backup_path']}")
                
                # Print error messages
                if not success and 'error' in details:
                    print(f"  Error: {details['error']}")


if __name__ == "__main__":
    main()