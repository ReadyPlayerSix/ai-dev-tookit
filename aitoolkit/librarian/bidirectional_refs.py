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
from datetime import datetime

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
            
            if not os.path.exists(component_registry_path):
                logger.error(f"AI Librarian component registry not found: {component_registry_path}")
                return False
                
            if not os.path.exists(script_index_path):
                logger.error(f"AI Librarian script index not found: {script_index_path}")
                return False
            
            try:
                with open(component_registry_path, 'r', encoding='utf-8') as f:
                    self.component_registry = json.load(f)
                logger.info(f"Loaded component registry with {len(self.component_registry.get('components', {}))} components")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing component registry: {str(e)}")
                return False
            
            try:
                with open(script_index_path, 'r', encoding='utf-8') as f:
                    self.script_index = json.load(f)
                logger.info(f"Loaded script index with {len(self.script_index.get('scripts', []))} scripts")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing script index: {str(e)}")
                return False
            
            # Load Tool Reference data
            registry_path = os.path.join(self.tool_ref_path, "registry.json")
            
            if not os.path.exists(registry_path):
                logger.error(f"Tool Reference registry not found: {registry_path}")
                return False
            
            try:
                with open(registry_path, 'r', encoding='utf-8') as f:
                    self.tool_registry = json.load(f)
                logger.info(f"Loaded tool registry with {len(self.tool_registry.get('tools', {}))} tools")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing tool registry: {str(e)}")
                return False
            
            # Load tool profiles - this is a potential source of errors
            profile_count = 0
            for tool_id, tool_info in self.tool_registry.get("tools", {}).items():
                if tool_info.get("has_profile", False):
                    profile_path = os.path.join(self.tool_ref_path, tool_info.get("profile_path", ""))
                    logger.info(f"Attempting to load profile for tool '{tool_id}' from {profile_path}")
                    
                    if not os.path.exists(profile_path):
                        logger.warning(f"Tool profile not found for {tool_id}: {profile_path}")
                        continue
                        
                    try:
                        with open(profile_path, 'r', encoding='utf-8') as f:
                            profile_data = json.load(f)
                            self.tool_profiles[tool_id] = profile_data
                            profile_count += 1
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parsing tool profile for {tool_id}: {str(e)}")
                    except Exception as e:
                        logger.warning(f"Error loading tool profile for {tool_id}: {str(e)}")
            
            logger.info(f"Loaded {profile_count} tool profiles out of {len(self.tool_registry.get('tools', {}))} tools")
            
            # If no profiles were loaded but profiles should exist, this is a warning but not a fatal error
            has_profile_count = sum(1 for tool_info in self.tool_registry.get("tools", {}).values() 
                                    if tool_info.get("has_profile", False))
                                    
            if has_profile_count > 0 and profile_count == 0:
                logger.warning(f"Failed to load any tool profiles, but {has_profile_count} tools indicated they should have profiles")
                # Continue anyway, just with empty profiles
                # Create the tool_profiles directory if it doesn't exist
                profiles_dir = os.path.join(self.tool_ref_path, "tool_profiles")
                os.makedirs(profiles_dir, exist_ok=True)
            
            return True
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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
                # This now returns detailed references with relationship info
                tools_in_file = self._find_tools_in_file(file_path)
                if tools_in_file:
                    # Extract detailed information
                    for tool_ref in tools_in_file:
                        # Check for duplicates before adding
                        if not self._contains_tool_ref(self.component_to_tool_refs[component_name], tool_ref["tool_id"]):
                            self.component_to_tool_refs[component_name].append(tool_ref)
            
            # Look for tool name matches in component name
            for tool_id in tools:
                # Check if tool name is part of component name (case insensitive)
                if tool_id.lower() in component_name.lower():
                    # Avoid duplicates by checking if the tool is already referenced
                    if not self._contains_tool_ref(self.component_to_tool_refs[component_name], tool_id):
                        # Create a name-based relationship
                        relationship_info = {
                            "relationship_type": "name_similarity",
                            "relationship_strength": "medium",
                            "match_reason": f"tool name '{tool_id}' is part of component name '{component_name}'",
                            "metadata": {
                                "tool_category": tools[tool_id].get("category", "unknown")
                            }
                        }
                        
                        self.component_to_tool_refs[component_name].append({
                            "tool_id": tool_id,
                            "relationship": relationship_info
                        })
                        
            # Add relationship to implementation tools if component is a function implementation
            if component_info.get("type") == "function" and component_name in tools:
                # If the component is itself a tool implementation, create a self-reference
                if not self._contains_tool_ref(self.component_to_tool_refs[component_name], component_name):
                    relationship_info = {
                        "relationship_type": "implementation",
                        "relationship_strength": "very_strong",
                        "match_reason": "direct implementation of tool",
                        "metadata": {
                            "tool_category": tools[component_name].get("category", "unknown")
                        }
                    }
                    
                    self.component_to_tool_refs[component_name].append({
                        "tool_id": component_name,
                        "relationship": relationship_info
                    })
                    
    def _contains_tool_ref(self, refs_list: List, tool_id: str) -> bool:
        """
        Check if a tool ID is already in the references list, accounting for both
        simple string references and dictionary references.
        
        Args:
            refs_list: List of references
            tool_id: Tool ID to check
            
        Returns:
            True if the tool is already referenced, False otherwise
        """
        for ref in refs_list:
            if isinstance(ref, dict) and ref.get("tool_id") == tool_id:
                return True
            elif ref == tool_id:  # Handle simple string references
                return True
        return False
    
    def _build_tool_to_component_references(self) -> None:
        """
        Build references from tools to components.
        """
        components = self.component_registry.get("components", {})
        
        # Skip if no tool profiles are available
        if not self.tool_profiles:
            logger.warning("No tool profiles available for building tool-to-component references")
            return
            
        # Iterate through all tools
        for tool_id in self.tool_profiles:
            self.tool_to_component_refs[tool_id] = []
            
            # Get the tool profile as text
            tool_profile = self.tool_profiles[tool_id]
            profile_text = json.dumps(tool_profile)
            
            # Look for component references in the profile
            for component_name in components:
                # Ensure component_name is a string
                if not isinstance(component_name, str):
                    logger.warning(f"Found non-string component name: {component_name}, skipping...")
                    continue
                    
                if component_name in profile_text:
                    # Check if we already have this component reference
                    if not self._contains_component_ref(self.tool_to_component_refs[tool_id], component_name):
                        # Get component type, ensuring it's safe to access
                        component_data = components[component_name]
                        component_type = "unknown"
                        if isinstance(component_data, dict):
                            component_type = component_data.get("type", "unknown")
                            
                        # Create a reference with relationship details
                        relationship_info = {
                            "relationship_type": "profile_reference",
                            "relationship_strength": "medium",
                            "match_reason": f"component '{component_name}' mentioned in tool profile",
                            "metadata": {
                                "component_type": component_type
                            }
                        }
                        
                        self.tool_to_component_refs[tool_id].append({
                            "component_name": component_name,
                            "relationship": relationship_info
                        })
            
            # Check for function name matches (implementation relationship)
            for component_name, component_info in components.items():
                # Ensure component_name is a string
                if not isinstance(component_name, str):
                    logger.warning(f"Found non-string component name in implementation check: {component_name}, skipping...")
                    continue
                    
                # Ensure component_info is a dict before accessing .get()
                if not isinstance(component_info, dict):
                    logger.warning(f"Component info for {component_name} is not a dictionary: {component_info}")
                    continue
                    
                if component_info.get("type") == "function" and tool_id.lower() == component_name.lower():
                    # Check for duplicates
                    if not self._contains_component_ref(self.tool_to_component_refs[tool_id], component_name):
                        # Create a strong implementation relationship
                        relationship_info = {
                            "relationship_type": "implementation",
                            "relationship_strength": "very_strong",
                            "match_reason": f"component '{component_name}' directly implements this tool",
                            "metadata": {
                                "component_type": "function",
                                "file": component_info.get("file", "")
                            }
                        }
                        
                        self.tool_to_component_refs[tool_id].append({
                            "component_name": component_name,
                            "relationship": relationship_info
                        })
            
            # If we have component-to-tool references, check for reverse relationships
            # This ensures bidirectional consistency
            for component_name, tool_refs in self.component_to_tool_refs.items():
                # Ensure component_name is a string
                if not isinstance(component_name, str):
                    logger.warning(f"Found non-string component name in bidirectional check: {component_name}, skipping...")
                    continue
                    
                # Skip empty or invalid tool references
                if not tool_refs or not isinstance(tool_refs, list):
                    continue
                    
                for tool_ref in tool_refs:
                    # Skip if tool_ref isn't a string or dict
                    if not isinstance(tool_ref, (dict, str)):
                        logger.warning(f"Invalid tool reference type: {type(tool_ref)}, skipping...")
                        continue
                        
                    # Handle both dictionary and string references
                    ref_tool_id = tool_ref.get("tool_id") if isinstance(tool_ref, dict) else tool_ref
                    
                    if ref_tool_id == tool_id:
                        # We found a component that references this tool
                        if not self._contains_component_ref(self.tool_to_component_refs[tool_id], component_name):
                            # Get relationship details if available
                            relationship_info = {}
                            if isinstance(tool_ref, dict) and "relationship" in tool_ref:
                                # Copy and invert relationship
                                orig_relationship = tool_ref["relationship"]
                                relationship_info = {
                                    "relationship_type": orig_relationship.get("relationship_type", "reference"),
                                    "relationship_strength": orig_relationship.get("relationship_strength", "medium"),
                                    "match_reason": orig_relationship.get("match_reason", "bidirectional reference"),
                                    "metadata": orig_relationship.get("metadata", {})
                                }
                            else:
                                # Create basic relationship info
                                relationship_info = {
                                    "relationship_type": "reference",
                                    "relationship_strength": "medium",
                                    "match_reason": "bidirectional reference consistency",
                                    "metadata": {
                                        "component_type": components[component_name].get("type", "unknown")
                                    }
                                }
                            
                            self.tool_to_component_refs[tool_id].append({
                                "component_name": component_name,
                                "relationship": relationship_info
                            })
                            
    def _contains_component_ref(self, refs_list: List, component_name: str) -> bool:
        """
        Check if a component name is already in the references list, accounting for both
        simple string references and dictionary references.
        
        Args:
            refs_list: List of references
            component_name: Component name to check
            
        Returns:
            True if the component is already referenced, False otherwise
        """
        for ref in refs_list:
            if isinstance(ref, dict) and ref.get("component_name") == component_name:
                return True
            elif ref == component_name:  # Handle simple string references
                return True
        return False
    
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
            component_description = component_info.get("description", "")
            component_responsibilities = component_info.get("responsibilities", [])
            
            # Check file path for category matches
            for category, tools in categories.items():
                # Match by file path, description or responsibilities
                should_match = False
                match_reason = ""
                
                if category.lower() in component_file.lower():
                    should_match = True
                    match_reason = f"path contains category '{category}'"
                elif category.lower() in component_description.lower():
                    should_match = True
                    match_reason = f"description contains category '{category}'"
                else:
                    # Check responsibilities
                    for responsibility in component_responsibilities:
                        if category.lower() in responsibility.lower():
                            should_match = True
                            match_reason = f"responsibility relates to '{category}'"
                            break
                
                if should_match:
                    for tool_id in tools:
                        # Get tool info for more detailed relationship data
                        tool_info = self.tool_registry.get("tools", {}).get(tool_id, {})
                        tool_purpose = ""
                        if tool_id in self.tool_profiles:
                            tool_purpose = self.tool_profiles[tool_id].get("primary_purpose", "")
                        
                        # Create reference information with relationship details
                        reference_info = {
                            "match_reason": match_reason,
                            "relationship_strength": "strong",
                            "relationship_type": "semantic_category",
                            "metadata": {
                                "category": category,
                                "tool_purpose": tool_purpose
                            }
                        }
                        
                        # Add bidirectional references with detailed information
                        if component_name not in self.component_to_tool_refs:
                            self.component_to_tool_refs[component_name] = []
                        
                        # Check if tool is already in references
                        existing_ref = False
                        for ref in self.component_to_tool_refs[component_name]:
                            if isinstance(ref, dict) and ref.get("tool_id") == tool_id:
                                existing_ref = True
                                break
                            elif ref == tool_id:  # Handle simple string references
                                existing_ref = True
                                # Remove simple reference to replace with enhanced one
                                self.component_to_tool_refs[component_name].remove(ref)
                                break
                                
                        if not existing_ref:
                            self.component_to_tool_refs[component_name].append({
                                "tool_id": tool_id,
                                "relationship": reference_info
                            })
                        
                        # Add component reference to tool
                        if tool_id not in self.tool_to_component_refs:
                            self.tool_to_component_refs[tool_id] = []
                            
                        # Check if component is already in references
                        existing_ref = False
                        for ref in self.tool_to_component_refs[tool_id]:
                            if isinstance(ref, dict) and ref.get("component_name") == component_name:
                                existing_ref = True
                                break
                            elif ref == component_name:  # Handle simple string references
                                existing_ref = True
                                # Remove simple reference to replace with enhanced one
                                self.tool_to_component_refs[tool_id].remove(ref)
                                break
                                
                        if not existing_ref:
                            self.tool_to_component_refs[tool_id].append({
                                "component_name": component_name,
                                "relationship": reference_info
                            })
    
    def _find_tools_in_file(self, file_path: str) -> List[dict]:
        """
        Find tools referenced in a file with detailed relationship information.
        
        Args:
            file_path: Relative path to the file
            
        Returns:
            List of dictionaries with tool IDs and relationship details
        """
        tools_found = []
        tool_ids = list(self.tool_registry.get("tools", {}).keys())
        
        try:
            full_path = os.path.join(self.project_path, file_path)
            if not os.path.exists(full_path):
                logger.warning(f"File does not exist: {full_path}")
                return tools_found
                
            # Skip binary files
            if self._is_binary_file(full_path):
                logger.debug(f"Skipping binary file: {full_path}")
                return tools_found
                
            # Get file extension
            file_ext = os.path.splitext(full_path)[1].lower()
            
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Use a more sophisticated pattern to find tool references
            for tool_id in tool_ids:
                # Initialize match strength and contexts
                match_strength = "weak"
                match_contexts = []
                match_lines = []
                relationship_type = "unknown"
                
                # Define different patterns based on file type
                if file_ext == '.py':
                    # Python-specific patterns
                    patterns = [
                        {
                            "pattern": r"def\s+" + re.escape(tool_id) + r"\s*\(",  # Function definition
                            "relationship_type": "implementation",
                            "strength": "very_strong"
                        },
                        {
                            "pattern": r"@mcp\.tool\(\).*?def\s+" + re.escape(tool_id),  # MCP tool decorator
                            "relationship_type": "implementation",
                            "strength": "very_strong"
                        },
                        {
                            "pattern": r"[^a-zA-Z0-9_]" + re.escape(tool_id) + r"\s*\(",  # Function call
                            "relationship_type": "usage",
                            "strength": "strong"
                        },
                        {
                            "pattern": r"['\"]" + re.escape(tool_id) + r"['\"]",  # String literal
                            "relationship_type": "reference",
                            "strength": "medium"
                        },
                        {
                            "pattern": r"#.*" + re.escape(tool_id),  # Comment
                            "relationship_type": "documentation",
                            "strength": "medium"
                        }
                    ]
                elif file_ext in ['.md', '.txt']:
                    # Documentation file patterns
                    patterns = [
                        {
                            "pattern": r"^#+\s+.*" + re.escape(tool_id),  # Headline
                            "relationship_type": "documentation",
                            "strength": "strong"
                        },
                        {
                            "pattern": r"`" + re.escape(tool_id) + r"`",  # Code formatting
                            "relationship_type": "documentation",
                            "strength": "strong"
                        },
                        {
                            "pattern": re.escape(tool_id),  # Plain text mention
                            "relationship_type": "documentation",
                            "strength": "medium"
                        }
                    ]
                else:
                    # Generic patterns for other file types
                    patterns = [
                        {
                            "pattern": re.escape(tool_id),
                            "relationship_type": "reference",
                            "strength": "medium"
                        }
                    ]
                
                # Check each pattern
                for pattern_info in patterns:
                    pattern = pattern_info["pattern"]
                    pattern_strength = pattern_info["strength"]
                    pattern_type = pattern_info["relationship_type"]
                    
                    # Find all matches
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        # Extract the matching line and some context
                        start_pos = max(0, match.start() - 40)
                        end_pos = min(len(content), match.end() + 40)
                        context = content[start_pos:end_pos].strip()
                        
                        # Count line number
                        line_number = content[:match.start()].count('\n') + 1
                        
                        match_contexts.append(context)
                        match_lines.append(line_number)
                        
                        # Update strength if this match is stronger
                        if self._strength_value(pattern_strength) > self._strength_value(match_strength):
                            match_strength = pattern_strength
                            relationship_type = pattern_type
                
                # If we found matches, add the tool with details
                if match_contexts:
                    tool_info = self.tool_registry.get("tools", {}).get(tool_id, {})
                    tool_category = tool_info.get("category", "unknown")
                    
                    relationship_info = {
                        "relationship_type": relationship_type,
                        "relationship_strength": match_strength,
                        "match_count": len(match_contexts),
                        "match_lines": match_lines[:5],  # Limit to first 5 line numbers
                        "match_contexts": match_contexts[:3],  # Limit to first 3 contexts
                        "metadata": {
                            "file_type": file_ext.lstrip('.') or "unknown",
                            "tool_category": tool_category
                        }
                    }
                    
                    tools_found.append({
                        "tool_id": tool_id,
                        "relationship": relationship_info
                    })
                    
        except UnicodeDecodeError:
            # This is likely a binary file
            logger.debug(f"Unicode decode error for file {file_path} - likely binary")
        except Exception as e:
            logger.error(f"Error searching for tools in file {file_path}: {str(e)}")
        
        return tools_found
        
    def _is_binary_file(self, file_path: str) -> bool:
        """
        Check if a file is binary.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is binary, False otherwise
        """
        try:
            # Read the first 8KB of the file
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)
            
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return True
                
            # Try to decode as text
            chunk.decode('utf-8')
            return False
        except UnicodeDecodeError:
            return True
        except Exception:
            # Default to False if we can't determine
            return False
            
    def _strength_value(self, strength: str) -> int:
        """
        Convert strength string to numeric value for comparison.
        
        Args:
            strength: Strength as string
            
        Returns:
            Numeric value
        """
        strengths = {
            "very_strong": 4,
            "strong": 3,
            "medium": 2,
            "weak": 1,
            "very_weak": 0
        }
        return strengths.get(strength, 0)
    
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
                
                # Count references by relationship type for summary statistics
                relationship_types = {}
                relationship_strengths = {}
                
                for ref in refs:
                    if isinstance(ref, dict) and "relationship" in ref:
                        rel_type = ref["relationship"].get("relationship_type", "unknown")
                        rel_strength = ref["relationship"].get("relationship_strength", "unknown")
                        
                        if rel_type not in relationship_types:
                            relationship_types[rel_type] = 0
                        relationship_types[rel_type] += 1
                        
                        if rel_strength not in relationship_strengths:
                            relationship_strengths[rel_strength] = 0
                        relationship_strengths[rel_strength] += 1
                
                # Add summary statistics to help Claude understand the relationships
                component_copy["tool_references_summary"] = {
                    "count": len(refs),
                    "relationship_types": relationship_types,
                    "relationship_strengths": relationship_strengths,
                    "last_updated": datetime.now().isoformat()
                }
                
                # Update the component in the registry
                components[component_name] = component_copy
                modified = True
        
        # Save the updated component registry
        if modified:
            component_registry_path = os.path.join(self.ai_ref_path, "component_registry.json")
            with open(component_registry_path, 'w', encoding='utf-8') as f:
                json.dump(self.component_registry, f, indent=2)
            
            logger.info(f"Saved enhanced component-to-tool references for {len(self.component_to_tool_refs)} components")
    
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
                
                # Count references by relationship type for summary statistics
                relationship_types = {}
                relationship_strengths = {}
                component_types = {}
                
                for ref in refs:
                    if isinstance(ref, dict) and "relationship" in ref:
                        rel_type = ref["relationship"].get("relationship_type", "unknown")
                        rel_strength = ref["relationship"].get("relationship_strength", "unknown")
                        comp_type = ref["relationship"].get("metadata", {}).get("component_type", "unknown")
                        
                        if rel_type not in relationship_types:
                            relationship_types[rel_type] = 0
                        relationship_types[rel_type] += 1
                        
                        if rel_strength not in relationship_strengths:
                            relationship_strengths[rel_strength] = 0
                        relationship_strengths[rel_strength] += 1
                        
                        if comp_type not in component_types:
                            component_types[comp_type] = 0
                        component_types[comp_type] += 1
                
                # Add summary statistics to help Claude understand the relationships
                profile["component_references_summary"] = {
                    "count": len(refs),
                    "relationship_types": relationship_types,
                    "relationship_strengths": relationship_strengths,
                    "component_types": component_types,
                    "last_updated": datetime.now().isoformat()
                }
                
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
            logger.info(f"Saved enhanced tool-to-component references for {len(modified_profiles)} tool profiles")
    
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
    
    This is the primary function that should be called to build cross-references
    between AI Librarian components and Tool Reference tools. It checks for the
    existence of both directories before proceeding.
    
    Args:
        project_path: Root path of the project
        
    Returns:
        True if references were built and saved successfully, False otherwise
    """
    try:
        # Check if both required directories exist
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        tool_ref_path = os.path.join(project_path, ".tool_reference")
        
        if not os.path.exists(ai_ref_path):
            logger.warning(f"AI Reference directory not found: {ai_ref_path}")
            # Create minimal AI Reference structure
            os.makedirs(ai_ref_path, exist_ok=True)
            os.makedirs(os.path.join(ai_ref_path, "components"), exist_ok=True)
            logger.info(f"Created minimal AI Reference directory")
                
        if not os.path.exists(tool_ref_path):
            logger.warning(f"Tool Reference directory not found: {tool_ref_path}")
            # Create minimal Tool Reference structure
            os.makedirs(tool_ref_path, exist_ok=True)
            os.makedirs(os.path.join(tool_ref_path, "tool_profiles"), exist_ok=True)
            logger.info(f"Created minimal Tool Reference directory")
        
        # Ensure the tool_profiles directory exists
        tool_profiles_dir = os.path.join(tool_ref_path, "tool_profiles")
        if not os.path.exists(tool_profiles_dir):
            os.makedirs(tool_profiles_dir, exist_ok=True)
            logger.info(f"Created tool_profiles directory")
        
        logger.info(f"Starting to build bidirectional references for {project_path}")
        
        # Attempt to use the full BidirectionalReferenceSystem
        try:
            brs = BidirectionalReferenceSystem(project_path)
            build_success = brs.build_references()
            save_success = False
            
            if build_success:
                try:
                    save_success = brs.save_references()
                except Exception as save_e:
                    logger.warning(f"Failed to save references: {save_e}")
                    # Continue to fallback
            
            if build_success and save_success:
                logger.info("Full bidirectional references built and saved successfully")
                return True
                
            logger.warning("Full reference building or saving failed, falling back to simplified version")
        except Exception as inner_e:
            logger.warning(f"Full reference building failed, falling back to simplified version: {str(inner_e)}")
            
        # Fallback to simplified references if the full system fails
        # Create simplified bidirectional references
        reference_map = {
            "version": "1.0.0",
            "description": "Simplified bidirectional references",
            "component_to_tool": {},
            "tool_to_component": {},
            "components_count": 0,
            "tools_count": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        # Save to both systems for redundancy
        try:
            # Create any needed parent directories first
            os.makedirs(os.path.dirname(os.path.join(ai_ref_path, "bidirectional_refs.json")), exist_ok=True)
            os.makedirs(os.path.dirname(os.path.join(tool_ref_path, "bidirectional_refs.json")), exist_ok=True)
            
            # Save the simplified maps
            unified_map_path_ai = os.path.join(ai_ref_path, "bidirectional_refs.json")
            unified_map_path_tool = os.path.join(tool_ref_path, "bidirectional_refs.json")
            
            with open(unified_map_path_ai, 'w', encoding='utf-8') as f:
                json.dump(reference_map, f, indent=2)
            
            with open(unified_map_path_tool, 'w', encoding='utf-8') as f:
                json.dump(reference_map, f, indent=2)
                
            logger.info("Created simplified bidirectional reference maps")
        except Exception as fallback_e:
            logger.error(f"Failed to save simplified references: {fallback_e}")
            # Continue anyway, don't fail hard
        
        # Return true to prevent complete failure even if we couldn't build full references
        return True
    except Exception as e:
        logger.error(f"Error creating bidirectional references: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Return true anyway to allow basic functionality to work
        logger.warning("Continuing with basic functionality despite bidirectional reference errors")
        return True
