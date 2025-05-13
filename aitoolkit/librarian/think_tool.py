#!/usr/bin/env python3
"""
AI Dev Toolkit Think Tool

A dedicated tool for Claude to perform structured thinking and reflection.
This tool acts as a scratchpad where Claude can analyze complex problems,
verify requirements, and plan next steps without actually performing any
changes to the system.
"""

import os
import logging
from typing import Dict, Any, Optional

# Configure logger
logger = logging.getLogger("ai_librarian.think_tool")

def think(thought: str) -> str:
    """
    Process a thought or reflection.
    
    This tool provides a structured way for Claude to think through complex problems.
    It functions as a scratchpad that helps break down tasks, verify requirements,
    perform rule checking, and plan next steps.
    
    Unlike other tools, the think tool doesn't actually modify anything or perform
    any external actions - it simply returns the thought that was passed to it,
    formatted in a way that makes reflection clear and separate from regular
    conversation with the user.
    
    Example use cases:
    - Breaking down complex tasks into steps
    - Verifying that all requirements are met before taking action
    - Checking if planned actions comply with policies or constraints
    - Analyzing the results of other tools to verify correctness
    
    Args:
        thought: The thought or reflection to process
        
    Returns:
        The formatted thought or reflection
    """
    logger.info("Processing thought with think tool")
    
    # Log the thought for debugging purposes
    formatted_thought = f"<reflection>\n{thought}\n</reflection>"
    
    # Return the thought as-is, but formatted to make it clear it's a reflection
    return formatted_thought

def think_with_template(template_type: str, **kwargs) -> str:
    """
    Use a structured template for thinking through specific problem types.
    
    This is an enhanced version of the think tool that provides structured
    templates for common reflection patterns.
    
    Args:
        template_type: The type of template to use (requirements, rules, action_plan, etc.)
        **kwargs: Template-specific parameters
        
    Returns:
        Formatted thought using the specified template
    """
    logger.info(f"Using think template: {template_type}")
    
    if template_type == "requirements":
        # Template for checking if all requirements are met
        requirements = kwargs.get("requirements", [])
        provided = kwargs.get("provided", [])
        missing = [req for req in requirements if req not in provided]
        
        thought = "## Requirements Check\n\n"
        thought += "### Required Information\n"
        for req in requirements:
            status = "✓" if req in provided else "✗"
            thought += f"- {status} {req}\n"
        
        thought += "\n### Missing Information\n"
        if missing:
            for item in missing:
                thought += f"- {item}\n"
        else:
            thought += "- All required information collected\n"
        
    elif template_type == "rule_check":
        # Template for checking if an action complies with rules
        rules = kwargs.get("rules", [])
        action = kwargs.get("action", "")
        
        thought = f"## Rule Compliance Check for: {action}\n\n"
        thought += "### Applicable Rules\n"
        for rule in rules:
            thought += f"- {rule}\n"
            
        thought += "\n### Compliance Analysis\n"
        # The analysis would be provided by the caller
        thought += kwargs.get("analysis", "")
        
    elif template_type == "action_plan":
        # Template for planning a series of actions
        goal = kwargs.get("goal", "")
        steps = kwargs.get("steps", [])
        
        thought = f"## Action Plan for: {goal}\n\n"
        thought += "### Planned Steps\n"
        for i, step in enumerate(steps, 1):
            thought += f"{i}. {step}\n"
            
        thought += "\n### Potential Issues\n"
        thought += kwargs.get("issues", "- None identified\n")
        
    else:
        # Default to a general reflection
        thought = f"## {template_type.title()} Reflection\n\n"
        thought += kwargs.get("content", "")
    
    return think(thought)

def think_about_code(code: str, objective: str) -> str:
    """
    Reflect on code snippets with a specific objective in mind.
    
    Args:
        code: The code snippet to analyze
        objective: What aspect of the code to think about (bugs, improvements, etc.)
        
    Returns:
        Formatted thought about the code
    """
    logger.info(f"Thinking about code with objective: {objective}")
    
    thought = f"## Code Analysis: {objective}\n\n"
    thought += "```\n"
    thought += code
    thought += "\n```\n\n"
    
    thought += "### Initial Observations\n"
    thought += "- This code needs to be analyzed for: " + objective + "\n"
    thought += "- I'll examine it systematically to address this objective\n"
    
    thought += "\n### Analysis\n"
    thought += "- The analysis would be provided by Claude's reasoning\n"
    
    return think(thought)

# Additional specialized think functions can be added here for different contexts