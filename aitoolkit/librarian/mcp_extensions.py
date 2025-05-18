"""
MCP Extensions for AI Librarian - Prompts and Resources

This module shows how to add prompts and resources to the AI Librarian MCP server.
"""

from typing import Dict, Any, List
import os
import json
import logging

def register_prompts(mcp):
    """Register pre-defined prompts for common AI Librarian tasks."""
    
    @mcp.prompt("analyze-codebase")
    def analyze_codebase_prompt() -> str:
        """Prompt to analyze a codebase structure."""
        return """Please analyze the codebase in this project directory and provide:
1. An overview of the project structure
2. Main components and their relationships  
3. Key files and their purposes
4. Any architectural patterns detected
5. Suggestions for improvements

Use the AI Librarian tools to explore the codebase thoroughly."""

    @mcp.prompt("debug-issue")
    def debug_issue_prompt() -> str:
        """Prompt to help debug an issue."""
        return """I'm experiencing an issue with my code. Please help me debug it:

Issue Description: [User will describe the issue]

Please:
1. Use the AI Librarian to find relevant code
2. Analyze potential causes
3. Suggest debugging steps
4. Provide potential solutions
5. Help implement the fix"""

    @mcp.prompt("refactor-code")
    def refactor_code_prompt() -> str:
        """Prompt for code refactoring assistance."""
        return """I need help refactoring some code. Please:

1. Analyze the current implementation
2. Identify code smells or improvements
3. Suggest refactoring strategies
4. Help implement the changes safely
5. Ensure tests still pass

Target: [User will specify what to refactor]"""

    @mcp.prompt("add-feature")
    def add_feature_prompt() -> str:
        """Prompt for adding new features."""
        return """I want to add a new feature to my project:

Feature: [User will describe the feature]

Please:
1. Analyze where this feature should be implemented
2. Check for existing similar functionality
3. Design the implementation approach
4. Help implement the feature
5. Add appropriate tests and documentation"""

def register_resources(mcp):
    """Register resources for the AI Librarian."""
    
    @mcp.resource("librarian://projects/*")
    def project_resource(uri: str) -> Dict[str, Any]:
        """Provide project information as a resource."""
        project_path = uri.replace("librarian://projects/", "")
        
        # Check if project exists in librarian context
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        if not os.path.exists(ai_ref_path):
            return {
                "uri": uri,
                "name": f"Project: {os.path.basename(project_path)}",
                "description": "Project not initialized with AI Librarian",
                "mimeType": "text/plain",
                "content": "This project has not been initialized with the AI Librarian yet."
            }
        
        # Load project metadata
        metadata = {}
        component_registry_path = os.path.join(ai_ref_path, "component_registry.json")
        if os.path.exists(component_registry_path):
            with open(component_registry_path, 'r') as f:
                metadata['components'] = json.load(f)
        
        script_index_path = os.path.join(ai_ref_path, "script_index.json")
        if os.path.exists(script_index_path):
            with open(script_index_path, 'r') as f:
                metadata['scripts'] = json.load(f)
        
        return {
            "uri": uri,
            "name": f"Project: {os.path.basename(project_path)}",
            "description": f"AI Librarian metadata for {project_path}",
            "mimeType": "application/json",
            "content": json.dumps(metadata, indent=2)
        }
    
    @mcp.resource("librarian://bookmarks/*")
    def bookmark_resource(uri: str) -> Dict[str, Any]:
        """Provide bookmark information as a resource."""
        parts = uri.replace("librarian://bookmarks/", "").split("/")
        if len(parts) < 2:
            return {
                "uri": uri,
                "name": "Invalid bookmark URI",
                "description": "Bookmark URI must include project path and bookmark ID",
                "mimeType": "text/plain",
                "content": "Invalid URI format"
            }
        
        project_path = parts[0]
        bookmark_id = parts[1]
        
        # Load bookmark data
        bookmark_path = os.path.join(project_path, ".ai_reference", "edit_bookmarks", f"{bookmark_id}.json")
        if not os.path.exists(bookmark_path):
            return {
                "uri": uri,
                "name": f"Bookmark {bookmark_id}",
                "description": "Bookmark not found",
                "mimeType": "text/plain",
                "content": "This bookmark does not exist"
            }
        
        with open(bookmark_path, 'r') as f:
            bookmark_data = json.load(f)
        
        return {
            "uri": uri,
            "name": bookmark_data.get("name", f"Bookmark {bookmark_id}"),
            "description": f"Edit bookmark for {bookmark_data['file_path']}",
            "mimeType": "application/json",
            "content": json.dumps(bookmark_data, indent=2)
        }
    
    @mcp.resource("librarian://diagnostics/*")
    def diagnostics_resource(uri: str) -> Dict[str, Any]:
        """Provide diagnostic information as a resource."""
        project_path = uri.replace("librarian://diagnostics/", "")
        
        diagnostics_dir = os.path.join(project_path, ".ai_reference", "diagnostics")
        if not os.path.exists(diagnostics_dir):
            return {
                "uri": uri,
                "name": f"Diagnostics: {os.path.basename(project_path)}",
                "description": "No diagnostics available",
                "mimeType": "text/plain",
                "content": "No diagnostic information found for this project"
            }
        
        # Collect all diagnostic files
        diagnostics = {}
        for filename in os.listdir(diagnostics_dir):
            if filename.endswith('.json'):
                with open(os.path.join(diagnostics_dir, filename), 'r') as f:
                    diagnostics[filename] = json.load(f)
        
        return {
            "uri": uri,
            "name": f"Diagnostics: {os.path.basename(project_path)}",
            "description": f"Diagnostic information for {project_path}",
            "mimeType": "application/json",
            "content": json.dumps(diagnostics, indent=2)
        }

def register_mcp_extensions(mcp):
    """Register all MCP extensions (prompts and resources)."""
    register_prompts(mcp)
    register_resources(mcp)
    
    # Log what was registered
    logger = logging.getLogger('ai-librarian')
    logger.info(f"Registered {len(mcp.prompts)} prompts")
    logger.info(f"Registered {len(mcp.resources)} resource patterns")