#!/usr/bin/env python3
"""
Unified Context Integration Module

This module integrates the Unified Context Builder and Bidirectional Reference System
into the AI Librarian server and Tool Reference system.

Usage:
    # Will be automatically imported by the AI Librarian server
    from aitoolkit.librarian.unified_context_integration import register_unified_context_tools
    
    register_unified_context_tools(mcp)
"""

import os
import json
import logging
import threading
import time
from typing import Dict, List, Any, Optional

# Import the Unified Context Builder and Bidirectional Reference System
from aitoolkit.librarian.unified_context import UnifiedContextBuilder, build_unified_context
from aitoolkit.librarian.bidirectional_refs import BidirectionalReferenceSystem, build_bidirectional_references

# Configure logging
logger = logging.getLogger("unified-context-integration")

# Global context for unified context data
unified_context_data = {
    "context": {},
    "last_updated": 0,
    "active_projects": set(),
    "context_lock": threading.Lock(),
    "update_interval": 300  # Update every 5 minutes
}

def register_unified_context_tools(mcp):
    """
    Register the unified context tools with the MCP server.
    
    Args:
        mcp: The MCP server instance
    """
    # Register the tools
    @mcp.tool()
    def get_unified_context(project_path: str) -> Dict[str, Any]:
        """
        Get the unified context for a project, combining AI Librarian and Tool Reference data.
        
        This tool provides a consolidated view of both systems, making it easier to
        understand the relationships between components and tools.
        
        Args:
            project_path: The root directory of the project
            
        Returns:
            Dictionary containing the unified context
        """
        # Check for cached context first
        with unified_context_data["context_lock"]:
            if project_path in unified_context_data["context"]:
                # Check if cached context is still fresh
                context = unified_context_data["context"][project_path]
                current_time = time.time()
                last_update = unified_context_data["last_updated"]
                
                # If context is fresh enough, return it
                if current_time - last_update < unified_context_data["update_interval"]:
                    logger.info(f"Using cached unified context for {project_path}")
                    return context
        
        # Build a new context
        try:
            context = build_unified_context(project_path)
            
            # Cache the context
            with unified_context_data["context_lock"]:
                unified_context_data["context"][project_path] = context
                unified_context_data["last_updated"] = time.time()
                unified_context_data["active_projects"].add(project_path)
            
            logger.info(f"Built new unified context for {project_path}")
            return context
        except Exception as e:
            logger.error(f"Error building unified context: {str(e)}")
            return {
                "status": "error",
                "message": f"Error building unified context: {str(e)}"
            }
    
    @mcp.tool()
    def build_cross_references(project_path: str) -> Dict[str, Any]:
        """
        Build bidirectional cross-references between AI Librarian components and Tool Reference tools.
        
        This tool enhances both systems by creating explicit references between them,
        making it easier to navigate between components and the tools that work with them.
        
        Args:
            project_path: The root directory of the project
            
        Returns:
            Dictionary containing the results of the operation
        """
        try:
            # Check if required directories exist
            ai_ref_path = os.path.join(project_path, ".ai_reference")
            tool_ref_path = os.path.join(project_path, ".tool_reference")
            tool_profiles_path = os.path.join(tool_ref_path, "tool_profiles")
            
            if not os.path.exists(ai_ref_path):
                logger.error(f"AI Reference directory not found: {ai_ref_path}")
                return {
                    "status": "error",
                    "message": f"AI Reference directory not found: {ai_ref_path}"
                }
                
            if not os.path.exists(tool_ref_path):
                logger.error(f"Tool Reference directory not found: {tool_ref_path}")
                return {
                    "status": "error",
                    "message": f"Tool Reference directory not found: {tool_ref_path}"
                }
            
            if not os.path.exists(tool_profiles_path):
                logger.error(f"Tool Profiles directory not found: {tool_profiles_path}")
                return {
                    "status": "error",
                    "message": f"Tool Profiles directory not found: {tool_profiles_path}"
                }
            
            # Check if tool profiles exist
            profiles_count = len([f for f in os.listdir(tool_profiles_path) if f.endswith('.json')])
            if profiles_count == 0:
                logger.error(f"No tool profiles found in {tool_profiles_path}")
                return {
                    "status": "error",
                    "message": f"No tool profiles found in {tool_profiles_path}"
                }
            
            # Use the main build_bidirectional_references function from bidirectional_refs.py
            logger.info(f"Building bidirectional references for {project_path}")
            try:
                success = build_bidirectional_references(project_path)
                logger.info(f"build_bidirectional_references result: {success}")
            except Exception as ref_e:
                logger.error(f"Exception in build_bidirectional_references: {str(ref_e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                success = False
            
            if success:
                # Invalidate cached context to force rebuild with new references
                with unified_context_data["context_lock"]:
                    if project_path in unified_context_data["context"]:
                        del unified_context_data["context"][project_path]
                
                # Count references
                try:
                    brs = BidirectionalReferenceSystem(project_path)
                    brs.build_references()
                    
                    component_ref_count = sum(len(refs) for refs in brs.component_to_tool_refs.values())
                    tool_ref_count = sum(len(refs) for refs in brs.tool_to_component_refs.values())
                    
                    return {
                        "status": "success",
                        "message": "Successfully built bidirectional cross-references",
                        "component_to_tool_references": component_ref_count,
                        "tool_to_component_references": tool_ref_count,
                        "components_with_references": len(brs.component_to_tool_refs),
                        "tools_with_references": len(brs.tool_to_component_refs)
                    }
                except Exception as count_e:
                    logger.error(f"Error counting references: {str(count_e)}")
                    return {
                        "status": "partial_success",
                        "message": f"References built but error counting them: {str(count_e)}"
                    }
            else:
                logger.error("build_bidirectional_references returned False")
                return {
                    "status": "error",
                    "message": "Failed to build bidirectional cross-references"
                }
        except Exception as e:
            logger.error(f"Error building cross-references: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "status": "error",
                "message": f"Error building cross-references: {str(e)}"
            }
    
    @mcp.tool()
    def find_related_tools(project_path: str, component_name: str) -> Dict[str, Any]:
        """
        Find tools related to a specific component.
        
        This tool leverages the bidirectional references to quickly identify which
        tools are most relevant for working with a particular component.
        
        Args:
            project_path: The root directory of the project
            component_name: The name of the component to find related tools for
            
        Returns:
            Dictionary containing the related tools and their relevance
        """
        try:
            # Get or build the unified context
            context = get_unified_context(project_path)
            
            if "status" in context and context["status"] == "error":
                return context
            
            # Check if the component exists
            if component_name not in context.get("components", {}):
                return {
                    "status": "error",
                    "message": f"Component not found: {component_name}"
                }
            
            # Get direct references from cross-references
            direct_refs = []
            if component_name in context.get("cross_references", {}):
                direct_refs = context["cross_references"][component_name].get("related_tools", [])
            
            # If no direct references, try to infer them
            inferred_refs = []
            if not direct_refs:
                # Get all tools
                tools = context.get("tools", {})
                
                # Look for tools in the same category as the component
                component_info = context["components"][component_name]
                component_file = component_info.get("file", "")
                
                for tool_id, tool_info in tools.items():
                    tool_category = tool_info.get("category", "unknown")
                    
                    # Check if tool category is in the component's file path
                    if tool_category in component_file:
                        inferred_refs.append(tool_id)
                    
                    # Check if tool's name is related to component's name
                    if tool_id.lower() in component_name.lower() or component_name.lower() in tool_id.lower():
                        inferred_refs.append(tool_id)
            
            # Combine and deduplicate
            all_refs = direct_refs + [r for r in inferred_refs if r not in direct_refs]
            
            if not all_refs:
                return {
                    "status": "success",
                    "message": f"No tools found related to component: {component_name}",
                    "component": component_name,
                    "related_tools": []
                }
            
            # Get detailed information about each related tool
            related_tools = []
            for tool_id in all_refs:
                if tool_id in context.get("tools", {}):
                    tool_info = context["tools"][tool_id]
                    related_tools.append({
                        "id": tool_id,
                        "category": tool_info.get("category", "unknown"),
                        "primary_purpose": tool_info.get("primary_purpose", ""),
                        "reference_type": "direct" if tool_id in direct_refs else "inferred"
                    })
            
            return {
                "status": "success",
                "component": component_name,
                "related_tools": related_tools,
                "count": len(related_tools)
            }
        except Exception as e:
            logger.error(f"Error finding related tools: {str(e)}")
            return {
                "status": "error",
                "message": f"Error finding related tools: {str(e)}"
            }
    
    @mcp.tool()
    def find_related_components(project_path: str, tool_id: str) -> Dict[str, Any]:
        """
        Find components related to a specific tool.
        
        This tool leverages the bidirectional references to quickly identify which
        components are most relevant for a particular tool.
        
        Args:
            project_path: The root directory of the project
            tool_id: The ID of the tool to find related components for
            
        Returns:
            Dictionary containing the related components and their relevance
        """
        try:
            # Get or build the unified context
            context = get_unified_context(project_path)
            
            if "status" in context and context["status"] == "error":
                return context
            
            # Check if the tool exists
            if tool_id not in context.get("tools", {}):
                return {
                    "status": "error",
                    "message": f"Tool not found: {tool_id}"
                }
            
            # Get direct references from cross-references
            direct_refs = []
            if tool_id in context.get("cross_references", {}):
                direct_refs = context["cross_references"][tool_id].get("related_components", [])
            
            # If no direct references, try to infer them
            inferred_refs = []
            if not direct_refs:
                # Get all components
                components = context.get("components", {})
                
                # Look for components related to the tool
                tool_info = context["tools"][tool_id]
                tool_category = tool_info.get("category", "unknown")
                
                for component_name, component_info in components.items():
                    component_file = component_info.get("file", "")
                    
                    # Check if tool category is in the component's file path
                    if tool_category in component_file:
                        inferred_refs.append(component_name)
                    
                    # Check if component's name is related to tool's name
                    if tool_id.lower() in component_name.lower() or component_name.lower() in tool_id.lower():
                        inferred_refs.append(component_name)
            
            # Combine and deduplicate
            all_refs = direct_refs + [r for r in inferred_refs if r not in direct_refs]
            
            if not all_refs:
                return {
                    "status": "success",
                    "message": f"No components found related to tool: {tool_id}",
                    "tool": tool_id,
                    "related_components": []
                }
            
            # Get detailed information about each related component
            related_components = []
            for component_name in all_refs:
                if component_name in context.get("components", {}):
                    component_info = context["components"][component_name]
                    related_components.append({
                        "name": component_name,
                        "type": component_info.get("type", "unknown"),
                        "file": component_info.get("file", ""),
                        "reference_type": "direct" if component_name in direct_refs else "inferred"
                    })
            
            return {
                "status": "success",
                "tool": tool_id,
                "related_components": related_components,
                "count": len(related_components)
            }
        except Exception as e:
            logger.error(f"Error finding related components: {str(e)}")
            return {
                "status": "error",
                "message": f"Error finding related components: {str(e)}"
            }
    
    # Start a background thread to keep the unified context updated
    def update_unified_context_thread():
        """Background thread to update unified context for active projects."""
        logger.info("Starting unified context update thread")
        
        while True:
            try:
                # Get a copy of active projects
                with unified_context_data["context_lock"]:
                    active_projects = list(unified_context_data["active_projects"])
                
                # Update context for each active project
                for project_path in active_projects:
                    try:
                        if os.path.exists(project_path):
                            logger.info(f"Updating unified context for {project_path}")
                            context = build_unified_context(project_path)
                            
                            with unified_context_data["context_lock"]:
                                unified_context_data["context"][project_path] = context
                                unified_context_data["last_updated"] = time.time()
                        else:
                            logger.warning(f"Project path no longer exists: {project_path}")
                            with unified_context_data["context_lock"]:
                                unified_context_data["active_projects"].remove(project_path)
                                if project_path in unified_context_data["context"]:
                                    del unified_context_data["context"][project_path]
                    except Exception as e:
                        logger.error(f"Error updating unified context for {project_path}: {str(e)}")
                
                # Sleep for the update interval
                time.sleep(unified_context_data["update_interval"])
            except Exception as e:
                logger.error(f"Error in unified context update thread: {str(e)}")
                time.sleep(60)  # Sleep for a minute on error
    
    # Start the update thread
    update_thread = threading.Thread(target=update_unified_context_thread, daemon=True)
    update_thread.start()
    
    logger.info("Registered unified context tools")

# Function to be called when the module is imported
def initialize():
    """Initialize the unified context integration module."""
    logger.info("Initializing unified context integration module")
    
    # This function will be called when the module is imported by the AI Librarian server
    # The actual tool registration happens in register_unified_context_tools, which is called by the server

# If this module is directly executed, print a helpful message
if __name__ == "__main__":
    print("This module is designed to be imported by the AI Librarian server.")
    print("Please run the AI Librarian server instead.")
