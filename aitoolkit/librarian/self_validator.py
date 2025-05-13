#!/usr/bin/env python3
"""
AI Librarian Self-Validator

This module provides self-validation capabilities for the AI Librarian,
allowing it to check the accuracy and completeness of its component registry
and other stored information.
"""

import os
import sys
import json
import time
import logging
import inspect
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set

# Configure logger
logger = logging.getLogger("ai_librarian.self_validator")

class SelfValidator:
    """
    Validates the accuracy and completeness of the AI Librarian's data.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the self-validator.
        
        Args:
            project_path: The root directory of the project
        """
        self.project_path = project_path
        self.ai_ref_path = os.path.join(project_path, ".ai_reference")
        self.diagnostics_path = os.path.join(self.ai_ref_path, "diagnostics")
        
        # Create diagnostics directory if it doesn't exist
        os.makedirs(self.diagnostics_path, exist_ok=True)
        
        # Paths to key files
        self.component_registry_path = os.path.join(self.ai_ref_path, "component_registry.json")
        self.script_index_path = os.path.join(self.ai_ref_path, "script_index.json")
        
        logger.info(f"Initialized self-validator for {project_path}")
    
    def validate_component_registry(self) -> Dict[str, Any]:
        """
        Validate the component registry against the actual codebase.
        
        Returns:
            Validation results
        """
        results = {
            "status": "success",
            "components_analyzed": 0,
            "components_verified": 0,
            "components_missing": 0,
            "components_outdated": 0,
            "dependency_errors": 0,
            "missing_components": [],
            "outdated_components": [],
            "dependency_issues": []
        }
        
        try:
            # Load component registry
            if not os.path.exists(self.component_registry_path):
                return {
                    "status": "error",
                    "message": "Component registry not found"
                }
            
            with open(self.component_registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            
            # Get all Python files in the project
            python_files = self._find_python_files()
            
            # Extract actual components from files
            actual_components = self._extract_components_from_files(python_files)
            
            # Check registry against actual components
            registry_components = registry.get("components", {})
            results["components_analyzed"] = len(registry_components)
            
            for component_name, component_info in registry_components.items():
                # Check if component exists in actual components
                if component_name in actual_components:
                    results["components_verified"] += 1
                    
                    # Check if primary file matches
                    actual_file = actual_components[component_name]["file"]
                    registry_file = component_info.get("primary_file", "")
                    
                    # Normalize paths for comparison
                    actual_file = os.path.normpath(actual_file)
                    registry_file = os.path.normpath(registry_file)
                    
                    if registry_file and not self._paths_match(actual_file, registry_file):
                        results["components_outdated"] += 1
                        results["outdated_components"].append({
                            "component": component_name,
                            "registry_file": registry_file,
                            "actual_file": actual_file
                        })
                    
                    # Check dependencies
                    registry_deps = set(component_info.get("dependencies", []))
                    actual_deps = set(actual_components[component_name].get("dependencies", []))
                    
                    missing_deps = actual_deps - registry_deps
                    if missing_deps:
                        results["dependency_errors"] += 1
                        results["dependency_issues"].append({
                            "component": component_name,
                            "missing_dependencies": list(missing_deps)
                        })
                else:
                    results["components_missing"] += 1
                    results["missing_components"].append(component_name)
            
            # Check for components in actual but not in registry
            actual_not_in_registry = set(actual_components.keys()) - set(registry_components.keys())
            
            if actual_not_in_registry:
                results["new_components"] = list(actual_not_in_registry)
                results["new_components_count"] = len(actual_not_in_registry)
            
            # Calculate percentages for easier reporting
            if results["components_analyzed"] > 0:
                results["verified_percentage"] = round(
                    (results["components_verified"] - results["components_outdated"]) / 
                    results["components_analyzed"] * 100, 2
                )
            
            # Overall status
            if results["components_missing"] > 0 or results["components_outdated"] > 0 or results["dependency_errors"] > 0:
                results["status"] = "issues_found"
            
        except Exception as e:
            logger.error(f"Error validating component registry: {str(e)}")
            results = {
                "status": "error",
                "message": f"Error validating component registry: {str(e)}"
            }
        
        return results
    
    def validate_script_index(self) -> Dict[str, Any]:
        """
        Validate the script index against the actual files.
        
        Returns:
            Validation results
        """
        results = {
            "status": "success",
            "files_analyzed": 0,
            "files_verified": 0,
            "files_missing": 0,
            "new_files": 0,
            "missing_files": []
        }
        
        try:
            # Load script index
            if not os.path.exists(self.script_index_path):
                return {
                    "status": "error",
                    "message": "Script index not found"
                }
            
            with open(self.script_index_path, 'r', encoding='utf-8') as f:
                script_index = json.load(f)
            
            # Get actual files
            actual_files = set(self._find_python_files())
            
            # Check index against actual files
            indexed_files = set()
            results["files_analyzed"] = len(script_index.get("files", []))
            
            for file_info in script_index.get("files", []):
                file_path = os.path.normpath(file_info.get("path", ""))
                
                if file_path:
                    indexed_files.add(file_path)
                    
                    if self._file_exists_in_project(file_path, actual_files):
                        results["files_verified"] += 1
                    else:
                        results["files_missing"] += 1
                        results["missing_files"].append(file_path)
            
            # Check for new files not in index
            new_files = actual_files - indexed_files
            results["new_files"] = len(new_files)
            if new_files:
                results["new_file_paths"] = list(new_files)
            
            # Calculate percentages
            if results["files_analyzed"] > 0:
                results["verified_percentage"] = round(
                    results["files_verified"] / results["files_analyzed"] * 100, 2
                )
            
            # Overall status
            if results["files_missing"] > 0 or results["new_files"] > 0:
                results["status"] = "issues_found"
            
        except Exception as e:
            logger.error(f"Error validating script index: {str(e)}")
            results = {
                "status": "error",
                "message": f"Error validating script index: {str(e)}"
            }
        
        return results
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive validation report.
        
        Returns:
            Validation report
        """
        # Perform validations
        component_validation = self.validate_component_registry()
        script_validation = self.validate_script_index()
        
        # Generate report
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project_path": self.project_path,
            "component_registry_validation": component_validation,
            "script_index_validation": script_validation,
            "overall_status": "success"
        }
        
        # Determine overall status
        if component_validation.get("status") == "error" or script_validation.get("status") == "error":
            report["overall_status"] = "error"
        elif component_validation.get("status") == "issues_found" or script_validation.get("status") == "issues_found":
            report["overall_status"] = "issues_found"
        
        # Add recommendations
        report["recommendations"] = self._generate_recommendations(component_validation, script_validation)
        
        # Save report
        report_path = os.path.join(self.diagnostics_path, f"validation_report_{time.strftime('%Y%m%d_%H%M%S')}.json")
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Generated validation report at {report_path}")
        except Exception as e:
            logger.error(f"Error saving validation report: {str(e)}")
        
        return report
    
    def _find_python_files(self) -> List[str]:
        """Find all Python files in the project."""
        python_files = []
        
        for root, _, files in os.walk(self.project_path):
            # Skip .git, __pycache__, and .ai_reference directories
            if ".git" in root or "__pycache__" in root or ".ai_reference" in root:
                continue
            
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    python_files.append(os.path.normpath(file_path))
        
        return python_files
    
    def _extract_components_from_files(self, python_files: List[str]) -> Dict[str, Dict[str, Any]]:
        """Extract components from Python files."""
        components = {}
        
        for file_path in python_files:
            try:
                # Parse the file to extract components
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract classes and functions as components
                file_components = self._extract_components_from_content(content, file_path)
                
                # Add to overall components
                components.update(file_components)
                
            except Exception as e:
                logger.warning(f"Error extracting components from {file_path}: {str(e)}")
        
        return components
    
    def _extract_components_from_content(self, content: str, file_path: str) -> Dict[str, Dict[str, Any]]:
        """Extract components from file content."""
        components = {}
        
        try:
            # Simple parsing to extract classes and functions
            lines = content.split("\n")
            component_stack = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Check for class definitions
                if line.startswith("class ") and ":" in line:
                    class_name = line[6:line.find("(")].strip() if "(" in line else line[6:line.find(":")].strip()
                    components[class_name] = {
                        "type": "class",
                        "file": file_path,
                        "line": i + 1,
                        "dependencies": []
                    }
                    component_stack.append(class_name)
                
                # Check for function definitions
                elif line.startswith("def ") and ":" in line:
                    func_name = line[4:line.find("(")].strip()
                    
                    # Skip if it's a method of a class
                    if component_stack and components[component_stack[-1]]["type"] == "class":
                        # Add method to class component
                        pass
                    else:
                        components[func_name] = {
                            "type": "function",
                            "file": file_path,
                            "line": i + 1,
                            "dependencies": []
                        }
                        component_stack.append(func_name)
                
                # Check for import statements to extract dependencies
                elif line.startswith("import ") or line.startswith("from "):
                    if component_stack:
                        current_component = component_stack[-1]
                        
                        if line.startswith("import "):
                            imports = line[7:].split(",")
                            for imp in imports:
                                imp = imp.strip()
                                if "." in imp:
                                    imp = imp.split(".")[-1]
                                if imp and imp not in components[current_component]["dependencies"]:
                                    components[current_component]["dependencies"].append(imp)
                        
                        elif line.startswith("from ") and " import " in line:
                            from_part, import_part = line.split(" import ")
                            imports = import_part.split(",")
                            for imp in imports:
                                imp = imp.strip()
                                if imp and imp not in components[current_component]["dependencies"]:
                                    components[current_component]["dependencies"].append(imp)
        
        except Exception as e:
            logger.warning(f"Error parsing content from {file_path}: {str(e)}")
        
        return components
    
    def _paths_match(self, path1: str, path2: str) -> bool:
        """Check if two paths refer to the same file."""
        # Normalize paths
        path1 = os.path.normpath(path1)
        path2 = os.path.normpath(path2)
        
        # Try direct comparison
        if path1 == path2:
            return True
        
        # Try to find common path by removing the project_path prefix
        rel_path1 = path1.replace(self.project_path, "").lstrip(os.path.sep)
        rel_path2 = path2.replace(self.project_path, "").lstrip(os.path.sep)
        
        return rel_path1 == rel_path2
    
    def _file_exists_in_project(self, file_path: str, actual_files: Set[str]) -> bool:
        """Check if a file exists in the project."""
        # Direct match
        if file_path in actual_files:
            return True
        
        # Try to match normalized paths
        file_path = os.path.normpath(file_path)
        for actual_file in actual_files:
            if self._paths_match(file_path, actual_file):
                return True
        
        return False
    
    def _generate_recommendations(self, component_validation: Dict[str, Any], script_validation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Component registry recommendations
        if component_validation.get("status") == "issues_found":
            if component_validation.get("components_missing", 0) > 0:
                recommendations.append({
                    "type": "component_registry",
                    "severity": "high",
                    "issue": "missing_components",
                    "description": f"Found {component_validation.get('components_missing')} components in registry that no longer exist in the codebase.",
                    "recommendation": "Re-generate component registry to remove obsolete components."
                })
            
            if component_validation.get("components_outdated", 0) > 0:
                recommendations.append({
                    "type": "component_registry",
                    "severity": "medium",
                    "issue": "outdated_components",
                    "description": f"Found {component_validation.get('components_outdated')} components with outdated file paths.",
                    "recommendation": "Re-generate component registry to update file paths."
                })
            
            if component_validation.get("dependency_errors", 0) > 0:
                recommendations.append({
                    "type": "component_registry",
                    "severity": "medium",
                    "issue": "dependency_errors",
                    "description": f"Found {component_validation.get('dependency_errors')} components with incorrect dependency information.",
                    "recommendation": "Re-analyze dependencies to ensure accurate relationships."
                })
            
            if component_validation.get("new_components_count", 0) > 0:
                recommendations.append({
                    "type": "component_registry",
                    "severity": "medium",
                    "issue": "new_components",
                    "description": f"Found {component_validation.get('new_components_count')} new components in the codebase that are not in the registry.",
                    "recommendation": "Update component registry to include new components."
                })
        
        # Script index recommendations
        if script_validation.get("status") == "issues_found":
            if script_validation.get("files_missing", 0) > 0:
                recommendations.append({
                    "type": "script_index",
                    "severity": "high",
                    "issue": "missing_files",
                    "description": f"Found {script_validation.get('files_missing')} files in the index that no longer exist in the codebase.",
                    "recommendation": "Re-generate script index to remove obsolete file entries."
                })
            
            if script_validation.get("new_files", 0) > 0:
                recommendations.append({
                    "type": "script_index",
                    "severity": "medium",
                    "issue": "new_files",
                    "description": f"Found {script_validation.get('new_files')} new files in the codebase that are not in the index.",
                    "recommendation": "Update script index to include new files."
                })
        
        return recommendations

def validate_ai_librarian(project_path: str) -> Dict[str, Any]:
    """
    Validate the AI Librarian for a project.
    
    Args:
        project_path: The root directory of the project
        
    Returns:
        Validation report
    """
    validator = SelfValidator(project_path)
    return validator.generate_validation_report()
