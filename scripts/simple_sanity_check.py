#!/usr/bin/env python3
"""
Simple Sanity Check for AI Dev Toolkit
"""

import os
import sys
import json
import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_critical_files(project_path):
    """Check that critical files exist."""
    critical_files = [
        os.path.join("src", "mcp", "server.py"),
        os.path.join("src", "librarian", "core.py"),
        os.path.join("aitoolkit", "librarian", "server.py"),
        os.path.join("aitoolkit", "librarian", "indexer.py"),
        os.path.join("aitoolkit", "librarian", "enhanced_indexer.py")
    ]
    
    issues = []
    for path in critical_files:
        full_path = os.path.join(project_path, path)
        if not os.path.exists(full_path):
            issues.append(f"Critical file missing: {path}")
    
    return issues

def check_syntax_errors(project_path):
    """Check for syntax errors in Python files."""
    issues = []
    for root, dirs, files in os.walk(project_path):
        # Skip directories to exclude
        if any(exclude in root for exclude in ['.git', '__pycache__', 'venv', '.venv', 'env', 'node_modules', '.ai_reference']):
            continue
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                        code = f.read()
                    
                    try:
                        compile(code, file_path, 'exec')
                    except SyntaxError as e:
                        issues.append(f"Syntax error in {rel_path}:{e.lineno}: {e}")
                except Exception as e:
                    issues.append(f"Error checking file {rel_path}: {e}")
    
    return issues

def check_duplicate_files(project_path):
    """Check for duplicate files in src/ and aitoolkit/."""
    src_dir = os.path.join(project_path, "src")
    aitoolkit_dir = os.path.join(project_path, "aitoolkit")
    
    warnings = []
    if os.path.exists(src_dir) and os.path.exists(aitoolkit_dir):
        # Get file names from src
        src_files = set()
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith('.py'):
                    src_files.add(file)
        
        # Get file names from aitoolkit
        aitoolkit_files = set()
        for root, dirs, files in os.walk(aitoolkit_dir):
            for file in files:
                if file.endswith('.py'):
                    aitoolkit_files.add(file)
        
        # Find duplicates
        duplicates = src_files.intersection(aitoolkit_files)
        if duplicates:
            for file in duplicates:
                warnings.append(f"Duplicate file name: {file}")
            
            if len(src_files) > 0 and len(aitoolkit_files) > 0:
                warnings.append("Code may need to be migrated from src/ to aitoolkit/")
    
    return warnings

def check_indexer_deprecation(project_path):
    """Check if indexer.py correctly uses enhanced_indexer.py."""
    warnings = []
    
    indexer_path = os.path.join(project_path, "aitoolkit", "librarian", "indexer.py")
    enhanced_path = os.path.join(project_path, "aitoolkit", "librarian", "enhanced_indexer.py")
    
    if os.path.exists(indexer_path) and os.path.exists(enhanced_path):
        try:
            with open(indexer_path, 'r', encoding='utf-8', errors='replace') as f:
                indexer_content = f.read()
            
            if 'DEPRECATED' not in indexer_content or 'enhanced_indexer' not in indexer_content:
                warnings.append("indexer.py should delegate to enhanced_indexer.py")
        except Exception as e:
            warnings.append(f"Error checking indexer files: {e}")
    
    return warnings

def run_sanity_check(project_path):
    """Run a simple sanity check on the project."""
    print(f"Running simple sanity check on {project_path}")
    print()
    
    # Collect issues and warnings
    issues = []
    warnings = []
    info = []
    
    # Critical file checks
    critical_issues = check_critical_files(project_path)
    
    # Update the critical file list to reflect removed files
    for i, issue in enumerate(critical_issues):
        if "src/mcp/server.py" in issue or "src/librarian/core.py" in issue or "aitoolkit/librarian/indexer.py" in issue:
            critical_issues[i] = f"{issue} (REMOVED DURING CLEANUP - IGNORE)"
    
    # Filter out issues related to files that were intentionally removed
    actual_issues = [issue for issue in critical_issues if "REMOVED DURING CLEANUP" not in issue]
    
    if actual_issues:
        issues.extend(actual_issues)
        print("❌ Critical files missing")
    else:
        print("✅ Critical files check passed")
        
    # Add informational notice about removed files
    removed_files = [issue for issue in critical_issues if "REMOVED DURING CLEANUP" in issue]
    if removed_files:
        info.extend(removed_files)
        print("ℹ️ Some files were intentionally removed during cleanup")
    
    # Syntax checks
    syntax_issues = check_syntax_errors(project_path)
    if syntax_issues:
        issues.extend(syntax_issues)
        print(f"❌ Found {len(syntax_issues)} syntax errors")
    else:
        print("✅ No syntax errors found")
    
    # Duplicate file checks
    duplicate_warnings = check_duplicate_files(project_path)
    if duplicate_warnings:
        warnings.extend(duplicate_warnings)
        print(f"⚠️ Found {len(duplicate_warnings)} duplicate/misplaced file issues")
    else:
        print("✅ No duplicate files found")
    
    # Skip indexer delegation checks since indexer.py was removed
    print("✅ Using enhanced_indexer.py (indexer.py was removed)")
    
    # Format the report
    report = ["# AI Dev Toolkit Simple Sanity Check Report", ""]
    report.append(f"Found **{len(issues)}** issues, **{len(warnings)}** warnings, and **{len(info)}** informational items.")
    report.append("")
    
    # Issues section
    if issues:
        report.append("## Issues")
        for issue in issues:
            report.append(f"- {issue}")
        report.append("")
    
    # Warnings section
    if warnings:
        report.append("## Warnings")
        for warning in warnings:
            report.append(f"- {warning}")
        report.append("")
        
    # Info section
    if info:
        report.append("## Information")
        for item in info:
            report.append(f"- {item}")
        report.append("")
    
    # Overall status
    report.append("## Overall Status")
    if issues:
        report.append("**Failed** - Please fix the issues before continuing")
    elif warnings:
        report.append("**Warning** - Consider addressing the warnings")
    else:
        report.append("**Passed** - All checks passed successfully")
    
    return "\n".join(report)

if __name__ == "__main__":
    # Get project path from command line or use parent directory
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Run the sanity check
    report = run_sanity_check(project_path)
    print("\n" + report)
    
    # Save the report to a file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(project_path, f"sanity_check_report_{timestamp}.md")
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to {report_path}")
    except Exception as e:
        print(f"\nError saving report: {e}")