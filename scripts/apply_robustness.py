#!/usr/bin/env python3
"""
Apply Robustness Features

This script applies robustness features to an existing MCP server installation.
It targets long-running operations like search and initialization functions,
making them more resilient against timeouts and failures.

Usage:
    python apply_robustness.py [--server-path PATH] [--timeout SECONDS] [--retries COUNT]
"""

import os
import sys
import argparse
import importlib
import inspect
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("apply-robustness")

def find_server_modules(server_path):
    """Find all Python modules in the server path."""
    modules = []
    for root, dirs, files in os.walk(server_path):
        # Skip __pycache__ and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                # Get the relative path to create a module name
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, server_path)
                # Convert path to module name
                module_name = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
                modules.append((module_name, file_path))
    
    return modules

def apply_robustness_to_module(module_name, file_path):
    """Apply robustness features to a module."""
    try:
        # Try to import the module
        if module_name not in sys.modules:
            module_spec = importlib.util.spec_from_file_location(module_name, file_path)
            if module_spec is None:
                logger.warning(f"Could not create module spec for {module_name} at {file_path}")
                return False
                
            module = importlib.util.module_from_spec(module_spec)
            sys.modules[module_name] = module
            module_spec.loader.exec_module(module)
        else:
            module = sys.modules[module_name]
        
        # Import the tool wrapper utilities
        try:
            from aitoolkit.utils.tool_wrappers import wrap_all_search_tools
            # Apply robustness to all search-related functions
            wrap_all_search_tools(module)
            return True
        except ImportError:
            logger.error("Could not import tool_wrappers module. Make sure you're running from the correct directory.")
            return False
            
    except Exception as e:
        logger.error(f"Error applying robustness to module {module_name}: {str(e)}")
        return False

def patch_mcp_server_file(file_path, timeout=60.0, retries=2):
    """
    Patch an MCP server file to add robustness features.
    This modifies the file directly.
    
    Args:
        file_path: Path to the MCP server file
        timeout: Default timeout for operations in seconds
        retries: Default number of retries for operations
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the server class definition
        if 'class' in content and 'server' in content.lower():
            # Add imports for robustness features
            import_section = "import os\nimport sys\n"
            robustness_import = "\n# Import robustness features\ntry:\n    from aitoolkit.utils.tool_wrappers import patch_mcp_server, apply_robustness\nexcept ImportError:\n    pass\n"
            
            if import_section in content and robustness_import not in content:
                # Add robustness imports after the regular imports
                content = content.replace(import_section, import_section + robustness_import)
            
            # Look for server initialization
            if "def __init__" in content:
                # Find where to add the patching code
                init_sections = content.split("def __init__")
                if len(init_sections) > 1:
                    # Find the end of the __init__ method
                    init_method = init_sections[1]
                    method_lines = init_method.split('\n')
                    
                    # Find the indentation level
                    indentation = ""
                    for line in method_lines:
                        if line.strip():
                            indentation = line[:len(line) - len(line.lstrip())]
                            break
                    
                    # Add patching code at the end of __init__
                    patching_code = f"\n{indentation}# Apply robustness features\n{indentation}try:\n{indentation}    # Patch the server with robustness features\n{indentation}    if 'patch_mcp_server' in globals():\n{indentation}        patch_mcp_server(self)\n{indentation}        logger.info(\"Applied robustness features to MCP server\")\n{indentation}except Exception as e:\n{indentation}    logger.warning(f\"Could not apply robustness features: {{str(e)}}\")\n"
                    
                    # Find where to insert the patching code
                    for i, line in enumerate(method_lines):
                        if "register_" in line or "self.run" in line or i == len(method_lines) - 1:
                            # Insert before this line
                            method_lines.insert(i, patching_code)
                            break
                    
                    # Reconstruct the method
                    new_init_method = "\n".join(method_lines)
                    content = content.replace(init_method, new_init_method)
            
            # Write the modified content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"Successfully patched MCP server file: {file_path}")
            return True
        
        logger.warning(f"No server class found in {file_path}")
        return False
        
    except Exception as e:
        logger.error(f"Error patching MCP server file {file_path}: {str(e)}")
        return False

def main():
    """Main function to apply robustness features to an MCP server."""
    parser = argparse.ArgumentParser(description="Apply robustness features to MCP server")
    parser.add_argument(
        "--server-path", 
        type=str, 
        default=".",
        help="Path to the MCP server directory (default: current directory)"
    )
    parser.add_argument(
        "--timeout", 
        type=float, 
        default=60.0,
        help="Default timeout for operations in seconds (default: 60.0)"
    )
    parser.add_argument(
        "--retries", 
        type=int, 
        default=2,
        help="Default number of retries for operations (default: 2)"
    )
    
    args = parser.parse_args()
    server_path = os.path.abspath(args.server_path)
    
    # Print banner
    print("\n" + "=" * 80)
    print("              Applying Robustness Features to MCP Server")
    print("=" * 80)
    print(f"Server path: {server_path}")
    print(f"Default timeout: {args.timeout} seconds")
    print(f"Default retries: {args.retries}")
    print("")
    
    # Check if the server path exists
    if not os.path.exists(server_path):
        print(f"Error: Server path does not exist: {server_path}")
        return 1
    
    # Find server files
    server_files = []
    for root, dirs, files in os.walk(server_path):
        for file in files:
            if file.endswith('.py') and ('server' in file.lower() or 'mcp' in file.lower()):
                server_files.append(os.path.join(root, file))
    
    if not server_files:
        print(f"Error: No server files found in {server_path}")
        return 1
    
    # Patch server files
    patched_files = []
    for file_path in server_files:
        print(f"Analyzing {file_path}...")
        if patch_mcp_server_file(file_path, args.timeout, args.retries):
            patched_files.append(file_path)
    
    # Find and apply robustness to modules
    modules = find_server_modules(server_path)
    for module_name, file_path in modules:
        if 'search' in module_name.lower() or 'query' in module_name.lower() or 'init' in module_name.lower():
            print(f"Applying robustness to module {module_name}...")
            apply_robustness_to_module(module_name, file_path)
    
    # Print results
    print("\nResults:")
    print(f"- Patched {len(patched_files)} server files")
    for file_path in patched_files:
        print(f"  - {os.path.relpath(file_path, server_path)}")
    
    print("\nNext steps:")
    print("1. Restart the MCP server to apply the changes")
    print("2. Monitor server logs for timeout errors")
    print("3. Adjust timeout and retry settings if needed")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
