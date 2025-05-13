#!/usr/bin/env python3
"""
Fix the sanity_check.py file encoding issue.
"""

import os
import sys

def fix_sanity_check():
    """Fix the encoding issue in sanity_check.py"""
    # Path to sanity_check.py
    sanity_check_path = os.path.join("aitoolkit", "librarian", "sanity_check.py")
    
    try:
        # Read the file
        with open(sanity_check_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the problematic character with a regular ASCII character
        content = content.replace("\u221a", "v")  # Replace with ASCII "v"
        
        # Write back to the file
        with open(sanity_check_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Successfully fixed encoding issue in {sanity_check_path}")
        return True
    except Exception as e:
        print(f"Error fixing sanity_check.py: {e}")
        return False

if __name__ == "__main__":
    fix_sanity_check()
