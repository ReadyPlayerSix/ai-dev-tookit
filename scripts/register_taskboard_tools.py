#!/usr/bin/env python3
"""
Register TaskBoard Tools Directly

This script directly registers the TaskBoard tools with the MCP server.
It can be used to add TaskBoard functionality to a running Claude Desktop session
without restarting the server.
"""

import os
import sys
import logging
import importlib.util
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("register_taskboard_tools")

def get_project_root():
    """Get the project root directory"""
    # Start with the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up one level to get project root
    project_root = os.path.dirname(current_dir)
    
    return project_root

def register_taskboard_tools():
    """Register TaskBoard tools with the MCP server"""
    try:
        # Get project root
        project_root = get_project_root()
        logger.info(f"Project root: {project_root}")
        
        # Import the task_board module
        task_board_path = os.path.join(
            project_root, "aitoolkit", "librarian", "task_board.py"
        )
        
        if not os.path.exists(task_board_path):
            logger.error(f"TaskBoard module not found: {task_board_path}")
            return False
        
        # Import the module
        spec = importlib.util.spec_from_file_location("task_board", task_board_path)
        task_board = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(task_board)
        
        # Get the server module
        server_path = os.path.join(
            project_root, "aitoolkit", "librarian", "server.py"
        )
        
        if not os.path.exists(server_path):
            logger.error(f"Server module not found: {server_path}")
            return False
        
        # Import the server module
        spec = importlib.util.spec_from_file_location("server", server_path)
        server = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(server)
        
        # Check if the MCP object is available
        if not hasattr(server, "mcp"):
            logger.error("MCP object not found in server module")
            return False
        
        # Get the MCP object
        mcp = server.mcp
        
        # Import the functions from task_board
        functions = [
            ("submit_background_task", task_board.submit_background_task),
            ("get_task_status_mcp", task_board.get_task_status_mcp),
            ("get_task_result_mcp", task_board.get_task_result_mcp),
            ("cancel_task_mcp", task_board.cancel_task_mcp),
            ("list_tasks_mcp", task_board.list_tasks_mcp),
            ("think", task_board.think)
        ]
        
        # Register each function with MCP
        for name, func in functions:
            # Create a wrapper function to register with MCP
            def create_wrapper(f):
                def wrapper(*args, **kwargs):
                    return f(*args, **kwargs)
                wrapper.__name__ = f.__name__
                wrapper.__doc__ = f.__doc__
                return wrapper
            
            # Register the function
            wrapped_func = create_wrapper(func)
            
            try:
                # Register directly with MCP
                if name == "get_task_status_mcp":
                    @mcp.tool()
                    def get_task_status(project_path: str, task_id: str) -> str:
                        """
                        Get the status of a background task
                        
                        Args:
                            project_path: Path to the project
                            task_id: ID of the task to check
                            
                        Returns:
                            Task status
                        """
                        return task_board.get_task_status_mcp(project_path, task_id)
                    
                    logger.info(f"Registered tool: get_task_status")
                elif name == "get_task_result_mcp":
                    @mcp.tool()
                    def get_task_result(project_path: str, task_id: str) -> str:
                        """
                        Get the result of a completed background task
                        
                        Args:
                            project_path: Path to the project
                            task_id: ID of the task to get the result for
                            
                        Returns:
                            Task result
                        """
                        return task_board.get_task_result_mcp(project_path, task_id)
                    
                    logger.info(f"Registered tool: get_task_result")
                elif name == "cancel_task_mcp":
                    @mcp.tool()
                    def cancel_task(project_path: str, task_id: str) -> str:
                        """
                        Cancel a pending background task
                        
                        Args:
                            project_path: Path to the project
                            task_id: ID of the task to cancel
                            
                        Returns:
                            Result of the cancellation attempt
                        """
                        return task_board.cancel_task_mcp(project_path, task_id)
                    
                    logger.info(f"Registered tool: cancel_task")
                elif name == "list_tasks_mcp":
                    @mcp.tool()
                    def list_tasks(project_path: str, status: str = None, task_type: str = None) -> str:
                        """
                        List background tasks
                        
                        Args:
                            project_path: Path to the project
                            status: Optional status filter ("pending", "running", "completed", "failed", "timeout", "cancelled")
                            task_type: Optional task type filter
                            
                        Returns:
                            List of tasks
                        """
                        return task_board.list_tasks_mcp(project_path, status, task_type)
                    
                    logger.info(f"Registered tool: list_tasks")
                elif name == "submit_background_task":
                    @mcp.tool()
                    def submit_background_task(project_path: str, task_type: str, parameters: dict, priority: str = "medium") -> str:
                        """
                        Submit a task to be processed asynchronously
                        
                        Args:
                            project_path: Path to the project
                            task_type: Type of task (e.g., "code_analysis", "semantic_search")
                            parameters: Parameters for the task
                            priority: Priority of the task ("high", "medium", "low")
                            
                        Returns:
                            Task ID
                        """
                        return task_board.submit_background_task(project_path, task_type, parameters, priority)
                    
                    logger.info(f"Registered tool: submit_background_task")
                elif name == "think":
                    @mcp.tool()
                    def think(project_path: str, query: str, priority: str = "high") -> str:
                        """
                        The 'think' function starts a deep analysis task that processes complex problems
                        
                        Args:
                            project_path: Path to the project
                            query: The question or problem to analyze
                            priority: Priority of the task ("high", "medium", "low")
                            
                        Returns:
                            Task ID for the thinking task
                        """
                        return task_board.think(project_path, query, priority)
                    
                    logger.info(f"Registered tool: think")
                
            except Exception as e:
                logger.error(f"Error registering function {name}: {e}")
                continue
        
        logger.info("TaskBoard tools registered successfully")
        print("\n===================================================")
        print("TaskBoard Tools Registration Complete!")
        print("===================================================")
        print("\nThe following tools are now available:")
        print("- think: Start a deep analysis task")
        print("- submit_background_task: Submit a custom background task")
        print("- get_task_status: Check the status of a task")
        print("- get_task_result: Get the result of a completed task")
        print("- cancel_task: Cancel a pending task")
        print("- list_tasks: List all tasks with filtering options")
        print("\nThese tools allow long-running operations to be processed")
        print("in the background without causing timeouts.")
        print("\nTo use them, send a message to your Claude Desktop session")
        print("to refresh the connection.")
        
        return True
        
    except Exception as e:
        logger.error(f"Error registering TaskBoard tools: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    register_taskboard_tools()