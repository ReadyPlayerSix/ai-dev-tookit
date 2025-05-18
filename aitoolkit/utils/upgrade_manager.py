"""
Upgrade Manager for AI Development Toolkit

This module provides functionality for upgrading AI Development Toolkit installations,
both for self-hosted systems and Claude Code integrations.

It includes tools for:
- Analyzing project structure to recommend features
- Comparing versions to determine if upgrades are needed
- Backing up existing configurations before upgrading
- Upgrading AI reference systems with minimal disruption
- Configuring the system for optimal use with different project types

Usage examples:
    # Check if an upgrade is needed
    needs_upgrade = UpgradeManager.needs_upgrade(project_path)
    
    # Analyze a project without making changes
    recommendations = UpgradeManager.analyze_project(project_path)
    
    # Perform an upgrade
    UpgradeManager.upgrade(project_path)
    
    # Or use the command-line interface
    # python -m aitoolkit.utils.upgrade_manager analyze /path/to/project
    # python -m aitoolkit.utils.upgrade_manager upgrade /path/to/project
"""

import os
import re
import sys
import json
import shutil
import logging
import argparse
import datetime
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from pathlib import Path

# Local imports
try:
    from ..librarian.ai_dev_toolkit import initialize_ai_dev_toolkit
    from ..librarian.filesystem import get_directory_structure
    from ..utils.git_tracker import is_git_repository, get_repository_status
except ImportError:
    # For standalone use
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from aitoolkit.librarian.ai_dev_toolkit import initialize_ai_dev_toolkit
    from aitoolkit.librarian.filesystem import get_directory_structure
    from aitoolkit.utils.git_tracker import is_git_repository, get_repository_status

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("upgrade_manager")

# Current version of the AI Development Toolkit
CURRENT_VERSION = "0.7.5"  # Should match the current release version


class Version:
    """Class for parsing and comparing semantic version strings."""
    
    def __init__(self, version_str: str):
        """
        Parse a version string into components.
        
        Args:
            version_str: A version string like "0.5.5" or "0.5.5-git-integration"
        """
        # Handle suffixes like -alpha, -beta, -git-integration, etc.
        if "-" in version_str:
            base_version, self.suffix = version_str.split("-", 1)
        else:
            base_version, self.suffix = version_str, ""
            
        # Parse version components
        parts = base_version.split(".")
        self.major = int(parts[0]) if len(parts) > 0 else 0
        self.minor = int(parts[1]) if len(parts) > 1 else 0
        self.patch = int(parts[2]) if len(parts) > 2 else 0
        
        # Original string for display purposes
        self.version_str = version_str
        
    def __str__(self) -> str:
        return self.version_str
        
    def __eq__(self, other) -> bool:
        if not isinstance(other, Version):
            other = Version(str(other))
        return (self.major == other.major and 
                self.minor == other.minor and 
                self.patch == other.patch and
                self.suffix == other.suffix)
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Version):
            other = Version(str(other))
            
        # Compare major, minor, patch versions
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
            
        # If base versions are equal, compare suffixes
        # No suffix beats any suffix
        if not self.suffix and other.suffix:
            return False
        if self.suffix and not other.suffix:
            return True
            
        # Compare suffixes alphabetically if both exist
        return self.suffix < other.suffix


class FeatureRecommender:
    """Recommends features based on project structure analysis."""
    
    @staticmethod
    def analyze_python_project(structure: Dict) -> Dict[str, bool]:
        """
        Analyze a Python project structure for specific features.
        
        Args:
            structure: A dictionary representing the project structure
            
        Returns:
            A dictionary of feature recommendations for Python projects
        """
        has_tests = False
        has_requirements = False
        has_setup = False
        has_flask = False
        has_django = False
        has_fastapi = False
        
        # Flatten the structure for easier searching
        flat_files = []
        def flatten_structure(struct, path=""):
            if isinstance(struct, dict):
                for key, value in struct.items():
                    new_path = f"{path}/{key}" if path else key
                    flatten_structure(value, new_path)
            elif isinstance(struct, list):
                for item in struct:
                    flat_files.append(f"{path}/{item}" if path else item)
        
        flatten_structure(structure)
        
        # Analyze files
        for file_path in flat_files:
            if "/tests/" in file_path or file_path.startswith("tests/"):
                has_tests = True
            if file_path.endswith("requirements.txt"):
                has_requirements = True
            if file_path.endswith("setup.py") or file_path.endswith("pyproject.toml"):
                has_setup = True
                
            # Check for web frameworks
            if file_path.endswith(".py"):
                # This is just a heuristic - for a real implementation we'd 
                # need to scan file contents
                lower_path = file_path.lower()
                if "flask" in lower_path or "app.py" in lower_path:
                    has_flask = True
                if "django" in lower_path or "wsgi.py" in lower_path or "settings.py" in lower_path:
                    has_django = True
                if "fastapi" in lower_path:
                    has_fastapi = True
        
        return {
            "python_project": True,
            "has_tests": has_tests,
            "has_requirements": has_requirements,
            "has_setup": has_setup,
            "has_flask": has_flask,
            "has_django": has_django,
            "has_fastapi": has_fastapi,
            "needs_test_tools": has_tests,
            "needs_package_tools": has_requirements or has_setup,
            "needs_web_tools": has_flask or has_django or has_fastapi
        }
    
    @staticmethod
    def analyze_web_project(structure: Dict) -> Dict[str, bool]:
        """
        Analyze a web project structure for specific features.
        
        Args:
            structure: A dictionary representing the project structure
            
        Returns:
            A dictionary of feature recommendations for web projects
        """
        has_node = False
        has_webpack = False
        has_react = False
        has_vue = False
        has_angular = False
        
        # Flatten the structure for easier searching
        flat_files = []
        def flatten_structure(struct, path=""):
            if isinstance(struct, dict):
                for key, value in struct.items():
                    new_path = f"{path}/{key}" if path else key
                    flatten_structure(value, new_path)
            elif isinstance(struct, list):
                for item in struct:
                    flat_files.append(f"{path}/{item}" if path else item)
        
        flatten_structure(structure)
        
        # Analyze files
        for file_path in flat_files:
            lower_path = file_path.lower()
            
            if "package.json" in lower_path:
                has_node = True
            if "webpack" in lower_path:
                has_webpack = True
            if "react" in lower_path or "jsx" in lower_path:
                has_react = True
            if "vue" in lower_path:
                has_vue = True
            if "angular" in lower_path or "ng" in lower_path:
                has_angular = True
        
        return {
            "web_project": has_node or has_webpack or has_react or has_vue or has_angular,
            "has_node": has_node,
            "has_webpack": has_webpack,
            "has_react": has_react,
            "has_vue": has_vue,
            "has_angular": has_angular,
            "needs_node_tools": has_node,
            "needs_build_tools": has_webpack,
            "needs_component_tools": has_react or has_vue or has_angular
        }

    @staticmethod
    def recommend_features(project_path: str) -> Dict[str, Any]:
        """
        Analyze a project and recommend AI Dev Toolkit features.
        
        Args:
            project_path: Path to the project to analyze
            
        Returns:
            A dictionary of feature recommendations
        """
        project_path = os.path.abspath(project_path)
        
        # Get project structure
        structure = get_directory_structure(project_path)
        
        # Base analysis
        analysis = {
            "project_path": project_path,
            "has_ai_reference": os.path.exists(os.path.join(project_path, ".ai_reference")),
            "has_claude_md": os.path.exists(os.path.join(project_path, "CLAUDE.md")),
            "has_git": is_git_repository(project_path),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Language-specific analysis
        python_analysis = FeatureRecommender.analyze_python_project(structure)
        web_analysis = FeatureRecommender.analyze_web_project(structure)
        
        # Merge analyses
        analysis.update(python_analysis)
        analysis.update(web_analysis)
        
        # Add recommendation summary
        analysis["recommendations"] = {
            "initialize_ai_reference": not analysis["has_ai_reference"],
            "create_claude_md": not analysis["has_claude_md"],
            "setup_git_tracking": analysis["has_git"],
            "setup_test_tools": analysis.get("needs_test_tools", False),
            "setup_package_tools": analysis.get("needs_package_tools", False),
            "setup_web_tools": analysis.get("needs_web_tools", False),
            "setup_node_tools": analysis.get("needs_node_tools", False),
            "setup_build_tools": analysis.get("needs_build_tools", False),
            "setup_component_tools": analysis.get("needs_component_tools", False)
        }
        
        return analysis


class UpgradeManager:
    """Manages upgrades for AI Development Toolkit installations."""
    
    @staticmethod
    def get_installed_version(project_path: str) -> Optional[str]:
        """
        Get the currently installed version of AI Development Toolkit.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Version string or None if not found
        """
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        version_file = os.path.join(ai_ref_path, "version.json")
        
        if not os.path.exists(version_file):
            # Legacy version detection
            readme_path = os.path.join(ai_ref_path, "README.md")
            if os.path.exists(readme_path):
                with open(readme_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Look for version patterns
                    match = re.search(r'version\s+(\d+\.\d+\.\d+)', content, re.IGNORECASE)
                    if match:
                        return match.group(1)
            return None
            
        try:
            with open(version_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("version")
        except (json.JSONDecodeError, IOError):
            return None
    
    @staticmethod
    def needs_upgrade(project_path: str) -> Tuple[bool, str, str]:
        """
        Check if a project needs an upgrade.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Tuple of (needs_upgrade, current_version, latest_version)
        """
        installed_version = UpgradeManager.get_installed_version(project_path)
        
        # If not installed, definitely needs an upgrade
        if not installed_version:
            return True, "not installed", CURRENT_VERSION
            
        # Compare versions
        current = Version(installed_version)
        latest = Version(CURRENT_VERSION)
        
        return current < latest, str(current), str(latest)
    
    @staticmethod
    def backup_ai_reference(project_path: str) -> Optional[str]:
        """
        Create a backup of the .ai_reference directory.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Path to the backup directory or None if backup failed
        """
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        if not os.path.exists(ai_ref_path):
            return None
            
        # Create backup with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{ai_ref_path}_backup_{timestamp}"
        
        try:
            shutil.copytree(ai_ref_path, backup_path)
            logger.info(f"Created backup of .ai_reference at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
            
    @staticmethod
    def create_claude_md(project_path: str, reinit: bool = False) -> bool:
        """
        Create or update CLAUDE.md file with auto-initialization.
        
        Args:
            project_path: Path to the project
            reinit: Whether to reinitialize an existing file
            
        Returns:
            True if file was created or updated
        """
        claude_md_path = os.path.join(project_path, "CLAUDE.md")
        
        # Check if file already exists and we're not forcing reinit
        if os.path.exists(claude_md_path) and not reinit:
            return False
            
        # Basic CLAUDE.md template
        template = """# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

```python
# Automatically initialize AI Dev Toolkit on startup
import os
from aitoolkit.librarian.ai_dev_toolkit import initialize_ai_dev_toolkit

# Initialize the toolkit with the current project path
current_dir = os.path.dirname(os.path.abspath(__file__))
initialize_ai_dev_toolkit(current_dir)
```

## Project Overview

This project uses AI Dev Toolkit for enhanced code understanding and development tools.

## Key Commands

```bash
# Common commands for this project
# Add project-specific commands here
```

## Project Structure

<!-- Add a brief description of your project structure -->

"""
        # Write the file
        try:
            with open(claude_md_path, "w", encoding="utf-8") as f:
                f.write(template)
            logger.info(f"Created CLAUDE.md at {claude_md_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create CLAUDE.md: {e}")
            return False
    
    @staticmethod
    def update_version_info(project_path: str) -> bool:
        """
        Update the version information in .ai_reference.
        
        Args:
            project_path: Path to the project
            
        Returns:
            True if version was updated
        """
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        version_file = os.path.join(ai_ref_path, "version.json")
        
        data = {
            "version": CURRENT_VERSION,
            "upgraded_at": datetime.datetime.now().isoformat(),
            "toolkit_path": os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        }
        
        try:
            os.makedirs(os.path.dirname(version_file), exist_ok=True)
            with open(version_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Updated version info to {CURRENT_VERSION}")
            return True
        except Exception as e:
            logger.error(f"Failed to update version info: {e}")
            return False
            
    @staticmethod
    def setup_git_tracking(project_path: str) -> bool:
        """
        Set up git tracking for the project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            True if git tracking was set up
        """
        if not is_git_repository(project_path):
            logger.info(f"Project at {project_path} is not a git repository")
            return False
            
        try:
            # Get initial repository status to initialize tracking
            status = get_repository_status(project_path)
            
            # Create a git directory in .ai_reference if it doesn't exist
            ai_ref_path = os.path.join(project_path, ".ai_reference")
            git_dir = os.path.join(ai_ref_path, "git")
            os.makedirs(git_dir, exist_ok=True)
            
            # Save initial status
            status_file = os.path.join(git_dir, "status.json")
            with open(status_file, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=2)
                
            logger.info(f"Set up git tracking for {project_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to set up git tracking: {e}")
            return False
    
    @staticmethod
    def analyze_project(project_path: str) -> Dict[str, Any]:
        """
        Analyze a project without upgrading.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Analysis results
        """
        # Get upgrade status
        needs_upgrade, current_version, latest_version = UpgradeManager.needs_upgrade(project_path)
        
        # Get feature recommendations
        recommendations = FeatureRecommender.recommend_features(project_path)
        
        # Combine results
        results = {
            "needs_upgrade": needs_upgrade,
            "current_version": current_version,
            "latest_version": latest_version,
            "recommendations": recommendations
        }
        
        return results
        
    @staticmethod
    def upgrade(project_path: str, backup: bool = True, claude_md: bool = True, 
                git_tracking: bool = True, force: bool = False) -> Dict[str, Any]:
        """
        Upgrade the AI Development Toolkit installation for a project.
        
        Args:
            project_path: Path to the project
            backup: Whether to create a backup
            claude_md: Whether to create/update CLAUDE.md
            git_tracking: Whether to set up git tracking
            force: Whether to force upgrade even if not needed
            
        Returns:
            Results of the upgrade operation
        """
        project_path = os.path.abspath(project_path)
        results = {
            "project_path": project_path,
            "steps": {},
            "success": True
        }
        
        # Check if upgrade is needed
        needs_upgrade, current_version, latest_version = UpgradeManager.needs_upgrade(project_path)
        results["needs_upgrade"] = needs_upgrade
        results["current_version"] = current_version
        results["latest_version"] = latest_version
        
        if not needs_upgrade and not force:
            logger.info(f"Project at {project_path} already has latest version {latest_version}")
            results["message"] = f"Already at latest version {latest_version}"
            return results
            
        # Create backup if requested
        if backup:
            backup_path = UpgradeManager.backup_ai_reference(project_path)
            results["steps"]["backup"] = {
                "success": backup_path is not None,
                "backup_path": backup_path
            }
        
        # Initialize or upgrade AI reference
        try:
            logger.info(f"Initializing AI reference for {project_path}")
            initialize_ai_dev_toolkit(project_path)
            results["steps"]["initialize"] = {"success": True}
        except Exception as e:
            logger.error(f"Failed to initialize AI reference: {e}")
            results["steps"]["initialize"] = {"success": False, "error": str(e)}
            results["success"] = False
            return results
            
        # Update version info
        version_updated = UpgradeManager.update_version_info(project_path)
        results["steps"]["version_update"] = {"success": version_updated}
        
        # Create CLAUDE.md if requested
        if claude_md:
            claude_created = UpgradeManager.create_claude_md(project_path)
            results["steps"]["claude_md"] = {"success": claude_created}
            
        # Set up git tracking if requested
        if git_tracking:
            git_setup = UpgradeManager.setup_git_tracking(project_path)
            results["steps"]["git_tracking"] = {"success": git_setup}
            
        # Overall success depends on version update
        if not version_updated:
            results["success"] = False
            results["message"] = "Failed to update version info"
        else:
            results["message"] = f"Successfully upgraded from {current_version} to {latest_version}"
            
        return results


def main():
    """
    Main function for command-line usage.
    """
    parser = argparse.ArgumentParser(description="AI Development Toolkit Upgrade Manager")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a project without upgrading")
    analyze_parser.add_argument("project_path", help="Path to the project to analyze")
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade a project")
    upgrade_parser.add_argument("project_path", help="Path to the project to upgrade")
    upgrade_parser.add_argument("--no-backup", action="store_true", help="Skip creating a backup")
    upgrade_parser.add_argument("--no-claude-md", action="store_true", help="Skip creating CLAUDE.md")
    upgrade_parser.add_argument("--no-git-tracking", action="store_true", help="Skip setting up git tracking")
    upgrade_parser.add_argument("--force", action="store_true", help="Force upgrade even if not needed")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == "analyze":
        results = UpgradeManager.analyze_project(args.project_path)
        print(json.dumps(results, indent=2))
    elif args.command == "upgrade":
        results = UpgradeManager.upgrade(
            args.project_path, 
            backup=not args.no_backup,
            claude_md=not args.no_claude_md,
            git_tracking=not args.no_git_tracking,
            force=args.force
        )
        print(json.dumps(results, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()