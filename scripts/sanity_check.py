#!/usr/bin/env python3
"""
AI Dev Toolkit Sanity Checker

This tool performs basic sanity checks on the AI Dev Toolkit codebase to identify
potential issues, inconsistencies, and path problems.
"""

import os
import sys
import json
import re
import importlib
import importlib.util
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# ANSI color codes for prettier output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

class SanityChecker:
    """
    Checks the AI Dev Toolkit codebase for common issues.
    """
    
    def __init__(self, root_dir: str):
        """
        Initialize the SanityChecker.
        
        Args:
            root_dir: Root directory of the project
        """
        self.root_dir = os.path.abspath(root_dir)
        self.issues = []
        self.warnings = []
        self.info = []
        
        self.exclude_dirs = [
            ".git", 
            "__pycache__", 
            "venv", 
            ".venv", 
            "env", 
            "node_modules",
            ".ai_reference"  # Exclude generated files
        ]
        
        # We need to check these paths specifically
        self.critical_paths = [
            os.path.join("aitoolkit", "librarian", "server.py"),
            os.path.join("aitoolkit", "librarian", "indexer.py"),
            os.path.join("aitoolkit", "librarian", "enhanced_indexer.py")
        ]
    
    def print_status(self, message: str, status: str = "info"):
        """Print a status message with appropriate formatting."""
        prefix = ""
        if status == "success":
            prefix = f"{GREEN}✓ "
        elif status == "warning":
            prefix = f"{YELLOW}⚠ "
        elif status == "error":
            prefix = f"{RED}✗ "
        elif status == "info":
            prefix = f"{BLUE}ℹ "
        
        print(f"{prefix}{message}{RESET}")
    
    def check_all(self) -> Tuple[int, int, int]:
        """
        Run all checks and return counts of issues, warnings, and info messages.
        
        Returns:
            Tuple containing counts of (issues, warnings, info messages)
        """
        self.print_status(f"{BOLD}Running sanity checks on {self.root_dir}{RESET}", "info")
        print()
        
        # File existence checks
        self.check_critical_paths()
        
        # Python static checks
        self.check_imports()
        self.check_path_references()
        self.check_deprecated_functions()
        
        # Project structure checks
        self.check_for_duplicate_functionality()
        self.check_for_misplaced_files()
        
        # Run external tools (if available)
        self.try_run_pylint()
        
        return len(self.issues), len(self.warnings), len(self.info)
    
    def check_critical_paths(self):
        """
        Check that critical files exist.
        """
        self.print_status("Checking for critical files...", "info")
        
        for path in self.critical_paths:
            full_path = os.path.join(self.root_dir, path)
            if os.path.exists(full_path):
                self.print_status(f"Found {path}", "success")
                self.info.append(f"Critical file {path} exists")
            else:
                self.print_status(f"Missing critical file: {path}", "error")
                self.issues.append(f"Critical file missing: {path}")
        
        print()
    
    def check_imports(self):
        """
        Check for import errors in Python files.
        """
        self.print_status("Checking Python imports...", "info")
        
        python_files = self._get_python_files()
        for file_path in python_files:
            rel_path = os.path.relpath(file_path, self.root_dir)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract imports
                import_lines = []
                for line in content.split('\n'):
                    if line.startswith('import ') or line.startswith('from '):
                        # Skip comments
                        if '#' in line:
                            line = line[:line.index('#')]
                        
                        # Basic cleanup
                        line = line.strip()
                        if line:
                            import_lines.append(line)
                
                # Basic syntax check for each import
                for import_line in import_lines:
                    try:
                        # This is a basic syntax check, not a full import test
                        compile(import_line, '<string>', 'exec')
                    except SyntaxError as e:
                        self.print_status(f"Syntax error in import in {rel_path}: {import_line}", "error")
                        self.issues.append(f"Import syntax error in {rel_path}: {import_line}")
                        continue
                    
                    # Check for common relative import issues
                    if 'from .' in import_line and 'librarian' in file_path:
                        if '..' in import_line:
                            # This is often an issue in subdirectory imports
                            self.print_status(f"Potentially problematic parent-level relative import in {rel_path}: {import_line}", "warning")
                            self.warnings.append(f"Suspicious relative import in {rel_path}: {import_line}")
            
            except Exception as e:
                self.print_status(f"Error checking imports in {rel_path}: {e}", "error")
                self.issues.append(f"Import check error in {rel_path}: {e}")
        
        print()
    
    def check_path_references(self):
        """
        Check for hardcoded paths that might be incorrect.
        """
        self.print_status("Checking for path references...", "info")
        
        bad_paths = [
            r'[\"\']src[/\\]', 
            r'[\"\']\.\.\/src',
            r'src\/.*?\.py',
            r'[\"\']src.librarian',
            r'ai_librarian_server\.py',
            r'\/src\/mcp\/',
            r'join\([^\)]*[\'"]src[\'"]\)',
        ]
        
        path_pattern = re.compile('|'.join(bad_paths))
        
        python_files = self._get_python_files()
        for file_path in python_files:
            rel_path = os.path.relpath(file_path, self.root_dir)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for the suspicious paths
                matches = path_pattern.findall(content)
                if matches:
                    for match in matches:
                        if 'src' in match.lower():
                            self.print_status(f"Possibly incorrect path reference in {rel_path}: {match}", "warning")
                            self.warnings.append(f"Suspicious path reference in {rel_path}: {match}")
            
            except Exception as e:
                self.print_status(f"Error checking paths in {rel_path}: {e}", "error")
                self.issues.append(f"Path check error in {rel_path}: {e}")
        
        print()
    
    def check_deprecated_functions(self):
        """
        Check for deprecated function calls.
        """
        self.print_status("Checking for deprecated function calls...", "info")
        
        deprecated_functions = [
            r'initialize_librarian\(',
            r'indexer\.initialize_librarian\(',
            r'from\s+indexer\s+import',
            r'import\s+indexer'
        ]
        
        pattern = re.compile('|'.join(deprecated_functions))
        
        python_files = self._get_python_files()
        for file_path in python_files:
            # Skip the indexer.py file itself
            if file_path.endswith('indexer.py'):
                continue
                
            rel_path = os.path.relpath(file_path, self.root_dir)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for deprecated function calls
                matches = pattern.findall(content)
                if matches:
                    for match in matches:
                        self.print_status(f"Deprecated indexer reference in {rel_path}: {match}", "warning")
                        self.warnings.append(f"Deprecated function reference in {rel_path}: {match}")
            
            except Exception as e:
                self.print_status(f"Error checking deprecated functions in {rel_path}: {e}", "error")
                self.issues.append(f"Deprecated function check error in {rel_path}: {e}")
        
        print()
    
    def check_for_duplicate_functionality(self):
        """
        Check for duplicate functionality across different modules.
        """
        self.print_status("Checking for duplicate functionality...", "info")
        
        # Specific check for indexer duplication
        indexer_path = os.path.join(self.root_dir, "aitoolkit", "librarian", "indexer.py")
        enhanced_path = os.path.join(self.root_dir, "aitoolkit", "librarian", "enhanced_indexer.py")
        
        if os.path.exists(indexer_path) and os.path.exists(enhanced_path):
            with open(indexer_path, 'r', encoding='utf-8') as f:
                indexer_content = f.read()
            
            if 'DEPRECATED' in indexer_content and 'enhanced_indexer' in indexer_content:
                self.print_status("Basic indexer.py correctly redirects to enhanced_indexer.py", "success")
                self.info.append("indexer.py correctly uses enhanced_indexer.py")
            else:
                self.print_status("indexer.py and enhanced_indexer.py contain duplicate functionality", "warning")
                self.warnings.append("Duplicate functionality in indexer modules")
        
        print()
    
    def check_for_misplaced_files(self):
        """
        Check for files that appear to be in the wrong location.
        """
        self.print_status("Checking for misplaced files...", "info")
        
        # Look for Python files in the src directory (which seems to be outdated)
        src_dir = os.path.join(self.root_dir, "src")
        if os.path.exists(src_dir):
            src_files = []
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    if file.endswith('.py'):
                        src_files.append(os.path.join(root, file))
            
            if src_files:
                self.print_status(f"Found {len(src_files)} Python files in the src directory, but code should be in aitoolkit", "warning")
                for file in src_files:
                    rel_path = os.path.relpath(file, self.root_dir)
                    self.warnings.append(f"Possibly misplaced file: {rel_path}")
                    self.print_status(f"  - {rel_path}", "warning")
        
        print()
    
    def try_run_pylint(self):
        """
        Attempt to run pylint on key modules if it's installed.
        """
        self.print_status("Trying to run pylint...", "info")
        
        try:
            # Check if pylint is installed
            result = subprocess.run(
                ["pylint", "--version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                self.print_status("pylint not available - skipping linting checks", "info")
                return
            
            # Check AI Librarian module
            librarian_dir = os.path.join(self.root_dir, "aitoolkit", "librarian")
            if os.path.exists(librarian_dir):
                self.print_status(f"Running pylint on librarian module...", "info")
                
                result = subprocess.run(
                    ["pylint", librarian_dir, "--disable=all", "--enable=import-error,undefined-variable"],
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0:
                    self.print_status("No critical pylint issues found", "success")
                else:
                    self.print_status("pylint found some issues:", "warning")
                    for line in result.stdout.splitlines():
                        if line.strip():
                            self.print_status(f"  {line}", "warning")
                            self.warnings.append(f"Pylint issue: {line}")
        
        except FileNotFoundError:
            self.print_status("pylint not installed - skipping linting checks", "info")
        except Exception as e:
            self.print_status(f"Error running pylint: {e}", "error")
            self.issues.append(f"Pylint error: {e}")
        
        print()
    
    def _get_python_files(self) -> List[str]:
        """
        Get all Python files in the project.
        
        Returns:
            List of absolute paths to Python files
        """
        python_files = []
        
        for root, dirs, files in os.walk(self.root_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files

def main():
    """Main entry point for the sanity checker."""
    # Parse arguments
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    checker = SanityChecker(root_dir)
    issues, warnings, info = checker.check_all()
    
    # Print summary
    print(f"\n{BOLD}Sanity Check Summary:{RESET}")
    print(f"{RED}{issues} issues{RESET}, {YELLOW}{warnings} warnings{RESET}, {BLUE}{info} info messages{RESET}")
    
    if issues > 0:
        print(f"\n{RED}❌ Sanity check failed with {issues} issues{RESET}")
        return 1
    elif warnings > 0:
        print(f"\n{YELLOW}⚠️ Sanity check passed with {warnings} warnings{RESET}")
        return 0
    else:
        print(f"\n{GREEN}✅ Sanity check passed successfully!{RESET}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
