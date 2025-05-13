#!/usr/bin/env python3
"""
AI Dev Toolkit Unified Analyzer

This module provides an integrated code analysis solution that combines the
functionality of the Sanity Checker and Security Analyzer into a single,
efficient system with shared file traversal and unified reporting.
"""

import os
import sys
import json
import re
import ast
import logging
import importlib
import concurrent.futures
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Any, Optional, Union
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("unified_analyzer")

# Try to import components
try:
    # Import sanity check components
    from .sanity_check_fixed import SanityChecker
    from .security_analyzer import SecurityAnalyzer, SeverityLevel, SecurityIssue
    COMPONENTS_AVAILABLE = True
except ImportError:
    logger.warning("Could not import all components. Running in limited mode.")
    COMPONENTS_AVAILABLE = False

# Define shared issue model
class IssueSeverity(Enum):
    """Unified severity levels for all types of issues"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1

@dataclass
class CodeIssue:
    """Unified representation of code issues from any analyzer"""
    issue_id: str
    severity: IssueSeverity
    category: str
    description: str
    file_path: str
    issue_type: str  # "quality" or "security"
    line_number: Optional[int] = None
    snippet: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    cwe_id: Optional[str] = None  # Used for security issues
    additional_info: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalysisReport:
    """Comprehensive analysis report combining quality and security findings"""
    project_path: str
    timestamp: str
    issues: List[CodeIssue] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    scan_info: Dict[str, Any] = field(default_factory=dict)
    
    def get_issues_by_severity(self, severity: IssueSeverity) -> List[CodeIssue]:
        """Get issues filtered by severity level"""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_type(self, issue_type: str) -> List[CodeIssue]:
        """Get issues filtered by type (quality or security)"""
        return [issue for issue in self.issues if issue.issue_type == issue_type]
    
    def get_issues_by_category(self, category: str) -> List[CodeIssue]:
        """Get issues filtered by category"""
        return [issue for issue in self.issues if issue.category == category]
    
    def get_issues_by_file(self, file_path: str) -> List[CodeIssue]:
        """Get issues for a specific file"""
        return [issue for issue in self.issues if issue.file_path == file_path]

class UnifiedAnalyzer:
    """
    Integrated code analyzer that combines quality and security checks
    with shared file traversal and unified reporting.
    """
    
    def __init__(self, project_path: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the unified analyzer.
        
        Args:
            project_path: Path to the project to analyze
            config: Optional configuration options
        """
        self.project_path = os.path.abspath(project_path)
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "max_workers": min(32, (os.cpu_count() or 4) * 2),
            "excluded_dirs": [
                ".git", "__pycache__", "venv", ".venv", "env", 
                "node_modules", ".ai_reference", "dist", "build"
            ],
            "security_level": "medium",  # "low", "medium", "high"
            "quality_level": "medium",   # "low", "medium", "high"
            "file_size_limit": 10 * 1024 * 1024,  # 10MB
            "use_cache": True,
            "include_security": True,
            "include_quality": True
        }
        
        # Apply defaults for missing config options
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Initialize report
        self.report = AnalysisReport(
            project_path=project_path,
            timestamp=datetime.now().isoformat(),
            scan_info={
                "analyzer_version": "1.0.0",
                "security_level": self.config["security_level"],
                "quality_level": self.config["quality_level"],
                "platform": sys.platform,
                "python_version": sys.version
            }
        )
        
        # File cache for content
        self.file_cache = {}
        
        # Track metrics
        self.report.metrics = {
            "files_scanned": 0,
            "files_analyzed": 0,
            "lines_analyzed": 0,
            "errors": 0,
            "time_taken": 0
        }
        
        # Initialize component analyzers if available
        if COMPONENTS_AVAILABLE:
            self.sanity_checker = SanityChecker(project_path)
            self.security_analyzer = SecurityAnalyzer(project_path)
        else:
            logger.warning("Component analyzers not available. Limited functionality.")
            self.sanity_checker = None
            self.security_analyzer = None
    
    def analyze_project(self) -> AnalysisReport:
        """
        Perform a comprehensive analysis of the project.
        
        Returns:
            AnalysisReport containing analysis results
        """
        start_time = datetime.now()
        logger.info(f"Starting unified analysis of {self.project_path}")
        
        # Track all files in project
        all_files = self._get_project_files()
        
        # Process files in parallel
        if self.config["max_workers"] > 1:
            issues = self._analyze_files_parallel(all_files)
        else:
            issues = self._analyze_files_sequential(all_files)
        
        # Add all issues to the report
        self.report.issues = issues
        
        # Generate summary
        self._generate_summary()
        
        # Calculate time taken
        end_time = datetime.now()
        time_taken = (end_time - start_time).total_seconds()
        self.report.metrics["time_taken"] = time_taken
        
        logger.info(f"Analysis complete in {time_taken:.2f} seconds. Found {len(issues)} issues.")
        
        return self.report
    
    def _get_project_files(self) -> Dict[str, Dict[str, Any]]:
        """Get all relevant files in the project."""
        all_files = {}
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.config["excluded_dirs"]]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_path)
                
                # Skip large files by default
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > self.config["file_size_limit"]:
                        logger.info(f"Skipping large file: {rel_path} ({file_size / 1024 / 1024:.2f} MB)")
                        continue
                except OSError:
                    continue
                
                # Categorize file
                file_info = self._categorize_file(file_path)
                
                if file_info["category"] != "ignored":
                    all_files[file_path] = file_info
        
        self.report.metrics["files_scanned"] = len(all_files)
        return all_files
    
    def _categorize_file(self, file_path: str) -> Dict[str, Any]:
        """Categorize a file for analysis."""
        filename = os.path.basename(file_path)
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        # Determine file category
        if ext == '.py':
            category = 'python'
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            category = 'javascript'
        elif ext in ['.json', '.yaml', '.yml', '.toml', '.ini']:
            category = 'config'
        elif ext in ['.md', '.txt', '.rst']:
            category = 'documentation'
        elif ext in ['.c', '.cpp', '.h', '.hpp', '.java']:
            category = 'compiled'
        elif ext in ['.html', '.css', '.scss', '.less']:
            category = 'web'
        elif ext in ['.sh', '.bat', '.ps1']:
            category = 'script'
        else:
            category = 'ignored'
        
        # Special categories for specific files
        if filename == 'claude_desktop_config.json':
            category = 'claude_config'
        
        # Determine risk level
        risk_level = self._get_file_risk_level(file_path, category)
        
        return {
            "category": category,
            "ext": ext,
            "rel_path": os.path.relpath(file_path, self.project_path),
            "risk_level": risk_level,
            "content": None  # Will be lazy-loaded when needed
        }
    
    def _get_file_risk_level(self, file_path: str, category: str) -> str:
        """Determine the risk level of a file."""
        rel_path = os.path.relpath(file_path, self.project_path)
        
        # High-risk paths and terms
        high_risk_indicators = [
            '/server/', '/api/', '/auth/', '/login/', '/admin/',
            'password', 'token', 'secret', 'crypt', 'security',
            'permission', 'access', 'authenticate'
        ]
        
        # Check if this is a high-risk file
        is_high_risk = any(indicator in rel_path.lower() for indicator in high_risk_indicators)
        
        # Configuration files are often high risk
        if category in ['config', 'claude_config']:
            return 'high'
        
        # Test files are lower risk
        if 'test' in rel_path or 'tests' in rel_path:
            return 'low'
        elif is_high_risk:
            return 'high'
        else:
            return 'medium'
    
    def _get_file_content(self, file_path: str) -> Optional[str]:
        """Get file content with caching."""
        if file_path in self.file_cache:
            return self.file_cache[file_path]
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Update metrics
            self.report.metrics["files_analyzed"] += 1
            self.report.metrics["lines_analyzed"] += content.count('\n') + 1
            
            # Cache content
            self.file_cache[file_path] = content
            
            return content
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
            self.report.metrics["errors"] += 1
            self.file_cache[file_path] = None
            return None
    
    def _analyze_files_parallel(self, all_files: Dict[str, Dict[str, Any]]) -> List[CodeIssue]:
        """Analyze files in parallel."""
        all_issues = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config["max_workers"]) as executor:
            # Submit all file analysis tasks
            future_to_file = {
                executor.submit(self._analyze_single_file, file_path, file_info): file_path
                for file_path, file_info in all_files.items()
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    file_issues = future.result()
                    all_issues.extend(file_issues)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    self.report.metrics["errors"] += 1
        
        return all_issues
    
    def _analyze_files_sequential(self, all_files: Dict[str, Dict[str, Any]]) -> List[CodeIssue]:
        """Analyze files sequentially."""
        all_issues = []
        
        for file_path, file_info in all_files.items():
            try:
                file_issues = self._analyze_single_file(file_path, file_info)
                all_issues.extend(file_issues)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                self.report.metrics["errors"] += 1
        
        return all_issues
    
    def _analyze_single_file(self, file_path: str, file_info: Dict[str, Any]) -> List[CodeIssue]:
        """Analyze a single file."""
        issues = []
        
        # Get file content
        content = self._get_file_content(file_path)
        if content is None:
            return issues
        
        # Determine which checks to run based on file category and risk level
        quality_checks = self._should_run_quality_checks(file_info)
        security_checks = self._should_run_security_checks(file_info)
        
        # Run quality checks if enabled
        if quality_checks and self.config["include_quality"]:
            quality_issues = self._run_quality_checks(file_path, content, file_info)
            issues.extend(quality_issues)
        
        # Run security checks if enabled
        if security_checks and self.config["include_security"]:
            security_issues = self._run_security_checks(file_path, content, file_info)
            issues.extend(security_issues)
        
        return issues
    
    def _should_run_quality_checks(self, file_info: Dict[str, Any]) -> bool:
        """Determine if quality checks should be run for this file."""
        # Always check Python files
        if file_info["category"] == "python":
            return True
        
        # Check configuration files if quality level is medium or high
        if file_info["category"] == "config" and self.config["quality_level"] in ["medium", "high"]:
            return True
        
        # Check documentation if quality level is high
        if file_info["category"] == "documentation" and self.config["quality_level"] == "high":
            return True
        
        # Skip other file types for quality checks
        return False
    
    def _should_run_security_checks(self, file_info: Dict[str, Any]) -> bool:
        """Determine if security checks should be run for this file."""
        # Always check high-risk files
        if file_info["risk_level"] == "high":
            return True
        
        # Check medium-risk files if security level is medium or high
        if file_info["risk_level"] == "medium" and self.config["security_level"] in ["medium", "high"]:
            return True
        
        # Check low-risk files only if security level is high
        if file_info["risk_level"] == "low" and self.config["security_level"] == "high":
            return True
        
        return False
    
    def _run_quality_checks(self, file_path: str, content: str, file_info: Dict[str, Any]) -> List[CodeIssue]:
        """Run quality checks on a file."""
        issues = []
        
        if not COMPONENTS_AVAILABLE:
            return issues
        
        try:
            if file_info["category"] == "python":
                # Check imports
                import_issues = self._check_python_imports(file_path, content)
                issues.extend(import_issues)
                
                # Check path references
                path_issues = self._check_python_path_references(file_path, content)
                issues.extend(path_issues)
                
                # Check for deprecated functions
                deprecated_issues = self._check_deprecated_functions(file_path, content)
                issues.extend(deprecated_issues)
                
                # Try AST parsing for more checks
                try:
                    tree = ast.parse(content)
                    ast_issues = self._check_python_ast_quality(file_path, tree)
                    issues.extend(ast_issues)
                except SyntaxError as e:
                    # Report syntax error
                    issues.append(CodeIssue(
                        issue_id=f"Q-SYN-{len(issues) + 1}",
                        severity=IssueSeverity.HIGH,
                        category="syntax",
                        description=f"Python syntax error: {str(e)}",
                        file_path=os.path.relpath(file_path, self.project_path),
                        issue_type="quality",
                        line_number=e.lineno,
                        snippet=e.text.strip() if e.text else None,
                        recommendations=["Fix the syntax error to make the code valid Python"]
                    ))
        except Exception as e:
            logger.warning(f"Error in quality checks for {file_path}: {e}")
        
        return issues
    
    def _run_security_checks(self, file_path: str, content: str, file_info: Dict[str, Any]) -> List[CodeIssue]:
        """Run security checks on a file."""
        issues = []
        
        if not COMPONENTS_AVAILABLE:
            return issues
        
        try:
            # Category-specific checks
            if file_info["category"] == "python":
                # Check for security patterns
                pattern_issues = self._check_python_security_patterns(file_path, content)
                issues.extend(pattern_issues)
                
                # Try AST parsing for more checks
                try:
                    tree = ast.parse(content)
                    ast_issues = self._check_python_ast_security(file_path, tree)
                    issues.extend(ast_issues)
                except SyntaxError:
                    # Already reported in quality checks
                    pass
                
            elif file_info["category"] == "config":
                # Check for security issues in config files
                config_issues = self._check_config_security(file_path, content, file_info["ext"])
                issues.extend(config_issues)
                
            elif file_info["category"] == "claude_config":
                # Special checks for claude desktop config
                claude_issues = self._check_claude_config_security(file_path, content)
                issues.extend(claude_issues)
        except Exception as e:
            logger.warning(f"Error in security checks for {file_path}: {e}")
        
        return issues
    
    def _check_python_imports(self, file_path: str, content: str) -> List[CodeIssue]:
        """Check Python imports for quality issues."""
        issues = []
        
        try:
            # Extract imports using regex for basic check
            import_pattern = re.compile(r'^(?:from\s+[^\s]+\s+)?import\s+[^\s#]+', re.MULTILINE)
            imports = import_pattern.finditer(content)
            
            for match in imports:
                import_line = match.group(0)
                line_num = content[:match.start()].count('\n') + 1
                
                # Check for common relative import issues
                if 'from .' in import_line and '..' in import_line:
                    issues.append(CodeIssue(
                        issue_id=f"Q-IMP-{len(issues) + 1}",
                        severity=IssueSeverity.MEDIUM,
                        category="imports",
                        description="Complex relative import may cause issues",
                        file_path=os.path.relpath(file_path, self.project_path),
                        issue_type="quality",
                        line_number=line_num,
                        snippet=import_line.strip(),
                        recommendations=[
                            "Consider using absolute imports instead of complex relative imports",
                            "Ensure the package structure supports these imports"
                        ]
                    ))
        except Exception as e:
            logger.warning(f"Error checking imports in {file_path}: {e}")
        
        return issues
    
    def _check_python_path_references(self, file_path: str, content: str) -> List[CodeIssue]:
        """Check for hardcoded paths in Python files."""
        issues = []
        
        # Define suspicious path patterns
        suspicious_patterns = [
            ('src/', 'Hardcoded src/ directory reference'),
            ('src\\\\', 'Hardcoded src\\ directory reference'),
            ('../src', 'Relative path to src directory'),
            ('src.librarian', 'Hardcoded module path'),
            ('ai_librarian_server.py', 'Hardcoded reference to ai_librarian_server.py'),
            ('/src/mcp/', 'Hardcoded absolute path to /src/mcp/')
        ]
        
        try:
            # Check for each pattern
            for pattern, description in suspicious_patterns:
                if pattern in content:
                    # Find line numbers and context
                    lines = content.splitlines()
                    for i, line in enumerate(lines, 1):
                        if pattern in line and not line.strip().startswith('#'):
                            issues.append(CodeIssue(
                                issue_id=f"Q-PATH-{len(issues) + 1}",
                                severity=IssueSeverity.MEDIUM,
                                category="paths",
                                description=f"{description}",
                                file_path=os.path.relpath(file_path, self.project_path),
                                issue_type="quality",
                                line_number=i,
                                snippet=line.strip(),
                                recommendations=[
                                    "Use relative imports or dynamic path resolution",
                                    "Avoid hardcoded file paths",
                                    "Consider using os.path.join for platform-independent paths"
                                ]
                            ))
        except Exception as e:
            logger.warning(f"Error checking paths in {file_path}: {e}")
        
        return issues
    
    def _check_deprecated_functions(self, file_path: str, content: str) -> List[CodeIssue]:
        """Check for deprecated function calls."""
        issues = []
        
        # Define patterns for deprecated functions
        deprecated_functions = [
            (r'initialize_librarian\(', 'Call to deprecated initialize_librarian() function'),
            (r'indexer\.initialize_librarian\(', 'Call to deprecated indexer.initialize_librarian() function'),
            (r'from\s+indexer\s+import', 'Importing from deprecated indexer module'),
            (r'import\s+indexer', 'Importing deprecated indexer module')
        ]
        
        try:
            # Skip the indexer.py file itself
            if file_path.endswith('indexer.py'):
                return issues
                
            # Check for each pattern
            for pattern, description in deprecated_functions:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Get line for context
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                        
                    snippet = content[line_start:line_end].strip()
                    
                    issues.append(CodeIssue(
                        issue_id=f"Q-DEP-{len(issues) + 1}",
                        severity=IssueSeverity.MEDIUM,
                        category="deprecated",
                        description=description,
                        file_path=os.path.relpath(file_path, self.project_path),
                        issue_type="quality",
                        line_number=line_num,
                        snippet=snippet,
                        recommendations=[
                            "Use enhanced_indexer.py instead of the deprecated indexer.py",
                            "Replace initialize_librarian() with initialize_enhanced_librarian()"
                        ]
                    ))
        except Exception as e:
            logger.warning(f"Error checking deprecated functions in {file_path}: {e}")
        
        return issues
    
    def _check_python_ast_quality(self, file_path: str, tree: ast.AST) -> List[CodeIssue]:
        """Check Python AST for quality issues."""
        issues = []
        
        # Use a custom AST visitor for quality checks
        visitor = QualityCheckVisitor(file_path)
        visitor.visit(tree)
        
        # Convert visitor issues to unified format
        for issue in visitor.issues:
            unified_issue = CodeIssue(
                issue_id=f"Q-AST-{len(issues) + 1}",
                severity=IssueSeverity.MEDIUM if issue["severity"] == "warning" else IssueSeverity.LOW,
                category=issue["category"],
                description=issue["description"],
                file_path=os.path.relpath(file_path, self.project_path),
                issue_type="quality",
                line_number=issue["line"],
                recommendations=issue.get("recommendations", [])
            )
            issues.append(unified_issue)
        
        return issues
    
    def _check_python_security_patterns(self, file_path: str, content: str) -> List[CodeIssue]:
        """Check Python code for security patterns."""
        issues = []
        
        # Import vulnerability patterns from security analyzer
        if hasattr(self, 'security_analyzer'):
            patterns = []
            
            # Combine all patterns
            for category, cat_patterns in self.security_analyzer.vulnerability_patterns.items():
                for pattern, description, severity in cat_patterns:
                    patterns.append((pattern, description, severity, category))
                    
            for category, cat_patterns in self.security_analyzer.toolkit_specific_patterns.items():
                for pattern, description, severity in cat_patterns:
                    patterns.append((pattern, description, severity, category))
            
            # Check each pattern
            for pattern_str, description, severity, category in patterns:
                try:
                    # Compile pattern
                    pattern = re.compile(pattern_str)
                    
                    # Find matches
                    matches = pattern.finditer(content)
                    for match in matches:
                        # Calculate line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Get line for context
                        line_start = content.rfind('\n', 0, match.start()) + 1
                        line_end = content.find('\n', match.end())
                        if line_end == -1:
                            line_end = len(content)
                            
                        snippet = content[line_start:line_end].strip()
                        
                        # Convert severity from security analyzer to unified format
                        unified_severity = {
                            SeverityLevel.CRITICAL: IssueSeverity.CRITICAL,
                            SeverityLevel.HIGH: IssueSeverity.HIGH,
                            SeverityLevel.MEDIUM: IssueSeverity.MEDIUM,
                            SeverityLevel.LOW: IssueSeverity.LOW,
                            SeverityLevel.INFO: IssueSeverity.INFO
                        }.get(severity, IssueSeverity.MEDIUM)
                        
                        issues.append(CodeIssue(
                            issue_id=f"S-PAT-{len(issues) + 1}",
                            severity=unified_severity,
                            category=category,
                            description=description,
                            file_path=os.path.relpath(file_path, self.project_path),
                            issue_type="security",
                            line_number=line_num,
                            snippet=snippet
                        ))
                except Exception as e:
                    logger.warning(f"Error checking pattern {pattern_str} in {file_path}: {e}")
        
        return issues
    
    def _check_python_ast_security(self, file_path: str, tree: ast.AST) -> List[CodeIssue]:
        """Check Python AST for security issues."""
        issues = []
        
        # Import security visitors if available
        if hasattr(self, 'security_analyzer'):
            # Run the ImportSecurityVisitor
            import_visitor = getattr(self.security_analyzer.__class__, 'ImportSecurityVisitor', None)
            if import_visitor:
                try:
                    visitor = import_visitor(file_path)
                    visitor.visit(tree)
                    issues.extend(self._convert_security_issues(visitor.issues))
                except Exception as e:
                    logger.warning(f"Error in import security visitor for {file_path}: {e}")
            
            # Run the FunctionCallSecurityVisitor
            call_visitor = getattr(self.security_analyzer.__class__, 'FunctionCallSecurityVisitor', None)
            if call_visitor:
                try:
                    visitor = call_visitor(file_path)
                    visitor.visit(tree)
                    issues.extend(self._convert_security_issues(visitor.issues))
                except Exception as e:
                    logger.warning(f"Error in function call security visitor for {file_path}: {e}")
            
            # Run the AssignmentSecurityVisitor
            assign_visitor = getattr(self.security_analyzer.__class__, 'AssignmentSecurityVisitor', None)
            if assign_visitor:
                try:
                    visitor = assign_visitor(file_path)
                    visitor.visit(tree)
                    issues.extend(self._convert_security_issues(visitor.issues))
                except Exception as e:
                    logger.warning(f"Error in assignment security visitor for {file_path}: {e}")
        
        return issues
    
    def _convert_security_issues(self, sec_issues: List[SecurityIssue]) -> List[CodeIssue]:
        """Convert security issues to unified format."""
        issues = []
        
        for issue in sec_issues:
            # Convert severity
            unified_severity = {
                SeverityLevel.CRITICAL: IssueSeverity.CRITICAL,
                SeverityLevel.HIGH: IssueSeverity.HIGH,
                SeverityLevel.MEDIUM: IssueSeverity.MEDIUM,
                SeverityLevel.LOW: IssueSeverity.LOW,
                SeverityLevel.INFO: IssueSeverity.INFO
            }.get(issue.severity, IssueSeverity.MEDIUM)
            
            # Create unified issue
            unified_issue = CodeIssue(
                issue_id=issue.issue_id,
                severity=unified_severity,
                category=issue.category,
                description=issue.description,
                file_path=os.path.relpath(issue.file_path, self.project_path),
                issue_type="security",
                line_number=issue.line_number,
                snippet=issue.snippet,
                cwe_id=issue.cwe_id
            )
            
            issues.append(unified_issue)
        
        return issues
    
    def _check_config_security(self, file_path: str, content: str, ext: str) -> List[CodeIssue]:
        """Check configuration files for security issues."""
        issues = []
        
        # Define patterns for different config file types
        config_patterns = {
            ".json": [
                (r"\"debug\"\s*:\s*true", "Debug mode enabled in JSON config", IssueSeverity.MEDIUM),
                (r"\"(password|secret|token|key)\"\s*:\s*\"[^\"]+\"", "Possible credentials in JSON config", IssueSeverity.HIGH),
                (r"\"verify\"\s*:\s*false", "SSL verification disabled in JSON config", IssueSeverity.HIGH)
            ],
            ".yaml": [
                (r"debug:\s*true", "Debug mode enabled in YAML config", IssueSeverity.MEDIUM),
                (r"(password|secret|token|key):\s*['\"]?[^'\"\n]+['\"]?", "Possible credentials in YAML config", IssueSeverity.HIGH),
                (r"verify:\s*false", "SSL verification disabled in YAML config", IssueSeverity.HIGH)
            ],
            ".ini": [
                (r"debug\s*=\s*true", "Debug mode enabled in INI config", IssueSeverity.MEDIUM),
                (r"(password|secret|token|key)\s*=\s*[^\n]+", "Possible credentials in INI config", IssueSeverity.HIGH),
                (r"verify\s*=\s*false", "SSL verification disabled in INI config", IssueSeverity.HIGH)
            ]
        }
        
        # Get patterns for this file type
        file_patterns = config_patterns.get(ext, [])
        
        # Check patterns
        for pattern_str, description, severity in file_patterns:
            try:
                pattern = re.compile(pattern_str)
                matches = pattern.finditer(content)
                
                for match in matches:
                    # Calculate line number
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Get line for context
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                        
                    snippet = content[line_start:line_end].strip()
                    
                    issues.append(CodeIssue(
                        issue_id=f"S-CONF-{len(issues) + 1}",
                        severity=severity,
                        category="configuration",
                        description=description,
                        file_path=os.path.relpath(file_path, self.project_path),
                        issue_type="security",
                        line_number=line_num,
                        snippet=snippet
                    ))
            except Exception as e:
                logger.warning(f"Error checking config pattern in {file_path}: {e}")
        
        return issues
    
    def _check_claude_config_security(self, file_path: str, content: str) -> List[CodeIssue]:
        """Check Claude Desktop config for security issues."""
        issues = []
        
        try:
            # Parse JSON
            config = json.loads(content)
            
            # Check MCP server configuration
            if "mcpServers" in config:
                for server_name, server_config in config["mcpServers"].items():
                    # Check for proper allowed directories configuration
                    if "env" not in server_config or "AI_LIBRARIAN_ALLOWED_DIRS" not in server_config.get("env", {}):
                        issues.append(CodeIssue(
                            issue_id=f"S-MCP-{len(issues) + 1}",
                            severity=IssueSeverity.HIGH,
                            category="mcp_security",
                            description=f"MCP server '{server_name}' may not have properly restricted directory access",
                            file_path=os.path.relpath(file_path, self.project_path),
                            issue_type="security",
                            recommendations=[
                                "Add AI_LIBRARIAN_ALLOWED_DIRS environment variable to the MCP server configuration",
                                "Restrict directory access to only what is needed"
                            ]
                        ))
                    
                    # Check for proper command validation
                    if "command" in server_config and server_config["command"] not in ["python", "python3"]:
                        issues.append(CodeIssue(
                            issue_id=f"S-MCP-{len(issues) + 1}",
                            severity=IssueSeverity.MEDIUM,
                            category="mcp_security",
                            description=f"MCP server '{server_name}' uses non-standard command: {server_config['command']}",
                            file_path=os.path.relpath(file_path, self.project_path),
                            issue_type="security",
                            recommendations=[
                                "Use standard 'python' or 'python3' commands for MCP servers",
                                "Avoid custom shell commands that may introduce security risks"
                            ]
                        ))
        except json.JSONDecodeError as e:
            # Report JSON parse error
            issues.append(CodeIssue(
                issue_id=f"S-JSON-{len(issues) + 1}",
                severity=IssueSeverity.MEDIUM,
                category="configuration",
                description=f"Invalid JSON in Claude Desktop config: {e}",
                file_path=os.path.relpath(file_path, self.project_path),
                issue_type="security",
                recommendations=[
                    "Fix the JSON syntax error in the configuration file",
                    "Use a JSON validator to ensure the file is correctly formatted"
                ]
            ))
        except Exception as e:
            logger.warning(f"Error checking Claude config in {file_path}: {e}")
        
        return issues
    
    def _generate_summary(self):
        """Generate summary information for the report."""
        # Count issues by severity
        severity_counts = {severity: 0 for severity in IssueSeverity}
        for issue in self.report.issues:
            severity_counts[issue.severity] += 1
        
        # Count issues by type
        type_counts = {"quality": 0, "security": 0}
        for issue in self.report.issues:
            type_counts[issue.issue_type] += 1
        
        # Count issues by category
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
            
            if issue.severity == IssueSeverity.CRITICAL:
                category_counts[issue.category]["critical"] += 1
            elif issue.severity == IssueSeverity.HIGH:
                category_counts[issue.category]["high"] += 1
            elif issue.severity == IssueSeverity.MEDIUM:
                category_counts[issue.category]["medium"] += 1
            elif issue.severity == IssueSeverity.LOW:
                category_counts[issue.category]["low"] += 1
            elif issue.severity == IssueSeverity.INFO:
                category_counts[issue.category]["info"] += 1
        
        # Group issues by file
        files_with_issues = {}
        for issue in self.report.issues:
            if issue.file_path not in files_with_issues:
                files_with_issues[issue.file_path] = 0
            files_with_issues[issue.file_path] += 1
        
        # Calculate overall risk level
        if severity_counts[IssueSeverity.CRITICAL] > 0:
            risk_level = "Critical"
        elif severity_counts[IssueSeverity.HIGH] > 3:
            risk_level = "High"
        elif severity_counts[IssueSeverity.HIGH] > 0 or severity_counts[IssueSeverity.MEDIUM] > 5:
            risk_level = "Medium"
        elif severity_counts[IssueSeverity.MEDIUM] > 0 or severity_counts[IssueSeverity.LOW] > 0:
            risk_level = "Low"
        else:
            risk_level = "Minimal"
        
        # Create summary
        self.report.summary = {
            "total_issues": len(self.report.issues),
            "severity_counts": {severity.name: count for severity, count in severity_counts.items()},
            "type_counts": type_counts,
            "category_counts": category_counts,
            "files_with_issues": len(files_with_issues),
            "risk_level": risk_level
        }
    
    def generate_report(self, format_type: str = "markdown") -> str:
        """
        Generate a formatted report of the analysis results.
        
        Args:
            format_type: Type of report format ("markdown", "json", "html")
            
        Returns:
            Formatted report string
        """
        if format_type == "json":
            return self._generate_json_report()
        elif format_type == "html":
            return self._generate_html_report()
        else:
            return self._generate_markdown_report()
    
    def _generate_markdown_report(self) -> str:
        """Generate a markdown format report."""
        report_lines = []
        
        # Header
        report_lines.append("# AI Dev Toolkit Unified Analysis Report")
        report_lines.append("")
        report_lines.append(f"Project: {self.report.project_path}")
        report_lines.append(f"Date: {self.report.timestamp}")
        report_lines.append(f"Analysis Mode: Quality={self.config['quality_level'].title()}, Security={self.config['security_level'].title()}")
        report_lines.append("")
        
        # Summary
        report_lines.append("## Executive Summary")
        report_lines.append("")
        report_lines.append(f"Overall Risk Level: **{self.report.summary['risk_level']}**")
        report_lines.append("")
        report_lines.append(f"- Found **{self.report.summary['total_issues']}** total issues")
        report_lines.append(f"- **{self.report.summary['severity_counts'].get('CRITICAL', 0)}** critical severity issues")
        report_lines.append(f"- **{self.report.summary['severity_counts'].get('HIGH', 0)}** high severity issues")
        report_lines.append(f"- **{self.report.summary['severity_counts'].get('MEDIUM', 0)}** medium severity issues")
        report_lines.append(f"- **{self.report.summary['severity_counts'].get('LOW', 0)}** low severity issues")
        report_lines.append(f"- **{self.report.summary['severity_counts'].get('INFO', 0)}** informational findings")
        report_lines.append(f"- **{self.report.summary['files_with_issues']}** files with issues")
        report_lines.append("")
        
        # Issues by category
        report_lines.append("## Issues by Category")
        report_lines.append("")
        report_lines.append("| Category | Critical | High | Medium | Low | Info | Total |")
        report_lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        
        for category, counts in self.report.summary["category_counts"].items():
            report_lines.append(f"| {category} | {counts['critical']} | {counts['high']} | {counts['medium']} | {counts['low']} | {counts['info']} | {counts['total']} |")
        
        report_lines.append("")
        
        # Scan metrics
        report_lines.append("## Scan Coverage")
        report_lines.append("")
        report_lines.append(f"- Files scanned: **{self.report.metrics['files_scanned']}**")
        report_lines.append(f"- Files analyzed: **{self.report.metrics['files_analyzed']}**")
        report_lines.append(f"- Lines of code analyzed: **{self.report.metrics['lines_analyzed']}**")
        report_lines.append(f"- Analysis time: **{self.report.metrics['time_taken']:.2f} seconds**")
        report_lines.append("")
        
        # Critical and high issues
        critical_high_issues = [issue for issue in self.report.issues 
                              if issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]]
        
        if critical_high_issues:
            report_lines.append("## Critical and High Severity Issues")
            report_lines.append("")
            
            for issue in critical_high_issues:
                report_lines.append(f"### {issue.issue_id}: {issue.description}")
                report_lines.append("")
                report_lines.append(f"**Severity**: {issue.severity.name}")
                report_lines.append(f"**Category**: {issue.category}")
                report_lines.append(f"**Type**: {issue.issue_type}")
                report_lines.append(f"**File**: {issue.file_path}")
                
                if issue.line_number:
                    report_lines.append(f"**Line**: {issue.line_number}")
                
                if issue.cwe_id:
                    report_lines.append(f"**CWE**: {issue.cwe_id}")
                
                if issue.snippet:
                    report_lines.append("")
                    report_lines.append("```")
                    report_lines.append(issue.snippet)
                    report_lines.append("```")
                
                if issue.recommendations:
                    report_lines.append("")
                    report_lines.append("**Recommendations**:")
                    for rec in issue.recommendations:
                        report_lines.append(f"- {rec}")
                
                report_lines.append("")
            
            report_lines.append("")
        
        # Issues by file
        report_lines.append("## Issues by File")
        report_lines.append("")
        
        # Group issues by file
        issues_by_file = {}
        for issue in self.report.issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)
        
        # Sort files by number of issues (desc)
        sorted_files = sorted(issues_by_file.items(), key=lambda x: len(x[1]), reverse=True)
        
        for file_path, file_issues in sorted_files:
            report_lines.append(f"### {file_path}")
            report_lines.append("")
            
            # Sort issues by severity
            sorted_issues = sorted(file_issues, key=lambda x: x.severity.value, reverse=True)
            
            report_lines.append("| ID | Severity | Type | Description | Line |")
            report_lines.append("| --- | --- | --- | --- | --- |")
            
            for issue in sorted_issues:
                line = issue.line_number if issue.line_number else "-"
                report_lines.append(f"| {issue.issue_id} | {issue.severity.name} | {issue.issue_type} | {issue.description} | {line} |")
            
            report_lines.append("")
        
        # Recommendations
        report_lines.append("## Recommendations")
        report_lines.append("")
        
        # Group recommendations by category
        recommendations_by_category = {}
        for issue in self.report.issues:
            if not issue.recommendations:
                continue
                
            if issue.category not in recommendations_by_category:
                recommendations_by_category[issue.category] = set()
                
            for rec in issue.recommendations:
                recommendations_by_category[issue.category].add(rec)
        
        if recommendations_by_category:
            for category, recs in recommendations_by_category.items():
                report_lines.append(f"### {category.title()}")
                report_lines.append("")
                
                for rec in recs:
                    report_lines.append(f"- {rec}")
                
                report_lines.append("")
        else:
            report_lines.append("No specific recommendations available.")
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def _generate_json_report(self) -> str:
        """Generate a JSON format report."""
        # Convert Enum values to strings
        def serialize_issue(issue):
            issue_dict = {
                "issue_id": issue.issue_id,
                "severity": issue.severity.name,
                "category": issue.category,
                "description": issue.description,
                "file_path": issue.file_path,
                "issue_type": issue.issue_type,
                "line_number": issue.line_number,
                "snippet": issue.snippet,
                "recommendations": issue.recommendations,
                "cwe_id": issue.cwe_id,
                "additional_info": issue.additional_info
            }
            return issue_dict
        
        # Create JSON structure
        report_dict = {
            "project_path": self.report.project_path,
            "timestamp": self.report.timestamp,
            "summary": self.report.summary,
            "metrics": self.report.metrics,
            "scan_info": self.report.scan_info,
            "issues": [serialize_issue(issue) for issue in self.report.issues]
        }
        
        # Convert to JSON
        return json.dumps(report_dict, indent=2)
    
    def _generate_html_report(self) -> str:
        """Generate an HTML format report."""
        # Convert markdown to HTML
        md_report = self._generate_markdown_report()
        
        # Simple HTML wrapper
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Dev Toolkit Analysis Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            border-bottom: 2px solid #eaecef;
            padding-bottom: 0.3em;
        }}
        h2 {{
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f6f8fa;
        }}
        code {{
            font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
            background-color: rgba(27, 31, 35, 0.05);
            border-radius: 3px;
            padding: 0.2em 0.4em;
        }}
        pre {{
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 16px;
            overflow: auto;
        }}
        .severity-CRITICAL {{
            color: #b71c1c;
            font-weight: bold;
        }}
        .severity-HIGH {{
            color: #e53935;
            font-weight: bold;
        }}
        .severity-MEDIUM {{
            color: #fb8c00;
        }}
        .severity-LOW {{
            color: #43a047;
        }}
        .severity-INFO {{
            color: #1e88e5;
        }}
    </style>
</head>
<body>
    <div id="content">
        <!-- Placeholder for Markdown content -->
        {md_report}
    </div>
    
    <script>
        // Simple markdown to HTML converter for basic elements
        document.addEventListener('DOMContentLoaded', function() {{
            const content = document.getElementById('content');
            let html = content.innerHTML;
            
            // Convert headers
            html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
            html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
            html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
            
            // Convert tables (simple approach)
            html = html.replace(/\\|(.+)\\|/g, '<tr><td>$1</td></tr>');
            html = html.replace(/<td>([^<]+)<\\/td>/g, function(match, p1) {{
                return '<td>' + p1.split('|').map(s => s.trim()).join('</td><td>') + '</td>';
            }});
            
            // Convert lists
            html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
            
            // Apply severity classes
            html = html.replace(/(CRITICAL|HIGH|MEDIUM|LOW|INFO)/g, '<span class="severity-$1">$1</span>');
            
            content.innerHTML = html;
        }});
    </script>
</body>
</html>
"""
        return html

# Custom AST visitor for quality checks
class QualityCheckVisitor(ast.NodeVisitor):
    """AST visitor that checks for code quality issues."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues = []
    
    def visit_FunctionDef(self, node):
        """Check function definitions."""
        # Check function length
        if len(node.body) > 50:
            self.issues.append({
                "category": "complexity",
                "severity": "warning",
                "description": f"Function '{node.name}' is too long ({len(node.body)} lines)",
                "line": node.lineno,
                "recommendations": [
                    "Consider breaking down large functions into smaller ones",
                    "Extract helper functions for repeated code blocks",
                    "Use higher-order functions when appropriate"
                ]
            })
        
        # Check number of arguments
        args = len(node.args.args)
        if args > 8:
            self.issues.append({
                "category": "complexity",
                "severity": "warning",
                "description": f"Function '{node.name}' has too many parameters ({args})",
                "line": node.lineno,
                "recommendations": [
                    "Group related parameters into a class or data structure",
                    "Use keyword arguments with defaults",
                    "Consider a configuration object pattern"
                ]
            })
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Check class definitions."""
        # Check class size
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) > 20:
            self.issues.append({
                "category": "complexity",
                "severity": "warning",
                "description": f"Class '{node.name}' has too many methods ({len(methods)})",
                "line": node.lineno,
                "recommendations": [
                    "Consider breaking the class into smaller, more focused classes",
                    "Extract utility methods to helper classes",
                    "Use composition over inheritance"
                ]
            })
        
        self.generic_visit(node)
    
    def visit_Try(self, node):
        """Check try-except blocks."""
        # Check for bare except
        for handler in node.handlers:
            if handler.type is None:
                self.issues.append({
                    "category": "error_handling",
                    "severity": "warning",
                    "description": "Use of bare 'except:' without specifying exceptions",
                    "line": handler.lineno,
                    "recommendations": [
                        "Specify the exceptions you expect to catch",
                        "Use 'except Exception:' as a last resort, not as default",
                        "Handle specific exceptions with specific recovery strategies"
                    ]
                })
        
        self.generic_visit(node)

# Run as a script
def analyze_project(project_path: str, output_format: str = "markdown", 
                  config: Optional[Dict[str, Any]] = None) -> str:
    """
    Analyze a project and return a formatted report.
    
    Args:
        project_path: Path to the project to analyze
        output_format: Format for the report ("markdown", "json", "html")
        config: Optional configuration options
        
    Returns:
        Formatted analysis report
    """
    analyzer = UnifiedAnalyzer(project_path, config)
    analyzer.analyze_project()
    return analyzer.generate_report(output_format)

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Dev Toolkit Unified Analyzer")
    parser.add_argument("project_path", help="Path to the project to analyze")
    parser.add_argument("--format", choices=["markdown", "json", "html"], default="markdown",
                       help="Output format for the report")
    parser.add_argument("--security-level", choices=["low", "medium", "high"], default="medium",
                       help="Level of security analysis")
    parser.add_argument("--quality-level", choices=["low", "medium", "high"], default="medium",
                       help="Level of quality analysis")
    parser.add_argument("--no-security", action="store_true", help="Disable security analysis")
    parser.add_argument("--no-quality", action="store_true", help="Disable quality analysis")
    parser.add_argument("--output", help="Output file to write report to")
    parser.add_argument("--workers", type=int, help="Number of worker threads to use")
    
    args = parser.parse_args()
    
    # Create configuration
    config = {
        "security_level": args.security_level,
        "quality_level": args.quality_level,
        "include_security": not args.no_security,
        "include_quality": not args.no_quality
    }
    
    if args.workers:
        config["max_workers"] = args.workers
    
    # Run analysis
    report = analyze_project(args.project_path, args.format, config)
    
    # Output report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
    else:
        print(report)