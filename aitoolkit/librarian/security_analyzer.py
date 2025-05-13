#!/usr/bin/env python3
"""
AI Dev Toolkit Security Analyzer

This module provides comprehensive code security analysis for detecting potential
vulnerabilities, security risks, and code quality issues in development projects.
It generates professional-level assessment reports without suggesting fixes or
implementations, only identifying issues and their severity.
"""

import os
import sys
import re
import ast
import json
import logging
import importlib
import subprocess
from enum import Enum
from typing import Dict, List, Set, Tuple, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("security_analyzer")

class SeverityLevel(Enum):
    """Severity levels for security issues"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1

@dataclass
class SecurityIssue:
    """Represents a security issue found in the codebase"""
    issue_id: str
    severity: SeverityLevel
    category: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    snippet: Optional[str] = None
    cwe_id: Optional[str] = None  # Common Weakness Enumeration ID
    additional_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityReport:
    """Comprehensive security report for a project"""
    project_path: str
    timestamp: str
    issues: List[SecurityIssue] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    scan_info: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def critical_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == SeverityLevel.CRITICAL)
    
    @property
    def high_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == SeverityLevel.HIGH)
    
    @property
    def medium_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == SeverityLevel.MEDIUM)
    
    @property
    def low_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == SeverityLevel.LOW)
    
    @property
    def info_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == SeverityLevel.INFO)
    
    @property
    def total_count(self) -> int:
        return len(self.issues)
    
    @property
    def has_critical_issues(self) -> bool:
        return self.critical_count > 0

class SecurityAnalyzer:
    """
    Analyzes code for security vulnerabilities and generates comprehensive reports.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the security analyzer.
        
        Args:
            project_path: Path to the project root directory
        """
        self.project_path = os.path.abspath(project_path)
        self.report = SecurityReport(
            project_path=project_path,
            timestamp=self._get_timestamp(),
            scan_info={
                "analyzer_version": "1.0.0",
                "platform": sys.platform,
                "python_version": sys.version
            }
        )
        
        # Directories to exclude from scanning
        self.exclude_dirs = [
            ".git",
            "__pycache__",
            "venv",
            ".venv",
            "env",
            "node_modules",
            ".ai_reference",
            "dist",
            "build"
        ]
        
        # Known vulnerability patterns by category
        self.vulnerability_patterns = {
            "injection": [
                (r"subprocess\.call\s*\([^)]*shell\s*=\s*True", "Shell injection risk", SeverityLevel.HIGH),
                (r"eval\s*\([^\)]+\)", "Code injection risk with eval()", SeverityLevel.CRITICAL),
                (r"exec\s*\([^\)]+\)", "Code injection risk with exec()", SeverityLevel.CRITICAL),
                (r"os\.system\s*\(", "Command injection risk with os.system()", SeverityLevel.HIGH),
                (r"cursor\.execute\s*\([^,)]*%|cursor\.execute\s*\([^,)]*\+", "SQL injection risk", SeverityLevel.HIGH),
                (r"\.format\s*\([^\)]*__[^\)]", "Format string injection risk", SeverityLevel.MEDIUM)
            ],
            "hardcoded_secrets": [
                (r"password\s*=\s*[\"'][^\"']+[\"']", "Possible hardcoded password", SeverityLevel.HIGH),
                (r"api_key\s*=\s*[\"'][^\"']+[\"']", "Possible hardcoded API key", SeverityLevel.HIGH),
                (r"secret\s*=\s*[\"'][^\"']+[\"']", "Possible hardcoded secret", SeverityLevel.HIGH),
                (r"token\s*=\s*[\"'][^\"']+[\"']", "Possible hardcoded token", SeverityLevel.HIGH),
                (r"-----BEGIN\s+PRIVATE\s+KEY-----", "Private key in code", SeverityLevel.CRITICAL)
            ],
            "insecure_operations": [
                (r"pickle\.load", "Insecure deserialization with pickle", SeverityLevel.HIGH),
                (r"yaml\.load\s*\([^,)]*Loader\s*=\s*None|yaml\.load\s*\([^,)]*Loader\s*=\s*yaml\.Loader", "Insecure YAML parsing", SeverityLevel.MEDIUM),
                (r"hashlib\.md5\s*\(|hashlib\.sha1\s*\(", "Weak cryptographic hash", SeverityLevel.MEDIUM),
                (r"random\.", "Non-cryptographic random number generator", SeverityLevel.LOW),
                (r"verify\s*=\s*False", "SSL certificate verification disabled", SeverityLevel.HIGH)
            ],
            "access_control": [
                (r"chmod\s*\(\s*[^,]+\s*,\s*0777", "Overly permissive file permissions", SeverityLevel.MEDIUM),
                (r"(?:ctx\.)?set_cookie\((?![^)]*secure=True)", "Cookie without secure flag", SeverityLevel.MEDIUM),
                (r"(?:ctx\.)?set_cookie\((?![^)]*httponly=True)", "Cookie without HttpOnly flag", SeverityLevel.MEDIUM),
                (r"@app\.route\([^)]*methods\s*=\s*\[\s*['\"]GET['\"]\s*,\s*['\"]POST['\"]", "Potentially insecure HTTP method handling", SeverityLevel.LOW)
            ],
            "error_handling": [
                (r"except\s*:", "Bare except clause", SeverityLevel.MEDIUM),
                (r"except\s+Exception\s*:", "Too broad exception handling", SeverityLevel.LOW),
                (r"print\s*\([^\)]*traceback", "Printing traceback information", SeverityLevel.LOW),
                (r"traceback\.print_exc\s*\(", "Printing exception traceback", SeverityLevel.LOW)
            ],
            "data_exposure": [
                (r"\.write\s*\([^)]*error|\.write\s*\([^)]*exception", "Potential sensitive data exposure in error output", SeverityLevel.MEDIUM),
                (r"DEBUG\s*=\s*True", "Debug mode enabled", SeverityLevel.MEDIUM),
                (r"json\.dumps\s*\([^)]*indent", "Pretty-printed JSON potentially exposing sensitive data", SeverityLevel.LOW)
            ],
            "networking": [
                (r"socket\.", "Raw socket usage", SeverityLevel.LOW),
                (r"bind\s*\(\s*['\"]0\.0\.0\.0['\"]\s*[,)]", "Binding to all network interfaces", SeverityLevel.MEDIUM),
                (r"open_redirect", "Potential open redirect vulnerability", SeverityLevel.MEDIUM)
            ],
            "file_operations": [
                (r"open\s*\([^,)]*[\"']w[\"']|open\s*\([^,)]*[\"']a[\"']", "File write operation", SeverityLevel.LOW),
                (r"shutil\.rmtree", "Directory removal operation", SeverityLevel.MEDIUM),
                (r"os\.remove|os\.unlink", "File deletion operation", SeverityLevel.LOW),
                (r"__file__", "File path reference", SeverityLevel.INFO)
            ],
            "ai_specific": [
                (r"skip_validation|bypass_check|no_verify", "Input validation potentially bypassed", SeverityLevel.MEDIUM),
                (r"allow_all|permit_all", "Potentially overly permissive access control", SeverityLevel.MEDIUM),
                (r"\.get\s*\([^)]*\)", "Dictionary access without key validation", SeverityLevel.LOW),
                (r"jailbreak|break_constraints|bypass", "Potential AI constraint bypass", SeverityLevel.HIGH)
            ]
        }
        
        # Additional patterns for the AI Dev Toolkit specifically
        self.toolkit_specific_patterns = {
            "filesystem_access": [
                (r"os\.path\.join\s*\([^)]*user_input", "Path traversal vulnerability with user input", SeverityLevel.HIGH),
                (r"validate_path|check_path", "Path validation function - verify implementation", SeverityLevel.MEDIUM),
                (r"allowed_dirs|permitted_paths", "Directory access control - verify implementation", SeverityLevel.MEDIUM),
                (r"\.\.\/|\.\.\\", "Directory traversal sequence", SeverityLevel.HIGH)
            ],
            "mcp_security": [
                (r"mcp\.tool\s*\(\)|@mcp\.tool", "MCP tool registration - verify proper input validation", SeverityLevel.MEDIUM),
                (r"mcp\.resource\s*\(", "MCP resource registration - verify proper input validation", SeverityLevel.MEDIUM),
                (r"execute_tool|run_tool", "Dynamic tool execution - verify proper input validation", SeverityLevel.HIGH)
            ],
            "context_handling": [
                (r"context\[", "Context dictionary access - verify key validation", SeverityLevel.LOW),
                (r"global_context|shared_context", "Global/shared context access - verify thread safety", SeverityLevel.MEDIUM),
                (r"context\.update\s*\(", "Context update - verify proper validation", SeverityLevel.MEDIUM)
            ]
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def analyze_project(self) -> SecurityReport:
        """
        Perform a comprehensive security analysis of the project.
        
        Returns:
            SecurityReport containing analysis results
        """
        logger.info(f"Starting security analysis of {self.project_path}")
        
        # Track metrics
        self.report.metrics = {
            "files_analyzed": 0,
            "lines_analyzed": 0,
            "patterns_checked": sum(len(patterns) for patterns in 
                                  list(self.vulnerability_patterns.values()) + 
                                  list(self.toolkit_specific_patterns.values()))
        }
        
        # Analyze Python files
        self._analyze_python_files()
        
        # Analyze configuration files
        self._analyze_config_files()
        
        # Process results for summary
        self._generate_summary()
        
        # Log completion
        logger.info(f"Security analysis complete. Found {len(self.report.issues)} potential issues.")
        logger.info(f"Critical: {self.report.critical_count}, High: {self.report.high_count}, " +
                   f"Medium: {self.report.medium_count}, Low: {self.report.low_count}, Info: {self.report.info_count}")
        
        return self.report
    
    def _analyze_python_files(self):
        """Analyze all Python files in the project"""
        logger.info("Analyzing Python files...")
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.project_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                            
                        # Track metrics
                        self.report.metrics["files_analyzed"] += 1
                        self.report.metrics["lines_analyzed"] += content.count('\n') + 1
                        
                        # Check general vulnerability patterns
                        for category, patterns in self.vulnerability_patterns.items():
                            for pattern, description, severity in patterns:
                                self._check_pattern(file_path, content, pattern, description, severity, category)
                        
                        # Check toolkit-specific patterns
                        for category, patterns in self.toolkit_specific_patterns.items():
                            for pattern, description, severity in patterns:
                                self._check_pattern(file_path, content, pattern, description, severity, category)
                        
                        # Perform AST-based analysis for more sophisticated checks
                        try:
                            tree = ast.parse(content)
                            self._analyze_ast(file_path, tree)
                        except SyntaxError as e:
                            # Record syntax error as a code quality issue
                            self._add_issue(
                                file_path=file_path,
                                line_number=e.lineno,
                                severity=SeverityLevel.HIGH,
                                category="code_quality",
                                description=f"Syntax error: {e}",
                                snippet=e.text.strip() if e.text else None
                            )
                    
                    except Exception as e:
                        logger.warning(f"Error analyzing {rel_path}: {e}")
                        # Record as an issue if we can't analyze a file
                        self._add_issue(
                            file_path=file_path,
                            severity=SeverityLevel.LOW,
                            category="analysis_error",
                            description=f"File analysis error: {str(e)}"
                        )
    
    def _analyze_config_files(self):
        """Analyze configuration files for security issues"""
        logger.info("Analyzing configuration files...")
        
        # Define patterns for different config file types
        config_patterns = {
            ".json": {
                "debug": (r"\"debug\"\s*:\s*true", "Debug mode enabled in JSON config", SeverityLevel.MEDIUM),
                "credentials": (r"\"(password|secret|token|key)\"\s*:\s*\"[^\"]+\"", "Possible credentials in JSON config", SeverityLevel.HIGH),
                "insecure_settings": (r"\"verify\"\s*:\s*false", "SSL verification disabled in JSON config", SeverityLevel.HIGH)
            },
            ".yaml": {
                "debug": (r"debug:\s*true", "Debug mode enabled in YAML config", SeverityLevel.MEDIUM),
                "credentials": (r"(password|secret|token|key):\s*['\"]?[^'\"\n]+['\"]?", "Possible credentials in YAML config", SeverityLevel.HIGH),
                "insecure_settings": (r"verify:\s*false", "SSL verification disabled in YAML config", SeverityLevel.HIGH)
            },
            ".ini": {
                "debug": (r"debug\s*=\s*true", "Debug mode enabled in INI config", SeverityLevel.MEDIUM),
                "credentials": (r"(password|secret|token|key)\s*=\s*[^\n]+", "Possible credentials in INI config", SeverityLevel.HIGH),
                "insecure_settings": (r"verify\s*=\s*false", "SSL verification disabled in INI config", SeverityLevel.HIGH)
            }
        }
        
        # Find and analyze config files
        for root, dirs, files in os.walk(self.project_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check if this is a config file we should analyze
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in config_patterns and not file.startswith('.'):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                        
                        # Track metrics
                        self.report.metrics["files_analyzed"] += 1
                        self.report.metrics["lines_analyzed"] += content.count('\n') + 1
                        
                        # Check patterns for this config file type
                        for check_name, (pattern, description, severity) in config_patterns[file_ext].items():
                            self._check_pattern(file_path, content, pattern, description, severity, "configuration")
                    
                    except Exception as e:
                        logger.warning(f"Error analyzing config file {file}: {e}")
                
                # Special handling for MCP server config
                if file == "claude_desktop_config.json":
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                            
                        # Parse JSON
                        try:
                            config = json.loads(content)
                            
                            # Check MCP server configuration
                            if "mcpServers" in config:
                                for server_name, server_config in config["mcpServers"].items():
                                    # Check for proper allowed directories configuration
                                    if "env" not in server_config or "AI_LIBRARIAN_ALLOWED_DIRS" not in server_config.get("env", {}):
                                        self._add_issue(
                                            file_path=file_path,
                                            severity=SeverityLevel.HIGH,
                                            category="mcp_security",
                                            description=f"MCP server '{server_name}' may not have properly restricted directory access"
                                        )
                                    
                                    # Check for proper command validation
                                    if "command" in server_config and server_config["command"] not in ["python", "python3"]:
                                        self._add_issue(
                                            file_path=file_path,
                                            severity=SeverityLevel.MEDIUM,
                                            category="mcp_security",
                                            description=f"MCP server '{server_name}' uses non-standard command: {server_config['command']}"
                                        )
                        except json.JSONDecodeError as e:
                            self._add_issue(
                                file_path=file_path,
                                severity=SeverityLevel.MEDIUM,
                                category="configuration",
                                description=f"Invalid JSON in Claude Desktop config: {e}"
                            )
                    except Exception as e:
                        logger.warning(f"Error analyzing Claude Desktop config: {e}")
    
    def _analyze_ast(self, file_path: str, tree: ast.AST):
        """
        Perform AST-based security analysis.
        
        Args:
            file_path: Path to the file being analyzed
            tree: AST of the file
        """
        # Check for security-relevant imports
        imports_checker = ImportSecurityVisitor(file_path)
        imports_checker.visit(tree)
        self.report.issues.extend(imports_checker.issues)
        
        # Check for dangerous function calls
        call_checker = FunctionCallSecurityVisitor(file_path)
        call_checker.visit(tree)
        self.report.issues.extend(call_checker.issues)
        
        # Check for dangerous variable assignments
        assignment_checker = AssignmentSecurityVisitor(file_path)
        assignment_checker.visit(tree)
        self.report.issues.extend(assignment_checker.issues)
    
    def _check_pattern(self, file_path: str, content: str, pattern: str, description: str, severity: SeverityLevel, category: str):
        """
        Check for a specific pattern in file content.
        
        Args:
            file_path: Path to the file being analyzed
            content: Content of the file
            pattern: Regex pattern to search for
            description: Description of the issue
            severity: Severity level of the issue
            category: Category of the issue
        """
        matches = re.finditer(pattern, content)
        for match in matches:
            # Get line number and snippet
            line_number = content[:match.start()].count('\n') + 1
            line_start = content.rfind('\n', 0, match.start()) + 1
            line_end = content.find('\n', match.end())
            if line_end == -1:
                line_end = len(content)
            
            snippet = content[line_start:line_end].strip()
            
            # Add the issue
            self._add_issue(
                file_path=file_path,
                line_number=line_number,
                severity=severity,
                category=category,
                description=description,
                snippet=snippet
            )
    
    def _add_issue(self, file_path: str, severity: SeverityLevel, category: str, description: str,
                 line_number: Optional[int] = None, snippet: Optional[str] = None, cwe_id: Optional[str] = None):
        """
        Add an issue to the report.
        
        Args:
            file_path: Path to the file with the issue
            severity: Severity level of the issue
            category: Category of the issue
            description: Description of the issue
            line_number: Line number of the issue (optional)
            snippet: Code snippet containing the issue (optional)
            cwe_id: CWE ID for the issue (optional)
        """
        # Generate a unique issue ID
        issue_id = f"SEC-{len(self.report.issues) + 1:04d}"
        
        # Get relative path for reporting
        rel_path = os.path.relpath(file_path, self.project_path)
        
        # Create and add the issue
        issue = SecurityIssue(
            issue_id=issue_id,
            severity=severity,
            category=category,
            description=description,
            file_path=rel_path,
            line_number=line_number,
            snippet=snippet,
            cwe_id=cwe_id
        )
        
        self.report.issues.append(issue)
    
    def _generate_summary(self):
        """Generate summary statistics for the report"""
        # Group issues by category
        category_counts = {}
        for issue in self.report.issues:
            if issue.category not in category_counts:
                category_counts[issue.category] = {
                    "total": 0,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "info": 0
                }
            
            category_counts[issue.category]["total"] += 1
            
            if issue.severity == SeverityLevel.CRITICAL:
                category_counts[issue.category]["critical"] += 1
            elif issue.severity == SeverityLevel.HIGH:
                category_counts[issue.category]["high"] += 1
            elif issue.severity == SeverityLevel.MEDIUM:
                category_counts[issue.category]["medium"] += 1
            elif issue.severity == SeverityLevel.LOW:
                category_counts[issue.category]["low"] += 1
            elif issue.severity == SeverityLevel.INFO:
                category_counts[issue.category]["info"] += 1
        
        # Create summary
        self.report.summary = {
            "total_issues": len(self.report.issues),
            "critical_issues": self.report.critical_count,
            "high_issues": self.report.high_count,
            "medium_issues": self.report.medium_count,
            "low_issues": self.report.low_count,
            "info_issues": self.report.info_count,
            "categories": category_counts,
            "risk_level": self._calculate_risk_level()
        }
    
    def _calculate_risk_level(self) -> str:
        """Calculate overall risk level based on issue counts"""
        if self.report.critical_count > 0:
            return "Critical"
        elif self.report.high_count > 3:
            return "High"
        elif self.report.high_count > 0 or self.report.medium_count > 5:
            return "Medium"
        elif self.report.medium_count > 0 or self.report.low_count > 0:
            return "Low"
        else:
            return "Minimal"
    
    def generate_text_report(self) -> str:
        """
        Generate a formatted text report of the security analysis results.
        
        Returns:
            Formatted report text
        """
        # Ensure we have analysis results
        if not self.report.issues and not hasattr(self.report, 'summary'):
            self.analyze_project()
        
        report_lines = []
        report_lines.append("# Security Analysis Report")
        report_lines.append("")
        
        # Executive summary
        report_lines.append("## Executive Summary")
        report_lines.append("")
        report_lines.append(f"Project: {self.report.project_path}")
        report_lines.append(f"Scan Date: {self.report.timestamp}")
        report_lines.append(f"Overall Risk Level: **{self.report.summary['risk_level']}**")
        report_lines.append("")
        report_lines.append("### Key Findings")
        report_lines.append("")
        report_lines.append(f"- **{self.report.summary['total_issues']}** total issues identified")
        report_lines.append(f"- **{self.report.critical_count}** critical severity issues")
        report_lines.append(f"- **{self.report.high_count}** high severity issues")
        report_lines.append(f"- **{self.report.medium_count}** medium severity issues")
        report_lines.append(f"- **{self.report.low_count}** low severity issues")
        report_lines.append(f"- **{self.report.info_count}** informational findings")
        report_lines.append("")
        
        # Issues by category
        report_lines.append("### Issues by Category")
        report_lines.append("")
        report_lines.append("| Category | Critical | High | Medium | Low | Info | Total |")
        report_lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        
        for category, counts in self.report.summary["categories"].items():
            report_lines.append(f"| {category} | {counts['critical']} | {counts['high']} | {counts['medium']} | {counts['low']} | {counts['info']} | {counts['total']} |")
        
        report_lines.append("")
        
        # Scan metrics
        report_lines.append("### Scan Coverage")
        report_lines.append("")
        report_lines.append(f"- Files analyzed: **{self.report.metrics['files_analyzed']}**")
        report_lines.append(f"- Lines of code analyzed: **{self.report.metrics['lines_analyzed']}**")
        report_lines.append(f"- Security patterns checked: **{self.report.metrics['patterns_checked']}**")
        report_lines.append("")
        
        # Critical and high issues detail
        if self.report.critical_count > 0 or self.report.high_count > 0:
            report_lines.append("## Critical and High Severity Issues")
            report_lines.append("")
            
            for issue in self.report.issues:
                if issue.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
                    report_lines.append(f"### {issue.issue_id}: {issue.description}")
                    report_lines.append("")
                    report_lines.append(f"**Severity**: {issue.severity.name}")
                    report_lines.append(f"**Category**: {issue.category}")
                    if issue.cwe_id:
                        report_lines.append(f"**CWE**: {issue.cwe_id}")
                    report_lines.append(f"**File**: {issue.file_path}")
                    if issue.line_number:
                        report_lines.append(f"**Line**: {issue.line_number}")
                    if issue.snippet:
                        report_lines.append("")
                        report_lines.append("```")
                        report_lines.append(issue.snippet)
                        report_lines.append("```")
                    report_lines.append("")
            
            report_lines.append("")
        
        # All issues table
        report_lines.append("## All Identified Issues")
        report_lines.append("")
        report_lines.append("| ID | Severity | Category | Description | File | Line |")
        report_lines.append("| --- | --- | --- | --- | --- | --- |")
        
        for issue in sorted(self.report.issues, key=lambda x: (x.severity.value, x.category), reverse=True):
            line = issue.line_number if issue.line_number else "-"
            report_lines.append(f"| {issue.issue_id} | {issue.severity.name} | {issue.category} | {issue.description} | {issue.file_path} | {line} |")
        
        return "\n".join(report_lines)
        

class ImportSecurityVisitor(ast.NodeVisitor):
    """AST visitor that checks imports for security issues"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues = []
        
        # Potentially dangerous modules
        self.dangerous_imports = {
            "pickle": (SeverityLevel.HIGH, "insecure_operations", "Importing pickle module (insecure deserialization risk)", "CWE-502"),
            "marshal": (SeverityLevel.HIGH, "insecure_operations", "Importing marshal module (insecure deserialization risk)", "CWE-502"),
            "shelve": (SeverityLevel.MEDIUM, "insecure_operations", "Importing shelve module (uses pickle internally)", "CWE-502"),
            "subprocess": (SeverityLevel.MEDIUM, "injection", "Importing subprocess module (potential command injection risk)", "CWE-78"),
            "os.system": (SeverityLevel.MEDIUM, "injection", "Importing os.system (potential command injection risk)", "CWE-78"),
            "ftplib": (SeverityLevel.MEDIUM, "networking", "Importing ftplib (unencrypted protocol risk)", "CWE-319"),
            "telnetlib": (SeverityLevel.HIGH, "networking", "Importing telnetlib (unencrypted protocol risk)", "CWE-319"),
            "smtplib": (SeverityLevel.LOW, "networking", "Importing smtplib (email functionality)", None),
            "xml.etree.ElementTree": (SeverityLevel.MEDIUM, "insecure_operations", "Importing ElementTree (potential XXE vulnerability)", "CWE-611"),
            "lxml.etree": (SeverityLevel.MEDIUM, "insecure_operations", "Importing lxml.etree (potential XXE vulnerability)", "CWE-611"),
            "eval": (SeverityLevel.CRITICAL, "injection", "Importing eval (code execution risk)", "CWE-95"),
            "exec": (SeverityLevel.CRITICAL, "injection", "Importing exec (code execution risk)", "CWE-95")
        }
    
    def visit_Import(self, node):
        """Process import statements"""
        for name in node.names:
            if name.name in self.dangerous_imports:
                severity, category, description, cwe = self.dangerous_imports[name.name]
                self._add_issue(node.lineno, severity, category, description, cwe)
        
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Process from X import Y statements"""
        # Check the module being imported from
        if node.module in self.dangerous_imports:
            severity, category, description, cwe = self.dangerous_imports[node.module]
            self._add_issue(node.lineno, severity, category, description, cwe)
        
        # Check specific imports
        for name in node.names:
            full_import = f"{node.module}.{name.name}" if node.module else name.name
            if full_import in self.dangerous_imports:
                severity, category, description, cwe = self.dangerous_imports[full_import]
                self._add_issue(node.lineno, severity, category, description, cwe)
        
        self.generic_visit(node)
    
    def _add_issue(self, line_number: int, severity: SeverityLevel, category: str, description: str, cwe_id: Optional[str] = None):
        """Add a security issue"""
        issue = SecurityIssue(
            issue_id=f"SEC-IMP-{len(self.issues) + 1:03d}",
            severity=severity,
            category=category,
            description=description,
            file_path=self.file_path,
            line_number=line_number,
            cwe_id=cwe_id
        )
        self.issues.append(issue)


class FunctionCallSecurityVisitor(ast.NodeVisitor):
    """AST visitor that checks function calls for security issues"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues = []
        
        # Dangerous function calls
        self.dangerous_calls = {
            "eval": (SeverityLevel.CRITICAL, "injection", "Call to eval() (code injection risk)", "CWE-95"),
            "exec": (SeverityLevel.CRITICAL, "injection", "Call to exec() (code injection risk)", "CWE-95"),
            "pickle.load": (SeverityLevel.HIGH, "insecure_operations", "Call to pickle.load() (insecure deserialization risk)", "CWE-502"),
            "pickle.loads": (SeverityLevel.HIGH, "insecure_operations", "Call to pickle.loads() (insecure deserialization risk)", "CWE-502"),
            "marshal.load": (SeverityLevel.HIGH, "insecure_operations", "Call to marshal.load() (insecure deserialization risk)", "CWE-502"),
            "marshal.loads": (SeverityLevel.HIGH, "insecure_operations", "Call to marshal.loads() (insecure deserialization risk)", "CWE-502"),
            "yaml.load": (SeverityLevel.MEDIUM, "insecure_operations", "Call to yaml.load() without safe loader", "CWE-502"),
            "subprocess.call": (SeverityLevel.MEDIUM, "injection", "Call to subprocess.call() (potential command injection risk)", "CWE-78"),
            "subprocess.Popen": (SeverityLevel.MEDIUM, "injection", "Call to subprocess.Popen() (potential command injection risk)", "CWE-78"),
            "os.system": (SeverityLevel.HIGH, "injection", "Call to os.system() (command injection risk)", "CWE-78"),
            "os.popen": (SeverityLevel.HIGH, "injection", "Call to os.popen() (command injection risk)", "CWE-78"),
            "input": (SeverityLevel.MEDIUM, "input_validation", "Call to input() without validation", "CWE-20"),
            "open": (SeverityLevel.LOW, "file_operations", "File operation with open()", None)
        }
    
    def visit_Call(self, node):
        """Process function calls"""
        # Get the function being called
        func_name = None
        
        if isinstance(node.func, ast.Name):
            # Simple function call like eval()
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            # Method call like pickle.load()
            if isinstance(node.func.value, ast.Name):
                func_name = f"{node.func.value.id}.{node.func.attr}"
        
        if func_name in self.dangerous_calls:
            severity, category, description, cwe = self.dangerous_calls[func_name]
            
            # Special case for subprocess calls with shell=True
            if func_name in ["subprocess.call", "subprocess.Popen"]:
                for keyword in node.keywords:
                    if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                        severity = SeverityLevel.HIGH
                        description = f"{description} with shell=True"
            
            # Special case for yaml.load without safe loader
            if func_name == "yaml.load" and node.args:
                has_safe_loader = False
                for keyword in node.keywords:
                    if keyword.arg == "Loader" and isinstance(keyword.value, ast.Name) and keyword.value.id in ["SafeLoader", "CSafeLoader"]:
                        has_safe_loader = True
                
                if not has_safe_loader:
                    description = f"{description} - consider using yaml.safe_load()"
            
            # Add the issue
            self._add_issue(node.lineno, severity, category, description, cwe)
        
        # Additional checks for specific function calls
        if isinstance(node.func, ast.Attribute) and node.func.attr == "format":
            # Check for potential format string injection
            if any(isinstance(arg, ast.Name) for arg in node.args) or node.keywords:
                self._add_issue(
                    node.lineno,
                    SeverityLevel.LOW,
                    "injection",
                    "String formatting with variables - verify input validation",
                    "CWE-134"
                )
        
        self.generic_visit(node)
    
    def _add_issue(self, line_number: int, severity: SeverityLevel, category: str, description: str, cwe_id: Optional[str] = None):
        """Add a security issue"""
        issue = SecurityIssue(
            issue_id=f"SEC-CALL-{len(self.issues) + 1:03d}",
            severity=severity,
            category=category,
            description=description,
            file_path=self.file_path,
            line_number=line_number,
            cwe_id=cwe_id
        )
        self.issues.append(issue)


class AssignmentSecurityVisitor(ast.NodeVisitor):
    """AST visitor that checks variable assignments for security issues"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues = []
        
        # Sensitive variable names
        self.sensitive_vars = {
            "password": (SeverityLevel.HIGH, "hardcoded_secrets", "Hardcoded password", "CWE-798"),
            "passwd": (SeverityLevel.HIGH, "hardcoded_secrets", "Hardcoded password", "CWE-798"),
            "pwd": (SeverityLevel.HIGH, "hardcoded_secrets", "Possible hardcoded password", "CWE-798"),
            "secret": (SeverityLevel.HIGH, "hardcoded_secrets", "Hardcoded secret", "CWE-798"),
            "api_key": (SeverityLevel.HIGH, "hardcoded_secrets", "Hardcoded API key", "CWE-798"),
            "apikey": (SeverityLevel.HIGH, "hardcoded_secrets", "Hardcoded API key", "CWE-798"),
            "token": (SeverityLevel.HIGH, "hardcoded_secrets", "Hardcoded token", "CWE-798"),
            "access_key": (SeverityLevel.HIGH, "hardcoded_secrets", "Hardcoded access key", "CWE-798"),
            "private_key": (SeverityLevel.HIGH, "hardcoded_secrets", "Hardcoded private key", "CWE-798"),
            "db_password": (SeverityLevel.HIGH, "hardcoded_secrets", "Hardcoded database password", "CWE-798"),
        }
        
        # Configuration flags
        self.config_flags = {
            "debug": (SeverityLevel.MEDIUM, "data_exposure", "Debug flag enabled", "CWE-489"),
            "dev_mode": (SeverityLevel.MEDIUM, "data_exposure", "Development mode enabled", "CWE-489"),
            "verbose": (SeverityLevel.LOW, "data_exposure", "Verbose mode enabled", "CWE-489"),
            "disable_security": (SeverityLevel.CRITICAL, "access_control", "Security explicitly disabled", "CWE-276"),
            "disable_validation": (SeverityLevel.HIGH, "input_validation", "Input validation disabled", "CWE-20"),
            "allow_all": (SeverityLevel.HIGH, "access_control", "Overly permissive access control", "CWE-284"),
            "verify_ssl": (SeverityLevel.MEDIUM, "insecure_operations", "SSL verification setting", "CWE-295"),
            "check_certificate": (SeverityLevel.MEDIUM, "insecure_operations", "Certificate verification setting", "CWE-295")
        }
    
    def visit_Assign(self, node):
        """Process assignment statements"""
        # Get the variable name being assigned to
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                
                # Check sensitive variables
                for sensitive_var, (severity, category, description, cwe) in self.sensitive_vars.items():
                    if sensitive_var in var_name:
                        # Check if assigned a literal value
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str) and node.value.value:
                            # Not an empty string or placeholder
                            if node.value.value not in ["", "None", "null", "placeholder", "changeme", "xxxxx"]:
                                self._add_issue(
                                    node.lineno,
                                    severity,
                                    category,
                                    f"{description}: '{var_name}'",
                                    cwe
                                )
                
                # Check configuration flags
                for flag, (severity, category, description, cwe) in self.config_flags.items():
                    if flag in var_name:
                        # Check for boolean true or similar values
                        is_true = False
                        
                        if isinstance(node.value, ast.Constant):
                            if isinstance(node.value.value, bool) and node.value.value is True:
                                is_true = True
                            elif node.value.value in [1, "1", "true", "True", "yes", "Yes", "on", "On"]:
                                is_true = True
                        elif isinstance(node.value, ast.Name) and node.value.id in ["True", "true"]:
                            is_true = True
                        
                        if is_true:
                            # Special case for SSL verification being disabled
                            if flag in ["verify_ssl", "check_certificate"] and is_true:
                                continue  # This is actually good
                            
                            self._add_issue(
                                node.lineno,
                                severity,
                                category,
                                f"{description}: '{var_name}' set to True",
                                cwe
                            )
                        elif flag in ["verify_ssl", "check_certificate"] and not is_true:
                            # Special case for SSL verification disabled
                            self._add_issue(
                                node.lineno,
                                SeverityLevel.HIGH,
                                "insecure_operations",
                                f"SSL/certificate verification disabled: '{var_name}'",
                                "CWE-295"
                            )
        
        self.generic_visit(node)
    
    def _add_issue(self, line_number: int, severity: SeverityLevel, category: str, description: str, cwe_id: Optional[str] = None):
        """Add a security issue"""
        issue = SecurityIssue(
            issue_id=f"SEC-ASN-{len(self.issues) + 1:03d}",
            severity=severity,
            category=category,
            description=description,
            file_path=self.file_path,
            line_number=line_number,
            cwe_id=cwe_id
        )
        self.issues.append(issue)


def analyze_security(project_path: str) -> str:
    """
    Perform a security analysis of the project and return a formatted report.
    This function is designed to be used as an MCP tool.
    
    Args:
        project_path: Path to the project to analyze
        
    Returns:
        Formatted report of the security analysis
    """
    analyzer = SecurityAnalyzer(project_path)
    analyzer.analyze_project()
    return analyzer.generate_text_report()


if __name__ == "__main__":
    """Main entry point for the script when run directly."""
    # Parse arguments
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Run analysis and print report
    analyzer = SecurityAnalyzer(project_path)
    analyzer.analyze_project()
    report = analyzer.generate_text_report()
    print(report)