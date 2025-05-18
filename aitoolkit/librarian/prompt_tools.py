"""
Prompt Tools for AI Librarian

These tools provide prompt-like guidance for common tasks.
Unlike MCP prompts, these are tools that return structured instructions.
"""

import os
import json
from typing import Dict, Any

def register_prompt_tools(mcp):
    """Register tools that provide prompt-like guidance."""
    
    @mcp.tool()
    def get_debugging_guide(project_path: str, issue_description: str) -> Dict[str, Any]:
        """
        Get a structured debugging guide for an issue.
        
        This tool analyzes the project context and returns specific debugging steps.
        """
        # Check if project has AI Librarian initialized
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        has_librarian = os.path.exists(ai_ref_path)
        
        steps = []
        
        if has_librarian:
            steps.extend([
                "1. Use `query_component` to find relevant components",
                "2. Use `find_implementation` to locate the specific code",
                "3. Create edit bookmarks for the problematic sections",
                "4. Use `get_related_files` to find connected code"
            ])
        else:
            steps.extend([
                "1. Initialize AI Librarian with `initialize_librarian`",
                "2. Then follow the debugging steps above"
            ])
        
        steps.extend([
            "5. Add debug logging to trace the issue",
            "6. Use `enhanced_edit_file` to make targeted fixes",
            "7. Test the changes",
            "8. Document the fix"
        ])
        
        return {
            "project": project_path,
            "issue": issue_description,
            "has_ai_librarian": has_librarian,
            "debugging_steps": steps,
            "suggested_tools": [
                "query_component",
                "find_implementation", 
                "create_edit_bookmark",
                "enhanced_edit_file",
                "get_related_files"
            ],
            "prompt": f"""I'll help you debug this issue: {issue_description}

Let me start by analyzing the codebase structure and finding the relevant components.

{chr(10).join(steps)}

Would you like me to start with step 1?"""
        }
    
    @mcp.tool()
    def get_refactoring_guide(project_path: str, target_code: str, refactor_type: str = "general") -> Dict[str, Any]:
        """
        Get a structured guide for refactoring code.
        
        Args:
            project_path: Path to the project
            target_code: Description of code to refactor (file, function, class, etc.)
            refactor_type: Type of refactoring (general, performance, readability, testability)
        """
        refactor_strategies = {
            "general": [
                "Extract common functionality into utilities",
                "Reduce coupling between components",
                "Apply SOLID principles",
                "Remove code duplication"
            ],
            "performance": [
                "Identify bottlenecks with profiling",
                "Cache expensive computations",
                "Optimize data structures",
                "Reduce I/O operations"
            ],
            "readability": [
                "Use descriptive variable names",
                "Break complex functions into smaller ones",
                "Add type hints",
                "Improve documentation"
            ],
            "testability": [
                "Extract dependencies for injection",
                "Create interfaces for mocking",
                "Separate business logic from I/O",
                "Make functions pure where possible"
            ]
        }
        
        strategies = refactor_strategies.get(refactor_type, refactor_strategies["general"])
        
        return {
            "project": project_path,
            "target": target_code,
            "refactor_type": refactor_type,
            "strategies": strategies,
            "workflow": [
                f"1. Analyze {target_code} using AI Librarian tools",
                "2. Create bookmarks for sections to refactor",
                "3. Apply refactoring strategies:",
                *[f"   - {s}" for s in strategies],
                "4. Update tests to cover changes",
                "5. Verify functionality remains intact"
            ],
            "prompt": f"""I'll help you refactor {target_code} for better {refactor_type}.

Here's my recommended approach:
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(strategies)])}

Let's start by analyzing the current implementation. Would you like me to proceed?"""
        }
    
    @mcp.tool()
    def get_feature_implementation_guide(project_path: str, feature_description: str) -> Dict[str, Any]:
        """
        Get a structured guide for implementing a new feature.
        """
        return {
            "project": project_path,
            "feature": feature_description,
            "implementation_phases": {
                "analysis": [
                    "Understand requirements",
                    "Find similar existing features",
                    "Identify integration points"
                ],
                "design": [
                    "Design the API/interface",
                    "Plan the data model",
                    "Consider edge cases"
                ],
                "implementation": [
                    "Create the core functionality",
                    "Add error handling",
                    "Implement data validation"
                ],
                "testing": [
                    "Write unit tests",
                    "Add integration tests",
                    "Test edge cases"
                ],
                "documentation": [
                    "Add code documentation",
                    "Update README if needed",
                    "Create usage examples"
                ]
            },
            "prompt": f"""I'll help you implement: {feature_description}

Let's break this down into phases:

1. **Analysis Phase**
   - Search for similar patterns in the codebase
   - Identify where this feature should live
   - Understand dependencies

2. **Design Phase**
   - Design the interface
   - Plan the implementation

3. **Implementation Phase**
   - Write the code using enhanced_edit_file
   - Create bookmarks for complex sections

4. **Testing Phase**
   - Add comprehensive tests

5. **Documentation Phase**
   - Document the feature

Which phase would you like to start with?"""
        }
    
    @mcp.tool()
    def get_analysis_guide(project_path: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        Get a structured guide for analyzing a codebase.
        
        Args:
            project_path: Path to the project
            analysis_type: Type of analysis (general, architecture, dependencies, security)
        """
        analysis_focus = {
            "general": {
                "focus": "Overall project structure and patterns",
                "tools": ["initialize_librarian", "query_component", "find_implementation"],
                "checks": ["Project structure", "Core components", "Design patterns", "Code quality"]
            },
            "architecture": {
                "focus": "Architectural patterns and design decisions",
                "tools": ["get_related_files", "query_component"],
                "checks": ["Layer separation", "Component coupling", "Design patterns", "Scalability"]
            },
            "dependencies": {
                "focus": "External and internal dependencies",
                "tools": ["find_implementation", "search_files"],
                "checks": ["External libraries", "Circular dependencies", "Version compatibility", "Unused dependencies"]
            },
            "security": {
                "focus": "Security vulnerabilities and best practices",
                "tools": ["search_files", "enhanced_edit_file"],
                "checks": ["Input validation", "Authentication", "Authorization", "Sensitive data handling"]
            }
        }
        
        config = analysis_focus.get(analysis_type, analysis_focus["general"])
        
        return {
            "project": project_path,
            "analysis_type": analysis_type,
            "focus": config["focus"],
            "recommended_tools": config["tools"],
            "checklist": config["checks"],
            "prompt": f"""I'll analyze the {analysis_type} aspects of this project.

Focus: {config['focus']}

Analysis checklist:
{chr(10).join([f"- {check}" for check in config['checks']])}

I'll use these tools:
{chr(10).join([f"- {tool}" for tool in config['tools']])}

Would you like me to begin the analysis?"""
        }

def register_prompt_like_tools(mcp):
    """Register all prompt-like tools."""
    register_prompt_tools(mcp)
    
    logger = logging.getLogger('ai-librarian')
    logger.info("Registered prompt-like guidance tools")