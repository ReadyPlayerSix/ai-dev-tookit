#!/usr/bin/env python3
"""
Server integration for the Security Analyzer

This module contains the integration code to connect the Security Analyzer
to the existing AI Librarian server, enhancing the sanity_check functionality
with professional security assessment capabilities.
"""

import os
import logging
from typing import Dict, Any, Optional

# Configure logger
logger = logging.getLogger("ai_librarian.security_analyzer_integration")

def apply_security_analyzer_integration(server_context: Dict[str, Any]) -> None:
    """
    Apply Security Analyzer integration to the server context
    
    Args:
        server_context: The server context dictionary
    """
    try:
        logger.info("Applying Security Analyzer integration to server...")
        
        # Import the Security Analyzer module
        from .security_analyzer import analyze_security
        
        # Add the security_analyze MCP tool to the server
        if "mcp" in server_context:
            mcp = server_context["mcp"]
            
            @mcp.tool
            def security_analyze(project_path: str) -> str:
                """
                Perform a comprehensive security analysis on the project codebase.
                
                This tool analyzes the project for potential security vulnerabilities and
                generates a detailed security report. The report identifies issues but does
                not suggest fixes or implementations, focusing solely on providing a
                professional assessment of the codebase's security posture.
                
                The analysis includes checking for:
                - Injection vulnerabilities (SQL, command, code)
                - Hardcoded secrets and credentials
                - Insecure deserialization
                - Weak cryptography
                - Path traversal vulnerabilities
                - Authentication and authorization issues
                - Insecure configuration settings
                - And many other security concerns
                
                The report categorizes issues by severity (Critical, High, Medium, Low, Info)
                and provides context including file paths and line numbers.
                
                Args:
                    project_path: The root directory of the project to analyze
                    
                Returns:
                    A formatted security analysis report
                """
                # Validate project path
                if not os.path.exists(project_path) or not os.path.isdir(project_path):
                    return f"Error: Invalid project path - {project_path} is not a valid directory"
                
                try:
                    # Lazy-load the security analyzer only when explicitly called
                    logger.info(f"Running security analysis on {project_path}")
                    report = analyze_security(project_path)
                    return report
                except Exception as e:
                    logger.error(f"Error performing security analysis: {str(e)}", exc_info=True)
                    return f"Error performing security analysis: {str(e)}"
            
            # Enhance the existing sanity_check function to include security analysis
            if "sanity_check" in server_context:
                original_sanity_check = server_context["sanity_check"]
                
                @mcp.tool
                def enhanced_sanity_check(project_path: str, create_artifact: bool = False, 
                                          include_security: bool = True) -> str:
                    """
                    Run a comprehensive code quality and security check on the project.
                    
                    This enhanced tool combines the original sanity check with security analysis,
                    providing a complete assessment of both code quality and security vulnerabilities.
                    
                    Quality checks include:
                    - Critical path verification
                    - Import validation
                    - Path reference analysis
                    - Deprecated function detection
                    - Duplicate functionality identification
                    - Misplaced files detection
                    - Static analysis with pylint (if available)
                    - AI Librarian self-validation
                    - Execution trace analysis
                    
                    Security checks include:
                    - Injection vulnerabilities (SQL, command, code)
                    - Hardcoded secrets and credentials
                    - Insecure deserialization
                    - Weak cryptography
                    - Path traversal vulnerabilities
                    - Authentication and authorization issues
                    - Insecure configuration settings
                    
                    Args:
                        project_path: The root directory of the project to check
                        create_artifact: Whether to create an artifact file with the results
                        include_security: Whether to include security analysis in the report
                        
                    Returns:
                        A formatted report with findings and recommendations
                    """
                    # First run the original sanity check
                    sanity_result = original_sanity_check(project_path, create_artifact)
                    
                    # If security analysis is not requested, return just the sanity check
                    if not include_security:
                        return sanity_result
                    
                    # Add security analysis
                    try:
                        security_result = analyze_security(project_path)
                        
                        # Combine the results
                        combined_report = f"{sanity_result}\n\n{'='*80}\n\nSECURITY ANALYSIS\n\n{security_result}"
                        return combined_report
                    except Exception as e:
                        logger.error(f"Error adding security analysis to sanity check: {str(e)}", exc_info=True)
                        return f"{sanity_result}\n\nSecurity Analysis Error: {str(e)}"
                
                # Replace the original sanity_check in the server context
                server_context["sanity_check"] = enhanced_sanity_check
                
            logger.info("Security Analyzer integration applied successfully")
        else:
            logger.error("Cannot integrate Security Analyzer: mcp server not found in context")
            
    except Exception as e:
        logger.error(f"Error applying Security Analyzer integration: {str(e)}", exc_info=True)

def analyze_project_security(project_path: str) -> str:
    """
    Analyze the security of a project directly
    
    This function can be called directly to perform security analysis
    without going through the MCP server.
    
    Args:
        project_path: Path to the project to analyze
        
    Returns:
        A formatted security analysis report
    """
    try:
        # Import the Security Analyzer
        from .security_analyzer import analyze_security
        
        # Run the analysis
        report = analyze_security(project_path)
        return report
        
    except Exception as e:
        logger.error(f"Error analyzing project security: {str(e)}", exc_info=True)
        return f"Error analyzing project security: {str(e)}"