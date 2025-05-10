#!/usr/bin/env python3
"""
Bidirectional Reference System

This module implements bidirectional references between AI Librarian components and Tool Reference tools,
enabling more efficient navigation and context awareness.

Usage:
    from aitoolkit.librarian.bidirectional_refs import BidirectionalReferenceSystem
    
    brs = BidirectionalReferenceSystem(project_path)
    brs.build_references()
    brs.save_references()
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

# Configure logging
logger = logging.getLogger("bidirectional-refs")

class BidirectionalReferenceSystem:
    """
    Implements bidirectional references between AI Librarian and Tool Reference.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the Bidirectional Reference System.
        
        Args:
            project_path: Root path of the project
        """
        self.project_path = project_path
        self.ai_ref_path = os.path.join(project_path, ".ai_reference")
        self.tool_ref_path = os.path.join(project_path, ".tool_reference")
        
        # Check if both systems exist
        self.ai_librarian_available = os.path.exists(self.ai_ref_path)
        self.tool_reference_available = os.path.exists(self.tool_ref_path)
        
        # Data structures
        self.component_registry = {}
        self.script_index = {}
        self.tool_registry = {}
        self.tool_profiles = {}
        
        # Reference maps
        self.component_to_tool_refs = {}
        self.tool_to_component_refs = {}
    
    def build_references(self) -> bool:
        """
        Build bidirectional references between components and tools.
        
        Returns:
            True if references were built successfully, False otherwise
        """
        if not self.ai_librarian_available or not self.tool_reference_available:
            logger.warning("Both AI Librarian and Tool Reference are required for bidirectional references")
            return False
        
        # Load data from both systems
        if not self._load_data():
            return False
        
        # Build component-to-tool references
        self._build_component_to_tool_references()
        
        # Build tool-to-component references
        self._build_tool_to_component_references()
        
        # Enhance references with semantic analysis
        self._enhance_references_with_semantics()
        
        return True
    
    def save_references(self) -> bool:
        """
        Save the bidirectional references to both systems.
        
        Returns:
            True if references were saved successfully, False otherwise
        """
        try:
            # Save component-to-tool references to AI Librarian
            self._save_component_references()
            
            # Save tool-to-component references to Tool Reference
            self._save_tool_references()
            
            # Save a unified reference map
            self._save_unified_reference_map()
            
            return True
        except Exception as e:
            logger.error(f"Error saving bidirectional references: {str(e)}")
            return False
    
    def _load_data(self) -> bool:
        """
        Load data from both AI Librarian and Tool Reference systems.
        
        Returns:
            True if data was loaded successfully, False otherwise
        """
        try:
            # Load AI Librarian data
            component_registry_path = os.path.join(self.ai_ref_path, "component_registry.json")
            script_index_path = os.path.join(self.ai_ref_path, "script_index.json")
            
            if not os.path.exists(component_registry_path) or not os.path.exists(script_index_path):
                logger.error("AI Librarian component registry or script index not found")
                return False
            
            with open(component_registry_path, 'r', encoding='utf-8') as f:
                self.component_registry = json.load(f)
            
            with open(script_index_path, 'r', encoding='utf-8') as f:
                self.script_index = json.load(f)
            
            # Load Tool Reference data
            registry_path = os.path.join(self.tool_ref_path, "registry.json")
            
            if not os.path.exists(registry_path):
                logger.error("Tool Reference registry not found")
                return False
            
            with open(registry_path, 'r', encoding='utf-8') as f:
                self.tool_registry = json.load(f)
            
            # Load tool profiles
            for tool_id, tool_info in self.tool_registry.get("tools", {}).items():
                if tool_info.get("has_profile", False):
                    profile_path = os.path.join(self.tool_ref_path, tool_info.get("profile_path", ""))
                    if os.path.exists(profile_path):
                        with open(profile_path, 'r', encoding='utf-8') as f:
                            self.tool_profiles[tool_id] = json.load(f)
            
            return True
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def _build_component_to_tool_references(self) -> None:
        """
        Build references from components to tools.
        """
        components = self.component_registry.get("components", {})
        tools = self.tool_registry.get("tools", {})
        
        # Iterate through all components
        for component_name, component_info in components.items():
            self.component_to_tool_refs[component_name] = []
            
            # Check if component file contains tool usage
            file_path = component_info.get("file", "")
            if file_path:
                tools_in_file = self._find_tools_in_file(file_path)
                if tools_in_file:
                    self.component_to_tool_refs[component_name].extend(tools_in_file)
            
            # Look for tool name matches in component name
            for tool_id in tools:
                # Check if tool name is part of component name
                if tool_id.lower() in component_name.lower():
                    if tool_id not in self.component_to_tool_refs[component_name]:
                        self.component_to_tool_refs[component_name].append(tool_id)
    
    def _build_tool_to_component_references(self) -> None:
        """
        Build references from tools to components.
        """
        components = self.component_registry.get("components", {})
        
        # Iterate through all tools
        for tool_id in self.tool_profiles:
            self.tool_to_component_refs[tool_id] = []
            
            # Get the tool profile as text
            tool_profile = self.tool_profiles[tool_id]
            profile_text = json.dumps(tool_profile)
            
            # Look for component references in the profile
            for component_name in components:
                if component_name in profile_text:
                    self.tool_to_component_refs[tool_id].append(component_name)
            
            # Check for function name matches
            for component_name, component_info in components.items():
                if component_info.get("type") == "function" and tool_id.lower() == component_name.lower():
                    if component_name not in self.tool_to_component_refs[tool_id]:
                        self.tool_to_component_refs[tool_id].append(component_name)
    
    def _enhance_references_with_semantics(self) -> None:
        """
        Enhance references with semantic analysis of relationships.
        """
        # Add references based on tool categories
        categories = {}
        for tool_id, tool_info in self.tool_registry.get("tools", {}).items():
            category = tool_info.get("category", "unknown")
            if category not in categories:
                categories[category] = []
            categories[category].append(tool_id)
        
        # Find components that match tool categories
        for component_name, component_info in self.component_registry.get("components", {}).items():
            component_file = component_info.get("file", "")
            
            # Check file path for category matches
            for category, tools in categories.items():
                if category.lower() in component_file.lower():
                    for tool_id in tools:
                        # Add bidirectional references
                        if tool_id not in self.component_to_tool_refs.get(component_name, []):
                            if component_name not in self.component_to_tool_refs:
                                self.component_to_tool_refs[component_name] = []
                            self.component_to_tool_refs[component_name].append(tool_id)
                        
                        if component_name not in self.tool_to_component_refs.get(tool_id, []):
                            if tool_id not in self.tool_to_component_refs:
                                self.tool_to_component_refs[tool_id] = []
                            self.tool_to_component_refs[tool_id].append(component_name)
    
    def _find_tools_in_file(self, file_path: str) -> List[str]:
        """
        Find tools referenced in a file.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            List of tool IDs found in the file
        """
        tools_found = []
        tool_ids = list(self.tool_registry.get("tools", {}).keys())
        
        try:
            full_path = os.path.join(self.project_path, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Use a more sophisticated pattern to find tool references
                # Look for patterns like "def tool_name", "@mcp.tool()\ndef tool_name", "tool_name("
                for tool_id in tool_ids:
                    # Patterns to search for
                    patterns = [
                        r"def\s+" + re.escape(tool_id) + r"\s*\(",  # Function definition
                        r"@mcp\.tool\(\).*?def\s+" + re.escape(tool_id),  # MCP tool decorator
                        r"[^a-zA-Z0-9_]" + re.escape(tool_id) + r"\s*\("  # Function call
                    ]
                    
                    for pattern in patterns:
                        if re.search(pattern, content, re.DOTALL):
                            tools_found.append(tool_id)
                            break
        except Exception as e:
            logger.error(f"Error searching for tools in file {file_path}: {str(e)}")
        
        return tools_found
    
    def _save_component_references(self) -> None:
        """
        Save tool references to the component registry.
        """
        # Add tool references to the component registry
        components = self.component_registry.get("components", {})
        modified = False
        
        for component_name, refs in self.component_to_tool_refs.items():
            if component_name in components and refs:
                # Create a copy to avoid modifying the original during iteration
                component_copy = components[component_name].copy()
                
                # Add tool references to the component
                component_copy["tool_references"] = refs
                
                # Update the component in the registry
                components[component_name] = component_copy
                modified = True
        
        # Save the updated component registry
        if modified:
            component_registry_path = os.path.join(self.ai_ref_path, "component_registry.json")
            with open(component_registry_path, 'w', encoding='utf-8') as f:
                json.dump(self.component_registry, f, indent=2)
            
            logger.info("Saved component-to-tool references to AI Librarian")
    
    def _save_tool_references(self) -> None:
        """
        Save component references to the tool profiles.
        """
        # Add component references to tool profiles
        modified_profiles = []
        
        for tool_id, refs in self.tool_to_component_refs.items():
            if tool_id in self.tool_profiles and refs:
                # Add component references to the tool profile
                profile = self.tool_profiles[tool_id]
                profile["component_references"] = refs
                
                # Save the updated profile
                profile_path = os.path.join(
                    self.tool_ref_path,
                    self.tool_registry["tools"][tool_id].get("profile_path", "")
                )
                
                if os.path.exists(profile_path):
                    with open(profile_path, 'w', encoding='utf-8') as f:
                        json.dump(profile, f, indent=2)
                    
                    modified_profiles.append(tool_id)
        
        if modified_profiles:
            logger.info(f"Saved tool-to-component references for {len(modified_profiles)} tool profiles")
    
    def _save_unified_reference_map(self) -> None:
        """
        Save a unified reference map that contains all bidirectional references.
        """
        reference_map = {
            "version": "1.0.0",
            "description": "Bidirectional references between AI Librarian components and Tool Reference tools",
            "component_to_tool": self.component_to_tool_refs,
            "tool_to_component": self.tool_to_component_refs,
            "components_count": len(self.component_to_tool_refs),
            "tools_count": len(self.tool_to_component_refs)
        }
        
        # Add timestamp
        from datetime import datetime
        reference_map["last_updated"] = datetime.now().isoformat()
        
        # Save to both systems for redundancy
        unified_map_path_ai = os.path.join(self.ai_ref_path, "bidirectional_refs.json")
        unified_map_path_tool = os.path.join(self.tool_ref_path, "bidirectional_refs.json")
        
        with open(unified_map_path_ai, 'w', encoding='utf-8') as f:
            json.dump(reference_map, f, indent=2)
        
        with open(unified_map_path_tool, 'w', encoding='utf-8') as f:
            json.dump(reference_map, f, indent=2)
        
        logger.info("Saved unified reference map to both systems")

def build_bidirectional_references(project_path: str) -> bool:
    """
    Build bidirectional references for the specified project.
    
    Args:
        project_path: Root path of the project
        
    Returns:
        True if references were built and saved successfully, False otherwise
    """
    brs = BidirectionalReferenceSystem(project_path)
    if brs.build_references():
        return brs.save_references()
    return False
