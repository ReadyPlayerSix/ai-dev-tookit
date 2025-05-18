"""
Internal Advisors for AI Librarian

These tools act as Claude's "internal voice of reason" - providing
automatic guidance and best practices that Claude consults internally.
"""

import os
import json
from typing import Dict, Any, List

def register_internal_advisors(mcp):
    """Register internal advisor tools that Claude uses automatically."""
    
    @mcp.tool(internal=True)  # Mark as internal tool
    def code_safety_advisor(operation: str, file_path: str, changes: str) -> Dict[str, Any]:
        """
        Internal advisor that reviews code changes for safety and best practices.
        Claude consults this automatically before making file modifications.
        """
        warnings = []
        recommendations = []
        
        # Check for dangerous operations
        dangerous_patterns = [
            ("rm -rf", "Destructive command detected"),
            ("DELETE FROM", "Database deletion detected"),
            ("DROP TABLE", "Table destruction detected"),
            ("os.remove", "File deletion detected"),
            ("shutil.rmtree", "Directory deletion detected")
        ]
        
        for pattern, warning in dangerous_patterns:
            if pattern in changes:
                warnings.append(f"⚠️ {warning}")
                recommendations.append(f"Consider creating a backup before {operation}")
        
        # Check file type specific concerns
        if file_path.endswith('.env'):
            warnings.append("🔐 Modifying environment file - ensure no secrets are exposed")
            recommendations.append("Double-check that no API keys or passwords are being committed")
        
        if file_path.endswith(('requirements.txt', 'package.json', 'Gemfile')):
            warnings.append("📦 Dependency file modification")
            recommendations.append("Verify compatibility with existing code")
            recommendations.append("Consider running tests after changes")
        
        # Best practices
        if operation == "create" and not file_path.endswith('.md'):
            recommendations.append("Add appropriate file header comments")
            recommendations.append("Include necessary imports")
        
        return {
            "operation": operation,
            "file_path": file_path,
            "warnings": warnings,
            "recommendations": recommendations,
            "should_proceed": len(warnings) == 0,
            "require_confirmation": len(warnings) > 0,
            "internal_guidance": f"""
Before {operation} on {file_path}:
{chr(10).join(warnings)}
{chr(10).join(recommendations)}

Proceed with caution if warnings present.
"""
        }
    
    @mcp.tool(internal=True)
    def workflow_advisor(task_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal advisor that provides workflow guidance based on task type.
        Claude consults this when planning multi-step operations.
        """
        workflows = {
            "debugging": {
                "phases": ["identify", "reproduce", "diagnose", "fix", "test"],
                "tools_by_phase": {
                    "identify": ["query_component", "find_implementation"],
                    "reproduce": ["read_file", "create_edit_bookmark"],
                    "diagnose": ["get_related_files", "search_files"],
                    "fix": ["enhanced_edit_file", "update_bookmark"],
                    "test": ["run_tests", "sanity_check"]
                },
                "checkpoints": [
                    "After identifying: Confirm you understand the issue",
                    "After reproducing: Verify you can trigger the bug",
                    "After diagnosing: Explain the root cause",
                    "After fixing: Ensure no side effects",
                    "After testing: Confirm fix works"
                ]
            },
            "feature_implementation": {
                "phases": ["design", "implement", "test", "document"],
                "tools_by_phase": {
                    "design": ["query_component", "find_similar_implementations"],
                    "implement": ["enhanced_edit_file", "create_edit_bookmark"],
                    "test": ["create_test_file", "run_tests"],
                    "document": ["update_readme", "add_docstrings"]
                },
                "checkpoints": [
                    "After design: Get user approval on approach",
                    "After implement: Review code quality",
                    "After test: Ensure coverage is adequate",
                    "After document: Verify clarity"
                ]
            }
        }
        
        workflow = workflows.get(task_type, {})
        current_phase = context.get("current_phase", workflow.get("phases", ["unknown"])[0])
        
        return {
            "task_type": task_type,
            "current_phase": current_phase,
            "recommended_tools": workflow.get("tools_by_phase", {}).get(current_phase, []),
            "next_phase": workflow.get("phases", [])[(workflow.get("phases", []).index(current_phase) + 1) % len(workflow.get("phases", []))],
            "checkpoint": workflow.get("checkpoints", [])[workflow.get("phases", []).index(current_phase)] if current_phase in workflow.get("phases", []) else "",
            "internal_guidance": f"""
For {task_type} in {current_phase} phase:
- Use tools: {', '.join(workflow.get('tools_by_phase', {}).get(current_phase, []))}
- Checkpoint: {workflow.get('checkpoints', [])[workflow.get('phases', []).index(current_phase)] if current_phase in workflow.get('phases', []) else 'Verify progress'}
- Next phase: {workflow.get('phases', [])[(workflow.get('phases', []).index(current_phase) + 1) % len(workflow.get('phases', []))] if current_phase in workflow.get('phases', []) else 'Complete'}
"""
        }
    
    @mcp.tool(internal=True)
    def context_advisor(project_path: str, operation: str) -> Dict[str, Any]:
        """
        Internal advisor that maintains project context awareness.
        Helps Claude understand the project state before operations.
        """
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        has_librarian = os.path.exists(ai_ref_path)
        
        context_checks = []
        required_tools = []
        
        if not has_librarian:
            context_checks.append("Project not initialized with AI Librarian")
            required_tools.append("initialize_librarian")
        else:
            # Check last update time
            component_registry = os.path.join(ai_ref_path, "component_registry.json")
            if os.path.exists(component_registry):
                mod_time = os.path.getmtime(component_registry)
                if time.time() - mod_time > 3600:  # More than 1 hour old
                    context_checks.append("AI Librarian index may be stale")
                    required_tools.append("update_librarian")
        
        # Operation-specific checks
        if operation.startswith("refactor"):
            required_tools.extend(["create_edit_bookmark", "find_related_files"])
            context_checks.append("Consider impact on dependent files")
        
        if operation.startswith("debug"):
            required_tools.extend(["query_component", "get_diagnostic_info"])
            context_checks.append("Check error logs and diagnostic info")
        
        return {
            "project_path": project_path,
            "operation": operation,
            "has_ai_librarian": has_librarian,
            "context_checks": context_checks,
            "required_tools": required_tools,
            "internal_guidance": f"""
Before {operation} on {project_path}:
- Context: {', '.join(context_checks) if context_checks else 'Ready'}
- Required tools: {', '.join(required_tools)}
- AI Librarian: {'Initialized' if has_librarian else 'Not initialized'}

Ensure context is established before proceeding.
"""
        }
    
    @mcp.tool(internal=True)
    def quality_advisor(code_snippet: str, language: str) -> Dict[str, Any]:
        """
        Internal advisor that reviews code quality and suggests improvements.
        """
        quality_issues = []
        improvements = []
        
        # Language-specific checks
        if language == "python":
            if "except:" in code_snippet:
                quality_issues.append("Bare except clause detected")
                improvements.append("Use specific exception types")
            
            if "import *" in code_snippet:
                quality_issues.append("Wildcard import detected")
                improvements.append("Use explicit imports")
            
            if not any(line.strip().startswith('"""') or line.strip().startswith('#') for line in code_snippet.split('\n')):
                quality_issues.append("Missing documentation")
                improvements.append("Add docstrings and comments")
        
        # General checks
        lines = code_snippet.split('\n')
        for i, line in enumerate(lines):
            if len(line) > 120:
                quality_issues.append(f"Line {i+1} exceeds 120 characters")
                improvements.append(f"Break line {i+1} for readability")
        
        return {
            "language": language,
            "quality_score": max(0, 100 - len(quality_issues) * 10),
            "issues": quality_issues,
            "improvements": improvements,
            "internal_guidance": f"""
Code quality review:
- Score: {max(0, 100 - len(quality_issues) * 10)}/100
- Issues: {len(quality_issues)}
- Suggested improvements: {len(improvements)}

{chr(10).join(f'Fix: {imp}' for imp in improvements)}
"""
        }

def register_internal_advisor_system(mcp):
    """Register the complete internal advisor system."""
    register_internal_advisors(mcp)
    
    # Register a meta-advisor that coordinates other advisors
    @mcp.tool(internal=True)
    def meta_advisor(operation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta-advisor that coordinates other advisors based on the operation.
        This is Claude's primary internal consultation tool.
        """
        advisors_to_consult = []
        
        # Determine which advisors to consult
        if "file" in operation or "edit" in operation:
            advisors_to_consult.append("code_safety_advisor")
            advisors_to_consult.append("quality_advisor")
        
        if "debug" in operation or "feature" in operation:
            advisors_to_consult.append("workflow_advisor")
        
        if "project" in operation or "initialize" in operation:
            advisors_to_consult.append("context_advisor")
        
        return {
            "operation": operation,
            "advisors_consulted": advisors_to_consult,
            "guidance": f"Consult {', '.join(advisors_to_consult)} before proceeding with {operation}"
        }
    
    logger = logging.getLogger('ai-librarian')
    logger.info("Registered internal advisor system")