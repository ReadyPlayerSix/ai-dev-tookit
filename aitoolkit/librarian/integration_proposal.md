# Security Analyzer and Sanity Check Integration Proposal

## Current State

The AI Dev Toolkit currently has two separate but complementary tools:

1. **Sanity Checker (`sanity_check_fixed.py`)**: Detects code quality issues, path problems, and structure inconsistencies.
2. **Security Analyzer (`security_analyzer.py`)**: Performs comprehensive security vulnerability scanning.

There is already a basic integration via `security_analyzer_integration.py`, which:
- Adds a standalone `security_analyze` MCP tool
- Creates an enhanced version of the sanity_check that can optionally include security analysis

## Improvement Opportunities

### 1. Performance Optimization

The current integration runs the security analyzer as a separate pass after the sanity check, which means:
- Files are read twice
- The codebase is traversed twice
- Some checks are duplicated (e.g., looking for critical files)

### 2. Unified Reporting

Currently, the reports from sanity check and security analyzer are simply concatenated with a separator. This leads to:
- Repetitive information
- Inconsistent formatting
- Difficulty correlating related issues

### 3. Severity Alignment

The security analyzer uses a structured severity system (Critical, High, Medium, Low, Info), while the sanity checker uses a simpler categorization (Issues, Warnings, Info). This makes it hard to prioritize findings.

## Proposed Integration Approach

### 1. Shared File Traversal

```python
def analyze_project(project_path):
    # Setup shared data structures
    all_files = {}
    
    # Single traversal of the codebase
    for file_path in traverse_files(project_path):
        # Read the file once
        content = read_file(file_path)
        all_files[file_path] = content
    
    # Run checks using the shared data
    sanity_results = run_sanity_checks(all_files)
    security_results = run_security_checks(all_files)
    
    # Generate unified report
    return generate_unified_report(sanity_results, security_results)
```

### 2. Unified Issue Model

Create a shared issue model that both systems can use:

```python
@dataclass
class CodeIssue:
    issue_id: str
    severity: SeverityLevel  # Enum with CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    snippet: Optional[str] = None
    issue_type: str = "quality"  # "quality" or "security"
    recommendations: List[str] = field(default_factory=list)
```

### 3. Integrated Reporting

Generate a unified report that groups findings by file, rather than by tool:

```python
def generate_unified_report(issues):
    # Group issues by file
    issues_by_file = {}
    for issue in issues:
        if issue.file_path not in issues_by_file:
            issues_by_file[issue.file_path] = []
        issues_by_file[issue.file_path].append(issue)
    
    # Generate report sections
    report = ["# AI Dev Toolkit Code Analysis Report", ""]
    
    # Executive summary (counts by severity and type)
    # ...
    
    # Critical and high issues across both tools
    # ...
    
    # File-by-file findings
    # ...
    
    return "\n".join(report)
```

### 4. Progressive Enhancement

The integration should support progressive enhancement, where users can:
1. Run just the sanity check (fast)
2. Run sanity check with basic security checks (medium)
3. Run full analysis with comprehensive security scanning (thorough)

## Implementation Plan

1. Create a new module `unified_analyzer.py` that implements the shared traversal and reporting
2. Refactor the sanity checker and security analyzer to expose their checks as importable functions
3. Update the MCP tool registration to provide both the original tools and the new unified analyzer
4. Add configuration options to control the depth of analysis

## Benefits

- **Improved Performance**: Single file traversal and shared data structures
- **Better Reporting**: Correlated findings make it easier to fix related issues
- **Configurable Depth**: Users can choose the appropriate level of analysis
- **Consistent Severity**: Unified severity model across all types of findings

## Timeline

This integration could be implemented in phases:
1. Create the unified issue model and reporting
2. Implement the shared file traversal
3. Refactor the existing tools to use the new model
4. Add the progressive analysis options

## Backwards Compatibility

The existing standalone tools would be maintained for backwards compatibility, with the unified analyzer available as an enhanced option.