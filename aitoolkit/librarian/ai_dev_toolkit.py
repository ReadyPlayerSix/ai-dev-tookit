#!/usr/bin/env python3
"""
AI Dev Toolkit Integration Module

This module integrates all components of the AI Dev Toolkit into a single unified system.
It provides one-stop initialization for both the AI Librarian and Tool Reference systems,
and establishes bidirectional references between them.

The implementation uses the simplified Tool Index system which provides dramatic 
performance improvements through a single-pass architecture with no subprocesses.

Usage:
    # Will be automatically imported by the AI Librarian server
    from aitoolkit.librarian.ai_dev_toolkit import initialize_ai_dev_toolkit
    
    result = initialize_ai_dev_toolkit("path/to/project")
"""

import os
import sys
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai-dev-toolkit")

# Import request helpers for robustness
try:
    from ..utils.request_helpers import robust_operation, with_retry, with_queue_clearing, with_timeout
except ImportError:
    logger.warning("Could not import request helpers, proceeding without robustness features")
    # Create stub decorators if imports fail
    def robust_operation(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def with_retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def with_queue_clearing(func):
        return func
    
    def with_timeout(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Import necessary components with clean imports
try:
    # Import AI Librarian components
    from .enhanced_indexer import initialize_enhanced_librarian
    from .enhanced_librarian_updater import update_project_librarian
    
    # Import Tool Reference component (using simplified implementation)
    from .simple_tool_index import initialize_tool_index
    
    # Import unified context components
    from .bidirectional_refs import build_bidirectional_references
    from .unified_context import build_unified_context
except ImportError as e:
    logger.error(f"Error importing components: {str(e)}")
    raise

# Apply robustness decorators to imported functions
initialize_enhanced_librarian = with_retry(max_retries=2)(initialize_enhanced_librarian)
update_project_librarian = with_retry(max_retries=2)(update_project_librarian)
initialize_tool_index = with_retry(max_retries=2)(initialize_tool_index)
build_bidirectional_references = with_retry(max_retries=2)(build_bidirectional_references)
build_unified_context = with_retry(max_retries=2)(build_unified_context)

@robust_operation(max_retries=3, timeout=120.0, clear_queue=True)
def initialize_ai_dev_toolkit(project_path: str) -> Dict[str, Any]:
    """
    Initialize the complete AI Dev Toolkit for a project.
    
    This is a one-stop initialization tool that sets up both the AI Librarian 
    (for code understanding) and the Tool Reference System (for tool awareness) 
    in a single operation. After running this tool, Claude will have complete 
    context awareness of both code components and available tools.
    
    Args:
        project_path: The root directory of the project
        
    Returns:
        Dictionary containing initialization results
    """
    try:
        # Log the start time for performance monitoring
        start_time = time.time()
        logger.info(f"Starting AI Dev Toolkit initialization for {project_path}")
        
        # Normalize the project path
        project_path = os.path.abspath(project_path)
        
        if not os.path.exists(project_path):
            return {
                "status": "error",
                "message": f"Project path does not exist: {project_path}"
            }
            
        results = {
            "status": "success",
            "project_path": project_path,
            "steps": [],
            "systems_initialized": [],
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "performance_metrics": {}
        }
        
        # Step 1: Initialize or update AI Librarian
        step_start = time.time()
        logger.info(f"Step 1: Initializing AI Librarian for {project_path}")
        ai_ref_path = os.path.join(project_path, ".ai_reference")
        
        if os.path.exists(ai_ref_path):
            # Update existing AI Librarian
            logger.info("AI Librarian directory exists, updating...")
            success, message = update_project_librarian(project_path)
        else:
            # Initialize new AI Librarian
            logger.info("Creating new AI Librarian...")
            message, file_count, component_count = initialize_enhanced_librarian(project_path)
            success = True
            message = f"{message} (Found {component_count} components in {file_count} files)"
        
        step_duration = time.time() - step_start
        results["performance_metrics"]["librarian_initialization"] = step_duration
        logger.info(f"AI Librarian initialization completed in {step_duration:.2f} seconds")
        
        results["steps"].append({
            "name": "ai_librarian_initialization",
            "success": success,
            "message": message,
            "duration_seconds": step_duration
        })
        
        if success:
            results["systems_initialized"].append("AI Librarian")
        else:
            logger.error(f"Failed to initialize AI Librarian: {message}")
            results["status"] = "partial_failure"
        
        # Step 2: Initialize or update Tool Reference System
        step_start = time.time()
        logger.info(f"Step 2: Initializing Tool Reference System for {project_path}")
        tool_ref_path = os.path.join(project_path, ".tool_reference")
        
        # Initialize the tool reference system using simple_tool_index
        tool_init_result = initialize_tool_index(project_path)
        
        # Process the result
        if isinstance(tool_init_result, dict):
            tool_init_success = tool_init_result.get("status") == "success"
            tool_init_message = tool_init_result.get("message", str(tool_init_result))
        else:
            # Handle string result case (for backward compatibility)
            tool_init_success = "Successfully initialized Tool Reference" in str(tool_init_result)
            tool_init_message = str(tool_init_result)
        
        step_duration = time.time() - step_start
        results["performance_metrics"]["tool_reference_initialization"] = step_duration
        logger.info(f"Tool Reference initialization completed in {step_duration:.2f} seconds")
        
        results["steps"].append({
            "name": "tool_reference_initialization",
            "success": tool_init_success,
            "message": tool_init_message if 'tool_init_message' in locals() else str(tool_init_result),
            "duration_seconds": step_duration
        })
        
        if tool_init_success:
            results["systems_initialized"].append("Tool Reference System")
        else:
            error_message = tool_init_message if 'tool_init_message' in locals() else str(tool_init_result)
            logger.error(f"Failed to initialize Tool Reference System: {error_message}")
            results["status"] = "partial_failure"
        
        # Step 3: Build bidirectional references if both systems are available
        if os.path.exists(ai_ref_path) and os.path.exists(tool_ref_path):
            step_start = time.time()
            logger.info(f"Step 3: Building bidirectional references")
            
            try:
                bidir_success = build_bidirectional_references(project_path)
                
                step_duration = time.time() - step_start
                results["performance_metrics"]["bidirectional_references"] = step_duration
                logger.info(f"Bidirectional references built in {step_duration:.2f} seconds")
                
                results["steps"].append({
                    "name": "bidirectional_references",
                    "success": bidir_success,
                    "message": "Successfully built bidirectional references" if bidir_success else "Failed to build bidirectional references",
                    "duration_seconds": step_duration
                })
                
                if bidir_success:
                    results["systems_initialized"].append("Bidirectional References")
                else:
                    logger.error("Failed to build bidirectional references")
                    results["status"] = "partial_failure"
            except Exception as e:
                step_duration = time.time() - step_start
                logger.error(f"Error building bidirectional references: {str(e)}")
                results["steps"].append({
                    "name": "bidirectional_references",
                    "success": False,
                    "message": f"Error building bidirectional references: {str(e)}",
                    "duration_seconds": step_duration
                })
                results["status"] = "partial_failure"
        else:
            # Skip bidirectional references if either system is missing
            missing_systems = []
            if not os.path.exists(ai_ref_path):
                missing_systems.append("AI Librarian")
            if not os.path.exists(tool_ref_path):
                missing_systems.append("Tool Reference System")
                
            results["steps"].append({
                "name": "bidirectional_references",
                "success": False,
                "skipped": True,
                "message": f"Skipped building bidirectional references because {' and '.join(missing_systems)} not available"
            })
        
        # Step 4: Build unified context
        step_start = time.time()
        logger.info(f"Step 4: Building unified context")
        try:
            unified_context = build_unified_context(project_path)
            
            step_duration = time.time() - step_start
            results["performance_metrics"]["unified_context"] = step_duration
            logger.info(f"Unified context built in {step_duration:.2f} seconds")
            
            # Add summary info about the context
            context_summary = {
                "components_count": len(unified_context.get("components", {})),
                "tools_count": len(unified_context.get("tools", {})),
                "relationships_count": len(unified_context.get("relationships", {})),
                "cross_references_count": len(unified_context.get("cross_references", {}))
            }
            
            results["steps"].append({
                "name": "unified_context",
                "success": True,
                "message": "Successfully built unified context",
                "context_summary": context_summary,
                "duration_seconds": step_duration
            })
            
            results["systems_initialized"].append("Unified Context")
        except Exception as e:
            step_duration = time.time() - step_start
            logger.error(f"Error building unified context: {str(e)}")
            results["steps"].append({
                "name": "unified_context",
                "success": False,
                "message": f"Error building unified context: {str(e)}",
                "duration_seconds": step_duration
            })
            results["status"] = "partial_failure"
        
        # Update end time and calculate total duration
        end_time = time.time()
        total_duration = end_time - start_time
        results["performance_metrics"]["total_duration"] = total_duration
        logger.info(f"Total AI Dev Toolkit initialization completed in {total_duration:.2f} seconds")
        
        results["end_time"] = datetime.now().isoformat()
        
        # Count successes and failures
        success_count = sum(1 for step in results["steps"] if step.get("success", False))
        failure_count = sum(1 for step in results["steps"] if not step.get("success", False) and not step.get("skipped", False))
        skipped_count = sum(1 for step in results["steps"] if step.get("skipped", False))
        
        results["summary"] = {
            "success_count": success_count,
            "failure_count": failure_count,
            "skipped_count": skipped_count,
            "systems_initialized_count": len(results["systems_initialized"])
        }
        
        # Create a user-friendly message
        if results["status"] == "success":
            results["message"] = f"Successfully initialized the complete AI Dev Toolkit for {project_path} in {total_duration:.2f} seconds. All {success_count} initialization steps completed successfully."
        else:
            results["message"] = f"Partially initialized the AI Dev Toolkit for {project_path} in {total_duration:.2f} seconds. {success_count} steps succeeded, {failure_count} failed, and {skipped_count} were skipped."
        
        # Save initialization record
        try:
            toolkit_init_record = {
                "last_initialized": datetime.now().isoformat(),
                "systems_initialized": results["systems_initialized"],
                "status": results["status"],
                "performance_metrics": results["performance_metrics"]
            }
            
            toolkit_record_path = os.path.join(project_path, ".ai_dev_toolkit.json")
            with open(toolkit_record_path, 'w', encoding='utf-8') as f:
                json.dump(toolkit_init_record, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save toolkit initialization record: {str(e)}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error initializing AI Dev Toolkit: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "status": "error",
            "message": f"Error initializing AI Dev Toolkit: {str(e)}",
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        results = initialize_ai_dev_toolkit(project_path)
        
        if results["status"] == "success":
            print(f"✅ {results['message']}")
            sys.exit(0)
        elif results["status"] == "partial_failure":
            print(f"⚠️ {results['message']}")
            sys.exit(2)
        else:
            print(f"❌ {results['message']}")
            sys.exit(1)
    else:
        print("Usage: python ai_dev_toolkit.py <project_path>")
        sys.exit(1)

