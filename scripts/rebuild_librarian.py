#!/usr/bin/env python3
"""
Script to rebuild the AI Librarian for the ai-dev-toolkit project.

This script uses the enhanced_librarian_updater to rebuild the .ai_reference directory
with comprehensive code context.
"""

import os
import sys
from pathlib import Path

# Get project path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_path = current_dir  # The script is in the project root

# Add the librarian directory to the path
librarian_dir = os.path.join(project_path, "src", "librarian")
sys.path.append(librarian_dir)

# Import the updater
from enhanced_librarian_updater import update_project_librarian

# Run the updater
print(f"Rebuilding AI Librarian for {project_path}...")
success, message = update_project_librarian(project_path)

# Print the result
print(f"Success: {success}")
print(f"Message: {message}")

# If successful, check what was created
if success:
    ai_ref_path = os.path.join(project_path, ".ai_reference")
    
    print("\nCreated files:")
    for root, dirs, files in os.walk(ai_ref_path):
        for file in files:
            print(f"- {os.path.relpath(os.path.join(root, file), project_path)}")
