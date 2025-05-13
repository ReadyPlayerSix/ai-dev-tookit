# Sanity Check Improvements

After analyzing the current implementation of `sanity_check_fixed.py`, I've identified several areas for improvement:

## 1. Error Handling and Robustness

### Current Issues:
- Uses bare `except` blocks in some places
- Limited error recovery in file operations
- Minimal validation of inputs

### Improvements:
- Add specific exception handling with clear error messages
- Implement better recovery mechanisms for file reading failures
- Add input validation for project paths and configuration options

## 2. Performance Optimization

### Current Issues:
- Reads files multiple times for different checks
- Traverses the codebase separately for each check
- Does not cache results between checks

### Improvements:
- Implement a shared file reader that caches file contents
- Use a single traversal for all checks
- Parallelize independent checks for larger codebases

## 3. Code Organization

### Current Issues:
- All checks are in one large class with limited separation of concerns
- Limited extension points for custom checks
- No clear plugin model for adding new checks

### Improvements:
- Refactor to use a modular check system
- Implement a plugin architecture for custom checks
- Separate the traversal, analysis, and reporting components

## 4. Check Coverage

### Current Issues:
- Focuses primarily on hardcoded paths and imports
- Limited checks for code quality issues
- No static type checking integration

### Improvements:
- Add integration with mypy for type checking
- Expand code quality checks (complexity, method length, etc.)
- Add checks for common patterns in AI/ML code

## 5. Reporting

### Current Issues:
- Report format is fixed markdown
- Limited grouping of related issues
- No way to filter or prioritize findings

### Improvements:
- Implement flexible report formatters (markdown, JSON, HTML)
- Group related issues by file, component, or issue type
- Add filtering and sorting options for findings

## 6. Configuration

### Current Issues:
- Limited configuration options
- Hardcoded exclusion paths
- No per-project configuration

### Improvements:
- Add configuration file support
- Implement per-project configuration
- Allow for check-specific configuration options

## 7. Integration with Development Workflow

### Current Issues:
- Runs as a standalone tool
- No CI/CD integration
- No incremental analysis support

### Improvements:
- Add pre-commit hook integration
- Implement incremental analysis (only check changed files)
- Support CI/CD pipeline configuration

## 8. Specific Code Improvements

### Path Reference Check

Current implementation uses simple string matching:

```python
def check_path_references(self):
    suspicious_patterns = ['src/', 'src\\\\', '../src', 'src.librarian', 'ai_librarian_server.py', '/src/mcp/']
    
    python_files = self._get_python_files()
    for file_path in python_files:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        for pattern in suspicious_patterns:
            if pattern in content:
                self.print_status(f"Possibly incorrect path reference in {rel_path}: {pattern}", "warning")
```

Improved implementation:

```python
def check_path_references(self):
    # Define patterns with context
    path_patterns = [
        {
            'pattern': r'[\'"]src/[^\'"]+[\'"]',
            'description': 'Hardcoded src/ path',
            'severity': 'warning',
            'context': 'import|open|path'
        },
        # More sophisticated patterns...
    ]
    
    python_files = self._get_python_files()
    for file_path in python_files:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        for pattern_def in path_patterns:
            # Check if pattern is within relevant context
            matches = re.finditer(pattern_def['pattern'], content)
            for match in matches:
                # Get surrounding context (20 chars before and after)
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 20)
                context_str = content[start:end]
                
                if re.search(pattern_def['context'], context_str):
                    # Get line number
                    line_number = content[:match.start()].count('\n') + 1
                    
                    self.add_issue(
                        file_path=file_path,
                        line_number=line_number,
                        severity=pattern_def['severity'],
                        description=pattern_def['description'],
                        snippet=context_str.strip()
                    )
```

### Improved Pylint Integration

Current implementation is limited:

```python
def try_run_pylint(self):
    # Check if pylint is installed
    result = subprocess.run(
        ["pylint", "--version"], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True,
        check=False
    )
    
    if result.returncode != 0:
        self.print_status("pylint not available - skipping linting checks", "info")
        return
    
    # Run basic pylint
    librarian_dir = os.path.join(self.root_dir, "aitoolkit", "librarian")
    if os.path.exists(librarian_dir):
        result = subprocess.run(
            ["pylint", librarian_dir, "--disable=all", "--enable=import-error,undefined-variable"],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
```

Improved implementation:

```python
def run_static_analysis(self):
    """Run various static analysis tools on the codebase."""
    self.print_status("Running static code analysis...", "info")
    
    # Dictionary of tools to try
    analysis_tools = {
        "pylint": {
            "check_cmd": ["pylint", "--version"],
            "run_cmd": lambda dir: ["pylint", dir, 
                                    "--disable=all", 
                                    "--enable=import-error,undefined-variable,unused-import,unused-argument"],
            "parse_output": self._parse_pylint_output
        },
        "mypy": {
            "check_cmd": ["mypy", "--version"],
            "run_cmd": lambda dir: ["mypy", dir, "--ignore-missing-imports"],
            "parse_output": self._parse_mypy_output
        },
        "flake8": {
            "check_cmd": ["flake8", "--version"],
            "run_cmd": lambda dir: ["flake8", dir, "--select=E9,F63,F7,F82"],
            "parse_output": self._parse_flake8_output
        }
    }
    
    # Try each tool
    for tool_name, tool_config in analysis_tools.items():
        try:
            # Check if tool is installed
            result = subprocess.run(
                tool_config["check_cmd"],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                self.print_status(f"{tool_name} not available - skipping", "info")
                continue
                
            # Run the tool on key directories
            dirs_to_check = [
                os.path.join(self.root_dir, "aitoolkit", "librarian"),
                os.path.join(self.root_dir, "aitoolkit", "mcp"),
                os.path.join(self.root_dir, "aitoolkit", "server")
            ]
            
            for check_dir in dirs_to_check:
                if not os.path.exists(check_dir):
                    continue
                    
                self.print_status(f"Running {tool_name} on {os.path.relpath(check_dir, self.root_dir)}", "info")
                
                cmd = tool_config["run_cmd"](check_dir)
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                # Parse and process the output
                issues = tool_config["parse_output"](result.stdout, check_dir)
                for issue in issues:
                    self.add_issue(**issue)
                    
        except Exception as e:
            self.print_status(f"Error running {tool_name}: {e}", "error")
```

## 9. Test Coverage

### Current Issues:
- No tests for the sanity checker itself
- No way to verify check correctness
- Manual verification required

### Improvements:
- Add unit tests for individual checks
- Create test fixtures with known issues
- Implement integration tests for the full checker

## Implementation Priority

1. Implement the shared file traversal and caching
2. Refactor the checker to use a modular check system
3. Improve the path reference check with better context analysis
4. Enhance the reporting with more flexible formatters
5. Add integration with additional static analysis tools
6. Implement configuration file support
7. Add test coverage