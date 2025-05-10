#!/usr/bin/env python3
"""
Custom sanity check runner with artifact support.
"""

import os
import sys
import json
import logging
from pathlib import Path
import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sanity_checker")

def run_custom_sanity_check(project_path, create_artifact=False):
    """
    Run a custom sanity check without encoding issues.
    
    Args:
        project_path: Path to the project
        create_artifact: Whether to create an artifact
        
    Returns:
        The sanity check report as a string
    """
    # Import the sanity check manually to avoid any circular imports
    try:
        # First try to import the fixed version
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "aitoolkit", "librarian"))
        from sanity_check_fixed import SanityChecker
    except ImportError:
        # Fall back to the regular version
        from aitoolkit.librarian.sanity_check import SanityChecker
    
    # Run the sanity check
    try:
        checker = SanityChecker(project_path)
        issues, warnings, info = checker.check_all()
        
        # Format the report
        report = ["# AI Dev Toolkit Sanity Check Report", ""]
        
        # Count issues and warnings
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
        
        # Save the report to the project's diagnostics directory
        try:
            ai_ref_path = os.path.join(project_path, ".ai_reference")
            if os.path.exists(ai_ref_path):
                diagnostics_path = os.path.join(ai_ref_path, "diagnostics")
                os.makedirs(diagnostics_path, exist_ok=True)
                
                # Save the report with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                report_path = os.path.join(diagnostics_path, f"sanity_check_{timestamp}.md")
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(report))
                
                logger.info(f"Saved sanity check report to {report_path}")
        except Exception as e:
            logger.warning(f"Failed to save sanity check report: {e}")
        
        return "\n".join(report)
    except Exception as e:
        logger.error(f"Error running sanity check: {e}")
        return f"Error running sanity check: {e}"

if __name__ == "__main__":
    # Get project path from command line or use parent directory
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Run the sanity check
    report = run_custom_sanity_check(project_path)
    print(report)
