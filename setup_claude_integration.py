#!/usr/bin/env python3
"""
Quick setup script for Claude Code integration
"""

import os
import shutil

def setup_claude_code_integration(install_dir):
    """Set up integration with Claude Code."""
    try:
        # Create CLAUDE.md file if it doesn't exist
        claude_md_path = os.path.join(install_dir, "CLAUDE.md")
        if not os.path.exists(claude_md_path):
            docs_reference = os.path.join(install_dir, "docs", "claude_code_reference.md")
            if os.path.exists(docs_reference):
                # Read the content
                with open(docs_reference, 'r') as f:
                    content = f.read()
                
                # Add auto-initialization code at the top
                auto_init_code = """```python
# Automatically initialize AI Dev Toolkit on startup
import os
from aitoolkit.librarian.ai_dev_toolkit import initialize_ai_dev_toolkit

# Initialize the toolkit with the current project path
current_dir = os.path.dirname(os.path.abspath(__file__))
initialize_ai_dev_toolkit(current_dir)
```

"""
                # Find where to insert the code (after the initial header)
                header_end = content.find("\n\n")
                if header_end != -1:
                    modified_content = content[:header_end+2] + auto_init_code + content[header_end+2:]
                else:
                    modified_content = content + "\n\n" + auto_init_code
                
                # Write the modified content
                with open(claude_md_path, 'w') as f:
                    f.write(modified_content)
                
                print("✅ Created CLAUDE.md with auto-initialization for Claude Code")
            else:
                print(f"❌ Reference file not found: {docs_reference}")
                return False
        else:
            # Add initialization code to existing CLAUDE.md if not already there
            with open(claude_md_path, 'r') as f:
                content = f.read()
            
            if "initialize_ai_dev_toolkit" not in content:
                auto_init_code = """```python
# Automatically initialize AI Dev Toolkit on startup
import os
from aitoolkit.librarian.ai_dev_toolkit import initialize_ai_dev_toolkit

# Initialize the toolkit with the current project path
current_dir = os.path.dirname(os.path.abspath(__file__))
initialize_ai_dev_toolkit(current_dir)
```

"""
                # Find where to insert the code (after the initial header)
                header_end = content.find("\n\n")
                if header_end != -1:
                    modified_content = content[:header_end+2] + auto_init_code + content[header_end+2:]
                else:
                    modified_content = content + "\n\n" + auto_init_code
                
                # Write the modified content
                with open(claude_md_path, 'w') as f:
                    f.write(modified_content)
                
                print("✅ Added auto-initialization to existing CLAUDE.md")
            else:
                print("✅ CLAUDE.md already contains auto-initialization code")
        
        # Make sure .ai_reference directory exists
        ai_ref_dir = os.path.join(install_dir, ".ai_reference")
        if not os.path.exists(ai_ref_dir):
            os.makedirs(ai_ref_dir)
            print(f"✅ Created .ai_reference directory")
        else:
            print(f"✅ .ai_reference directory already exists")
        
        # Add CLAUDE.md to .gitignore
        gitignore_path = os.path.join(install_dir, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                gitignore_content = f.read()
            
            if "CLAUDE.md" not in gitignore_content:
                with open(gitignore_path, "a") as f:
                    f.write("\n# Claude Code integration\nCLAUDE.md\n")
                print("✅ Added CLAUDE.md to .gitignore")
        
        print("\n✅ Claude Code integration setup complete!")
        return True
    except Exception as e:
        print(f"❌ Error setting up Claude Code integration: {str(e)}")
        return False

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    setup_claude_code_integration(current_dir)