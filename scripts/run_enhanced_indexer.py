
#!/usr/bin/env python3
"""
This script runs the enhanced AI Librarian indexer to rebuild
the .ai_reference directory for the ai-dev-toolkit project.
"""

import os
import sys
from pathlib import Path

# Get the current directory (should be the project root)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the librarian directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(current_dir), 'aitoolkit', 'librarian'))

# Import the enhanced indexer
try:
    from enhanced_indexer import initialize_enhanced_librarian
    
    # Run the enhanced indexer
    print(f"Initializing enhanced AI Librarian for {current_dir}")
    message, file_count, component_count = initialize_enhanced_librarian(current_dir)
    
    print(message)
    print(f"Found {component_count} components in {file_count} files")
    
    # Print the created directories
    ai_ref_dir = os.path.join(current_dir, '.ai_reference')
    if os.path.exists(ai_ref_dir):
        print("\nCreated directories:")
        for root, dirs, files in os.walk(ai_ref_dir):
            for dir in dirs:
                print(f"- {os.path.relpath(os.path.join(root, dir), current_dir)}")
                
        print("\nSample files created:")
        file_count = 0
        for root, dirs, files in os.walk(ai_ref_dir):
            for file in files:
                print(f"- {os.path.relpath(os.path.join(root, file), current_dir)}")
                file_count += 1
                if file_count >= 5:  # Just show a few sample files
                    print("... and more")
                    break
            if file_count >= 5:
                break
                
except ImportError as e:
    print(f"Error importing enhanced_indexer: {e}")
    print("Make sure the enhanced_indexer.py file exists in src/librarian/")
except Exception as e:
    import traceback
    print(f"Error running enhanced indexer: {e}")
    traceback.print_exc()
