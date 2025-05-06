#!/usr/bin/env python3
"""
Enhanced AI Librarian Updater

This script updates the AI Librarian with enhanced capabilities for more comprehensive
code understanding and context generation, similar to the machine learning optimizer's
implementation.

Usage:
    python enhanced_librarian_updater.py <project_path>
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import the enhanced indexer
try:
    from .enhanced_indexer import initialize_enhanced_librarian
except ImportError:
    # Adjust path if running as standalone script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.append(script_dir)
    from enhanced_indexer import initialize_enhanced_librarian

def update_project_librarian(project_path: str) -> Tuple[bool, str]:
    """
    Update a project's AI Librarian with enhanced capabilities.
    
    Args:
        project_path: Path to the project root
        
    Returns:
        Tuple containing (success flag, message)
    """
    try:
        # Validate project path
        if not os.path.exists(project_path):
            return False, f"Project path does not exist: {project_path}"
        
        project_path = os.path.abspath(project_path)
        
        # Check if .ai_reference exists
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        if not os.path.exists(ai_ref_path):
            # Create it first
            os.makedirs(ai_ref_path, exist_ok=True)
            
        # Backup existing files if they exist
        backup_dir = os.path.join(ai_ref_path, "backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        
        component_registry_path = os.path.join(ai_ref_path, "component_registry.json")
        script_index_path = os.path.join(ai_ref_path, "script_index.json")
        
        if os.path.exists(component_registry_path) or os.path.exists(script_index_path):
            os.makedirs(backup_dir, exist_ok=True)
            
            if os.path.exists(component_registry_path):
                shutil.copy2(component_registry_path, os.path.join(backup_dir, "component_registry.json"))
                
            if os.path.exists(script_index_path):
                shutil.copy2(script_index_path, os.path.join(backup_dir, "script_index.json"))
                
            # Backup diagnostics if they exist
            diagnostics_dir = os.path.join(ai_ref_path, "diagnostics")
            if os.path.exists(diagnostics_dir):
                backup_diagnostics = os.path.join(backup_dir, "diagnostics")
                os.makedirs(backup_diagnostics, exist_ok=True)
                
                for file in os.listdir(diagnostics_dir):
                    src_file = os.path.join(diagnostics_dir, file)
                    if os.path.isfile(src_file):
                        shutil.copy2(src_file, os.path.join(backup_diagnostics, file))
        
        # Generate enhanced librarian
        print(f"Generating enhanced AI Librarian for {project_path}...")
        message, file_count, component_count = initialize_enhanced_librarian(project_path)
        
        # Create an update log
        update_log_path = os.path.join(ai_ref_path, "update_log.md")
        
        with open(update_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n## Enhanced Librarian Update - {datetime.now().isoformat()}\n\n")
            f.write(f"- {message}\n")
            f.write(f"- Indexed {file_count} files\n")
            f.write(f"- Identified {component_count} components\n")
            if os.path.exists(backup_dir):
                f.write(f"- Created backup at {os.path.basename(backup_dir)}\n")
        
        return True, f"Successfully updated AI Librarian for {project_path}. Found {component_count} components in {file_count} files."
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        return False, f"Error updating AI Librarian: {str(e)}\n\n{error_details}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        success, message = update_project_librarian(project_path)
        
        if success:
            print(f"✅ {message}")
            sys.exit(0)
        else:
            print(f"❌ {message}")
            sys.exit(1)
    else:
        print("Usage: python enhanced_librarian_updater.py <project_path>")
        sys.exit(1)
