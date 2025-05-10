#!/usr/bin/env python3
"""
Unified Context Builder

This module creates a unified context that bridges the AI Librarian and Tool Reference systems,
enabling faster tool discovery and more efficient contextual navigation.

Usage:
    from aitoolkit.librarian.unified_context import UnifiedContextBuilder
    
    unified_context = UnifiedContextBuilder(project_path)
    context = unified_context.build_context()
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

# Configure logging
logger = logging.getLogger("unified-context-builder")

class UnifiedContextBuilder:
    """
    Builds a unified context that bridges the AI Librarian and Tool Reference systems.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the Unified Context Builder.
        
        Args:
            project_path: Root path of the project
        """
        self.project_path = project_path
        self.ai_ref_path = os.path.join(project_path, ".ai_reference")
        self.tool_ref_path = os.path.join(project_path, ".tool_reference")
        
        # Check if both systems exist
        self.ai_librarian_available = os.path.exists(self.ai_ref_path)
        self.tool_reference_available = os.path.exists(self.tool_ref_path)
        
        # Cache for loaded data
        self.cache = {
            "component_registry": None,
            "script_index": None,
            "tool_registry": None,
            "tool_profiles": {},
            "relationship_groups": {},
            "decision_trees": {}
        }
    
    def build_context(self) -> Dict[str, Any]:
        """
        Build the unified context by combining data from both systems.
        
        Returns:
            Dictionary containing the unified context
        """
        context = {
            "project_path": self.project_path,
            "systems_available": {
                "ai_librarian": self.ai_librarian_available,
                "tool_reference": self.tool_reference_available
            },
            "components": {},
            "tools": {},
            "relationships": {},
            "decision_trees": {},
            "cross_references": {},
            "last_updated": ""
        }
        
        # If neither system is available, return the basic context
        if not self.ai_librarian_available and not self.tool_reference_available:
            logger.warning("Neither AI Librarian nor Tool Reference system found")
            return context
        
        # Load data from AI Librarian if available
        if self.ai_librarian_available:
            self._load_ai_librarian_data()
            self._integrate_ai_librarian_data(context)
        
        # Load data from Tool Reference if available
        if self.tool_reference_available:
            self._load_tool_reference_data()
            self._integrate_tool_reference_data(context)
        
        # Build cross-references
        if self.ai_librarian_available and self.tool_reference_available:
            self._build_cross_references(context)
        
        # Set last updated timestamp
        from datetime import datetime
        context["last_updated"] = datetime.now().isoformat()
        
        return context
    
    def _load_ai_librarian_data(self) -> None:
        """
        Load data from the AI Librarian system.
        """
        try:
            # Load component registry
            component_registry_path = os.path.join(self.ai_ref_path, "component_registry.json")
            if os.path.exists(component_registry_path):
                with open(component_registry_path, 'r', encoding='utf-8') as f:
                    self.cache["component_registry"] = json.load(f)
            
            # Load script index
            script_index_path = os.path.join(self.ai_ref_path, "script_index.json")
            if os.path.exists(script_index_path):
                with open(script_index_path, 'r', encoding='utf-8') as f:
                    self.cache["script_index"] = json.load(f)
        
        except Exception as e:
            logger.error(f"Error loading AI Librarian data: {str(e)}")
    
    def _load_tool_reference_data(self) -> None:
        """
        Load data from the Tool Reference system.
        """
        try:
            # Load tool registry
            registry_path = os.path.join(self.tool_ref_path, "registry.json")
            if os.path.exists(registry_path):
                with open(registry_path, 'r', encoding='utf-8') as f:
                    self.cache["tool_registry"] = json.load(f)
            
            # Load tool profiles
            if self.cache["tool_registry"] and "tools" in self.cache["tool_registry"]:
                for tool_id, tool_info in self.cache["tool_registry"]["tools"].items():
                    if tool_info.get("has_profile", False):
                        profile_path = os.path.join(self.tool_ref_path, tool_info.get("profile_path", ""))
                        if os.path.exists(profile_path):
                            with open(profile_path, 'r', encoding='utf-8') as f:
                                self.cache["tool_profiles"][tool_id] = json.load(f)
            
            # Load relationship groups
            if self.cache["tool_registry"] and "relationships" in self.cache["tool_registry"]:
                for group_name in self.cache["tool_registry"]["relationships"].get("groups", []):
                    rel_path = os.path.join(self.tool_ref_path, f"relationship_{group_name}.json")
                    if os.path.exists(rel_path):
                        with open(rel_path, 'r', encoding='utf-8') as f:
                            self.cache["relationship_groups"][group_name] = json.load(f)
            
            # Load decision trees
            if self.cache["tool_registry"] and "relationships" in self.cache["tool_registry"]:
                for tree_id in self.cache["tool_registry"]["relationships"].get("decision_trees", []):
                    tree_path = os.path.join(self.tool_ref_path, "decision_trees", f"{tree_id}.json")
                    if os.path.exists(tree_path):
                        with open(tree_path, 'r', encoding='utf-8') as f:
                            self.cache["decision_trees"][tree_id] = json.load(f)
        
        except Exception as e:
            logger.error(f"Error loading Tool Reference data: {str(e)}")
    
    def _integrate_ai_librarian_data(self, context: Dict[str, Any]) -> None:
        """
        Integrate AI Librarian data into the unified context.
        
        Args:
            context: The unified context to update
        """
        if not self.cache["component_registry"]:
            return
        
        # Add components to the context
        for component_name, component_info in self.cache["component_registry"].get("components", {}).items():
            context["components"][component_name] = {
                "name": component_name,
                "type": component_info.get("type", "unknown"),
                "file": component_info.get("file", ""),
                "references": component_info.get("references", []),
                "source": "ai_librarian"
            }
    
    def _integrate_tool_reference_data(self, context: Dict[str, Any]) -> None:
        """
        Integrate Tool Reference data into the unified context.
        
        Args:
            context: The unified context to update
        """
        if not self.cache["tool_registry"]:
            return
        
        # Add tools to the context
        for tool_id, tool_info in self.cache["tool_registry"].get("tools", {}).items():
            tool_profile = self.cache["tool_profiles"].get(tool_id, {})
            
            context["tools"][tool_id] = {
                "id": tool_id,
                "category": tool_info.get("category", "unknown"),
                "primary_purpose": tool_profile.get("primary_purpose", ""),
                "always_use_when": tool_profile.get("always_use_when", []),
                "never_use_when": tool_profile.get("never_use_when", []),
                "has_detailed_profile": tool_info.get("has_profile", False),
                "source": "tool_reference"
            }
        
        # Add relationships to the context
        for group_name, group_data in self.cache["relationship_groups"].items():
            context["relationships"][group_name] = {
                "name": group_name,
                "description": group_data.get("description", ""),
                "tools": group_data.get("tools", []),
                "common_sequences": group_data.get("common_sequences", []),
                "source": "tool_reference"
            }
        
        # Add decision trees to the context
        for tree_id, tree_data in self.cache["decision_trees"].items():
            context["decision_trees"][tree_id] = {
                "id": tree_id,
                "description": tree_data.get("description", ""),
                "decision_nodes": tree_data.get("decision_nodes", []),
                "source": "tool_reference"
            }
    
    def _build_cross_references(self, context: Dict[str, Any]) -> None:
        """
        Build cross-references between AI Librarian and Tool Reference data.
        
        Args:
            context: The unified context to update
        """
        cross_refs = {}
        
        # Find tool references in component files
        for component_name, component_info in context["components"].items():
            file_path = component_info.get("file", "")
            if file_path:
                tools_in_file = self._find_tools_in_file(file_path)
                if tools_in_file:
                    if component_name not in cross_refs:
                        cross_refs[component_name] = {"related_tools": []}
                    cross_refs[component_name]["related_tools"].extend(tools_in_file)
        
        # Find components referenced in tool descriptions
        for tool_id, tool_info in context["tools"].items():
            components_in_tool = self._find_components_in_tool(tool_id, tool_info)
            if components_in_tool:
                if tool_id not in cross_refs:
                    cross_refs[tool_id] = {"related_components": []}
                cross_refs[tool_id]["related_components"] = components_in_tool
        
        context["cross_references"] = cross_refs
    
    def _find_tools_in_file(self, file_path: str) -> List[str]:
        """
        Find tools referenced in a file.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            List of tool IDs found in the file
        """
        tools_found = []
        
        # Skip if no tool registry
        if not self.cache["tool_registry"]:
            return tools_found
            
        # Get all tool IDs
        tool_ids = list(self.cache["tool_registry"].get("tools", {}).keys())
        
        # Try to read the file
        try:
            full_path = os.path.join(self.project_path, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for tool references
                for tool_id in tool_ids:
                    if tool_id in content:
                        tools_found.append(tool_id)
        except Exception as e:
            logger.error(f"Error searching for tools in file {file_path}: {str(e)}")
        
        return tools_found
    
    def _find_components_in_tool(self, tool_id: str, tool_info: Dict[str, Any]) -> List[str]:
        """
        Find components referenced in a tool's profile.
        
        Args:
            tool_id: ID of the tool
            tool_info: Information about the tool
            
        Returns:
            List of component names found in the tool's profile
        """
        components_found = []
        
        # Skip if no component registry
        if not self.cache["component_registry"]:
            return components_found
            
        # Get all component names
        component_names = list(self.cache["component_registry"].get("components", {}).keys())
        
        # Get the tool profile
        tool_profile = self.cache["tool_profiles"].get(tool_id, {})
        profile_text = json.dumps(tool_profile)
        
        # Look for component references
        for component_name in component_names:
            if component_name in profile_text:
                components_found.append(component_name)
        
        return components_found

def build_unified_context(project_path: str) -> Dict[str, Any]:
    """
    Build a unified context for the specified project.
    
    Args:
        project_path: Root path of the project
        
    Returns:
        Dictionary containing the unified context
    """
    builder = UnifiedContextBuilder(project_path)
    return builder.build_context()
