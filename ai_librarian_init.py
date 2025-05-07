#!/usr/bin/env python3
"""
AI Librarian Initialization Script

This script properly initializes the AI Librarian for a given project directory.
It ensures proper path resolution and handles import errors gracefully.
"""

import os
import sys
import argparse
from pathlib import Path

def main():
    """Main entry point for AI Librarian initialization"""
    parser = argparse.ArgumentParser(description="Initialize AI Librarian for a project")
    parser.add_argument("project_path", nargs="?", help="Path to the project directory")
    parser.add_argument("--generate", action="store_true", help="Regenerate librarian even if already initialized")
    args = parser.parse_args()

    # Get project path from args or use current directory
    project_path = args.project_path or os.getcwd()
    project_path = os.path.abspath(project_path)
    
    print(f"Initializing AI Librarian for: {project_path}")
    
    # Add the src directory to Python path to resolve imports
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(script_dir, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    try:
        # Now import the librarian functions with proper path resolution
        from librarian.core import initialize_librarian_tool, generate_librarian
        
        # Initialize or regenerate
        if args.generate:
            print("Generating AI Librarian...")
            result = generate_librarian(project_path)
            print(f"AI Librarian generated successfully:")
            print(result)
        else:
            print("Initializing AI Librarian...")
            result = initialize_librarian_tool(project_path)
            print(f"AI Librarian initialized successfully:")
            print(result)
        
        return 0
    except ImportError as e:
        print(f"Error importing required modules: {str(e)}")
        print(f"Python path: {sys.path}")
        return 1
    except Exception as e:
        print(f"Error initializing AI Librarian: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
