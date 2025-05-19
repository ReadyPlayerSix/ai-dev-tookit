#!/usr/bin/env python3
"""
AI Dev Toolkit TaskBoard System

A modular, asynchronous task processing system that connects mini-librarians
with long-running operations to prevent timeouts and improve responsiveness.
"""

import os
import json
import time
import uuid
import queue
import logging
import threading
import traceback
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta

# Local imports
from .execution_tracer import get_tracer

# Configure logger
logger = logging.getLogger("ai_librarian.task_board")


class TaskStatus(Enum):
    """Status of a TaskBoard task"""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    TIMEOUT = auto()
    CANCELLED = auto()


class TaskPriority(Enum):
    """Priority of a TaskBoard task"""
    HIGH = 0
    MEDIUM = 1
    LOW = 2


@dataclass
class TaskResult:
    """Result of a TaskBoard task"""
    success: bool
    data: Any
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskBoard:
    """
    TaskBoard for managing async tasks and communicating with mini-librarians
    """
    project_path: str
    max_workers: int = 1  # Reduced from 4 to prevent timeout issues
    task_timeout: int = 120  # seconds
    
    # Task queues and storage
    task_queue: "queue.PriorityQueue" = field(default_factory=queue.PriorityQueue)
    tasks: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    results: Dict[str, TaskResult] = field(default_factory=dict)
    _cancelled_tasks: set = field(default_factory=set)  # Track cancelled tasks
    
    # Locks for thread safety
    task_lock: threading.Lock = field(default_factory=threading.Lock)
    
    # Workers
    workers: List[threading.Thread] = field(default_factory=list)
    running: bool = True
    
    def __post_init__(self):
        """Initialize the TaskBoard"""
        # Create storage directory
        self.storage_path = os.path.join(self.project_path, ".ai_reference", "task_board")
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Create workers
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"TaskBoard-Worker-{i}",
                daemon=False
            )
            self.workers.append(worker)
            worker.start()
        
        logger.info(f"TaskBoard initialized with {self.max_workers} workers for {self.project_path}")
        
        # Load any pending tasks from storage
        self._load_tasks()
    
    def _worker_loop(self):
        """Worker thread loop for processing tasks"""
        while self.running:
            try:
                # Get task from queue with timeout to allow for shutdown
                try:
                    priority, task_id, _ = self.task_queue.get(timeout=1.0)
                    
                    # Skip tasks that have been cancelled or already processed
                    with self.task_lock:
                        if task_id not in self.tasks or self.tasks[task_id]["status"] != TaskStatus.PENDING:
                            self.task_queue.task_done()
                            continue
                        
                        # Mark task as running
                        self.tasks[task_id]["status"] = TaskStatus.RUNNING
                        self.tasks[task_id]["started_at"] = datetime.now().isoformat()
                        
                        # Save task state
                        self._save_task(task_id)
                    
                    # Execute task
                    self._execute_task(task_id)
                    
                    # Mark task as completed
                    self.task_queue.task_done()
                    
                except queue.Empty:
                    continue
                
            except Exception as e:
                logger.error(f"Error in worker thread: {str(e)}")
                traceback.print_exc()
                
                # Sleep a bit to avoid thrashing
                time.sleep(0.1)
    
    def _execute_task(self, task_id: str):
        """Execute a task by its ID"""
        # Get task info
        try:
            with self.task_lock:
                task_info = self.tasks.get(task_id)
                if not task_info:
                    logger.error(f"Task {task_id} not found")
                    return
            
            # Record start time
            start_time = time.time()
            
            # Extract task details
            task_type = task_info["task_type"]
            params = task_info["parameters"]
            timeout = task_info.get("timeout", self.task_timeout)
            
            # Get handler for task type
            handler = self._get_task_handler(task_type)
            if not handler:
                raise ValueError(f"No handler found for task type: {task_type}")
                
            # Execute with timeout in a separate thread
            result_queue = queue.Queue()
            
            def execute_with_handler():
                try:
                    result = handler(params)
                    result_queue.put((True, result, None))
                except Exception as e:
                    result_queue.put((False, None, str(e)))
            
            # Run handler in thread
            handler_thread = threading.Thread(target=execute_with_handler)
            handler_thread.daemon = True
            handler_thread.start()
            
            # Wait for result with timeout
            try:
                success, result_data, error = result_queue.get(timeout=timeout)
                execution_time_ms = (time.time() - start_time) * 1000
                
                # Create task result
                task_result = TaskResult(
                    success=success,
                    data=result_data,
                    error_message=error,
                    execution_time_ms=execution_time_ms
                )
                
                # Update task status
                with self.task_lock:
                    self.tasks[task_id]["status"] = TaskStatus.COMPLETED if success else TaskStatus.FAILED
                    self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
                    self.tasks[task_id]["execution_time_ms"] = execution_time_ms
                    
                    if not success:
                        self.tasks[task_id]["error"] = error
                    
                    # Store result
                    self.results[task_id] = task_result
                    
                    # Save task state
                    self._save_task(task_id)
                
                # Notify tracer
                tracer = get_tracer(self.project_path)
                tracer.record_operation(
                    operation=f"taskboard_{task_type}",
                    parameters=params,
                    result_status="success" if success else "error",
                    execution_time_ms=execution_time_ms,
                    error_message=error,
                    metadata={"task_id": task_id}
                )
                
            except queue.Empty:
                # Task timed out
                with self.task_lock:
                    self.tasks[task_id]["status"] = TaskStatus.TIMEOUT
                    self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
                    self.tasks[task_id]["error"] = f"Task timed out after {timeout} seconds"
                    
                    # Create timeout result
                    execution_time_ms = (time.time() - start_time) * 1000
                    self.tasks[task_id]["execution_time_ms"] = execution_time_ms
                    
                    self.results[task_id] = TaskResult(
                        success=False,
                        data=None,
                        error_message=f"Task timed out after {timeout} seconds",
                        execution_time_ms=execution_time_ms
                    )
                    
                    # Save task state
                    self._save_task(task_id)
                
                # Notify tracer
                tracer = get_tracer(self.project_path)
                tracer.record_operation(
                    operation=f"taskboard_{task_type}",
                    parameters=params,
                    result_status="timeout",
                    execution_time_ms=timeout * 1000,
                    error_message=f"Task timed out after {timeout} seconds",
                    metadata={"task_id": task_id}
                )
                
                # Add thread cleanup on timeout
                if handler_thread.is_alive():
                    logger.warning(f"Handler thread for task {task_id} is still running after timeout")
                    # We can't forcibly terminate threads in Python, but we can try to set a flag
                    # that the handler can check to know it should exit early
        
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            traceback.print_exc()
            
            # Update task status
            with self.task_lock:
                self.tasks[task_id]["status"] = TaskStatus.FAILED
                self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
                self.tasks[task_id]["error"] = str(e)
                
                # Save task state
                self._save_task(task_id)
    
    def _get_task_handler(self, task_type: str) -> Optional[Callable]:
        """Get the handler function for a task type"""
        # This would connect to the mini-librarian system
        # For now, use some placeholder handlers
        from .server import determine_mini_librarians
        
        # Connect to mini-librarian system
        try:
            mini_librarians = determine_mini_librarians(task_type)
            if not mini_librarians:
                logger.warning(f"No mini-librarians found for task type: {task_type}")
                return None
                
            # For now, return a placeholder handler
            def handler(params):
                logger.info(f"Executing {task_type} with mini-librarians: {mini_librarians}")
                
                # Do some work with the mini-librarians
                time.sleep(0.1)  # Simulate work
                
                return {
                    "status": "success",
                    "task_type": task_type,
                    "mini_librarians_used": mini_librarians,
                    "result": f"Simulated execution of {task_type}"
                }
                
            return handler
            
        except Exception as e:
            logger.error(f"Error getting task handler for {task_type}: {str(e)}")
            return None
    
    def submit_task(self, 
                  task_type: str, 
                  parameters: Dict[str, Any], 
                  priority: TaskPriority = TaskPriority.MEDIUM,
                  timeout: Optional[int] = None) -> str:
        """
        Submit a task to the TaskBoard
        
        Args:
            task_type: Type of task to execute
            parameters: Parameters for the task
            priority: Priority of the task
            timeout: Optional timeout in seconds (overrides default)
            
        Returns:
            Task ID
        """
        # Generate task ID
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        
        # Create task info
        task_info = {
            "id": task_id,
            "task_type": task_type,
            "parameters": parameters,
            "priority": priority.value,
            "status": TaskStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "timeout": timeout or self.task_timeout
        }
        
        # Store task info
        with self.task_lock:
            self.tasks[task_id] = task_info
            
            # Save task state
            self._save_task(task_id)
        
        # Add to queue
        self.task_queue.put((priority.value, task_id, time.time()))
        
        logger.info(f"Submitted task {task_id} of type {task_type} with priority {priority.name}")
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task"""
        with self.task_lock:
            task_info = self.tasks.get(task_id)
            if not task_info:
                return None
                
            # Include result if available
            result = self.results.get(task_id)
            if result:
                task_info["result"] = asdict(result)
                
            return task_info
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        with self.task_lock:
            task_info = self.tasks.get(task_id)
            if not task_info:
                return False
                
            # Can only cancel pending tasks
            if task_info["status"] != TaskStatus.PENDING:
                return False
                
            # Mark task as cancelled
            task_info["status"] = TaskStatus.CANCELLED
            task_info["cancelled_at"] = datetime.now().isoformat()
            
            # Save task state
            self._save_task(task_id)
                
            return True
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get the result of a completed task"""
        with self.task_lock:
            return self.results.get(task_id)
    
    def list_tasks(self, 
                  status: Optional[TaskStatus] = None, 
                  task_type: Optional[str] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """List tasks with optional filtering"""
        with self.task_lock:
            tasks = []
            
            for task_id, task_info in self.tasks.items():
                # Apply filters
                if status and task_info["status"] != status:
                    continue
                    
                if task_type and task_info["task_type"] != task_type:
                    continue
                    
                tasks.append(task_info.copy())
                
                # Include result if available
                result = self.results.get(task_id)
                if result:
                    tasks[-1]["result"] = asdict(result)
                    
                # Apply limit
                if len(tasks) >= limit:
                    break
                    
            return tasks
    
    def _save_task(self, task_id: str):
        """Save task state to disk"""
        try:
            task_info = self.tasks[task_id]
            
            # Create task directory if it doesn't exist
            tasks_dir = os.path.join(self.storage_path, "tasks")
            os.makedirs(tasks_dir, exist_ok=True)
            
            # Save task info
            task_file = os.path.join(tasks_dir, f"{task_id}.json")
            with open(task_file, 'w', encoding='utf-8') as f:
                # Include result if available
                task_data = task_info.copy()
                result = self.results.get(task_id)
                if result:
                    task_data["result"] = asdict(result)
                    
                json.dump(task_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving task {task_id}: {str(e)}")
    
    def _load_tasks(self):
        """Load tasks from disk"""
        try:
            # Get task directory
            tasks_dir = os.path.join(self.storage_path, "tasks")
            if not os.path.exists(tasks_dir):
                return
                
            # Load all task files
            for filename in os.listdir(tasks_dir):
                if not filename.endswith('.json'):
                    continue
                    
                try:
                    task_file = os.path.join(tasks_dir, filename)
                    with open(task_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                        
                    task_id = task_data["id"]
                    
                    # Extract result if present
                    result_data = task_data.pop("result", None)
                    
                    # Store task info
                    with self.task_lock:
                        self.tasks[task_id] = task_data
                        
                        # Restore result if present
                        if result_data:
                            self.results[task_id] = TaskResult(**result_data)
                            
                        # Re-queue pending tasks
                        if task_data["status"] == TaskStatus.PENDING:
                            priority = task_data["priority"]
                            self.task_queue.put((priority, task_id, time.time()))
                            
                except Exception as e:
                    logger.error(f"Error loading task file {filename}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error loading tasks: {str(e)}")
    
    def cleanup(self):
        """Clean up old tasks"""
        with self.task_lock:
            # Get cutoff time
            cutoff = datetime.now() - timedelta(days=7)
            
            # Find completed tasks older than cutoff
            to_remove = []
            for task_id, task_info in self.tasks.items():
                # Skip pending and running tasks
                if task_info["status"] in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                    continue
                    
                # Check completion time
                completed_at = task_info.get("completed_at") or task_info.get("cancelled_at")
                if not completed_at:
                    continue
                    
                completed_time = datetime.fromisoformat(completed_at)
                if completed_time < cutoff:
                    to_remove.append(task_id)
            
            # Remove old tasks
            for task_id in to_remove:
                # Remove from memory
                self.tasks.pop(task_id, None)
                self.results.pop(task_id, None)
                
                # Remove from disk
                try:
                    task_file = os.path.join(self.storage_path, "tasks", f"{task_id}.json")
                    if os.path.exists(task_file):
                        os.remove(task_file)
                except Exception as e:
                    logger.error(f"Error removing task file for {task_id}: {str(e)}")
    
    def shutdown(self):
        """Shutdown the TaskBoard"""
        logger.info("Shutting down TaskBoard...")
        
        # Signal workers to stop
        self.running = False
        
        # Wait for workers to finish (with timeout)
        for worker in self.workers:
            worker.join(timeout=1.0)
        
        logger.info("TaskBoard shutdown complete")


# Singleton pattern for the TaskBoard
_task_boards = {}

def get_task_board(project_path: str) -> TaskBoard:
    """
    Get or create a TaskBoard for the specified project.
    
    Args:
        project_path: The project path
        
    Returns:
        TaskBoard instance
    """
    if project_path not in _task_boards:
        _task_boards[project_path] = TaskBoard(project_path)
    
    return _task_boards[project_path]


# === MCP Tool Functions ===

def submit_background_task(project_path: str, 
                          task_type: str, 
                          parameters: Dict[str, Any],
                          priority: str = "medium") -> str:
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
    # Map priority string to enum
    priority_map = {
        "high": TaskPriority.HIGH,
        "medium": TaskPriority.MEDIUM,
        "low": TaskPriority.LOW
    }
    priority_enum = priority_map.get(priority.lower(), TaskPriority.MEDIUM)
    
    # Get TaskBoard and submit task
    task_board = get_task_board(project_path)
    task_id = task_board.submit_task(
        task_type=task_type,
        parameters=parameters,
        priority=priority_enum
    )
    
    return f"Task submitted with ID: {task_id}\nType: {task_type}\nPriority: {priority}"

def get_task_status_mcp(project_path: str, task_id: str) -> str:
    """
    Get the status of a background task
    
    Args:
        project_path: Path to the project
        task_id: ID of the task to check
        
    Returns:
        Task status
    """
    # Get TaskBoard and check status
    task_board = get_task_board(project_path)
    task_info = task_board.get_task_status(task_id)
    
    if not task_info:
        return f"Task {task_id} not found"
    
    # Format status response
    status = task_info["status"]
    created_at = task_info["created_at"]
    
    response = [
        f"Task ID: {task_id}",
        f"Type: {task_info['task_type']}",
        f"Status: {status}",
        f"Created: {created_at}"
    ]
    
    # Add additional status details
    if status == TaskStatus.RUNNING:
        started_at = task_info.get("started_at")
        if started_at:
            response.append(f"Started: {started_at}")
            
    elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TIMEOUT]:
        completed_at = task_info.get("completed_at")
        if completed_at:
            response.append(f"Completed: {completed_at}")
            
        execution_time = task_info.get("execution_time_ms")
        if execution_time:
            response.append(f"Execution time: {execution_time:.2f}ms")
            
        if status == TaskStatus.FAILED:
            error = task_info.get("error")
            if error:
                response.append(f"Error: {error}")
                
    elif status == TaskStatus.CANCELLED:
        cancelled_at = task_info.get("cancelled_at")
        if cancelled_at:
            response.append(f"Cancelled: {cancelled_at}")
    
    # Include result summary if available
    if "result" in task_info:
        result = task_info["result"]
        response.append("\nResult Summary:")
        
        if result["success"]:
            if isinstance(result["data"], dict) and "status" in result["data"]:
                response.append(f"Status: {result['data']['status']}")
                
            if isinstance(result["data"], dict) and "result" in result["data"]:
                response.append(f"Result: {result['data']['result']}")
        else:
            response.append(f"Error: {result.get('error_message', 'Unknown error')}")
    
    return "\n".join(response)

def get_task_result_mcp(project_path: str, task_id: str) -> str:
    """
    Get the result of a completed background task
    
    Args:
        project_path: Path to the project
        task_id: ID of the task to get the result for
        
    Returns:
        Task result
    """
    # Get TaskBoard and check result
    task_board = get_task_board(project_path)
    task_info = task_board.get_task_status(task_id)
    
    if not task_info:
        return f"Task {task_id} not found"
    
    # Check if task is completed
    status = task_info["status"]
    if status != TaskStatus.COMPLETED:
        return f"Task {task_id} is not completed (current status: {status})"
    
    # Get result
    result = task_board.get_task_result(task_id)
    if not result:
        return f"No result found for task {task_id}"
    
    # Format result response
    response = [
        f"Task {task_id} Result:",
        f"Success: {result.success}",
        f"Execution Time: {result.execution_time_ms:.2f}ms"
    ]
    
    # Add result data
    if result.success:
        response.append("\nResult Data:")
        
        # Format result data
        if isinstance(result.data, dict):
            for key, value in result.data.items():
                response.append(f"{key}: {value}")
        else:
            response.append(str(result.data))
    else:
        response.append(f"\nError: {result.error_message}")
    
    return "\n".join(response)

def cancel_task_mcp(project_path: str, task_id: str) -> str:
    """
    Cancel a pending background task
    
    Args:
        project_path: Path to the project
        task_id: ID of the task to cancel
        
    Returns:
        Result of the cancellation attempt
    """
    # Get TaskBoard and cancel task
    task_board = get_task_board(project_path)
    success = task_board.cancel_task(task_id)
    
    if success:
        return f"Task {task_id} has been cancelled"
    else:
        task_info = task_board.get_task_status(task_id)
        if not task_info:
            return f"Task {task_id} not found"
        else:
            return f"Task {task_id} could not be cancelled (current status: {task_info['status']})"

def list_tasks_mcp(project_path: str, status: str = None, task_type: str = None) -> str:
    """
    List background tasks
    
    Args:
        project_path: Path to the project
        status: Optional status filter ("pending", "running", "completed", "failed", "timeout", "cancelled")
        task_type: Optional task type filter
        
    Returns:
        List of tasks
    """
    # Get TaskBoard
    task_board = get_task_board(project_path)
    
    # Map status string to enum
    status_enum = None
    if status:
        status_map = {
            "pending": TaskStatus.PENDING,
            "running": TaskStatus.RUNNING,
            "completed": TaskStatus.COMPLETED,
            "failed": TaskStatus.FAILED,
            "timeout": TaskStatus.TIMEOUT,
            "cancelled": TaskStatus.CANCELLED
        }
        status_enum = status_map.get(status.lower())
        if not status_enum:
            return f"Invalid status: {status}. Valid values are: pending, running, completed, failed, timeout, cancelled"
    
    # List tasks
    tasks = task_board.list_tasks(status=status_enum, task_type=task_type)
    
    if not tasks:
        filters = []
        if status:
            filters.append(f"status={status}")
        if task_type:
            filters.append(f"task_type={task_type}")
        
        if filters:
            return f"No tasks found with filters: {', '.join(filters)}"
        else:
            return "No tasks found"
    
    # Format response
    response = [f"Found {len(tasks)} tasks:"]
    
    for task in tasks:
        # Basic task info
        task_line = f"ID: {task['id']} | Type: {task['task_type']} | Status: {task['status']}"
        
        # Add time info
        if task["status"] == TaskStatus.PENDING:
            # Show waiting time
            created = datetime.fromisoformat(task["created_at"])
            waiting_time = datetime.now() - created
            task_line += f" | Waiting: {waiting_time.total_seconds():.1f}s"
            
        elif task["status"] == TaskStatus.RUNNING:
            # Show running time
            started = datetime.fromisoformat(task["started_at"])
            running_time = datetime.now() - started
            task_line += f" | Running: {running_time.total_seconds():.1f}s"
            
        elif task["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TIMEOUT]:
            # Show execution time
            if "execution_time_ms" in task:
                task_line += f" | Execution: {task['execution_time_ms']:.1f}ms"
        
        response.append(task_line)
    
    return "\n".join(response)

def task_deep_analysis(project_path: str, query: str, priority: str = "high") -> str:
    """
    Start a deep analysis task that processes complex problems asynchronously
    
    Unlike the 'think' tool which provides immediate reflection,
    this function submits a background task for deeper analysis that
    may take some time to complete.
    
    Args:
        project_path: Path to the project
        query: The question or problem to analyze
        priority: Priority of the task ("high", "medium", "low")
        
    Returns:
        Task ID for the deep analysis task
    """
    # Parameters for the deep analysis task
    parameters = {
        "query": query,
        "mode": "comprehensive",
        "use_mini_librarians": True
    }
    
    # Submit task
    task_board = get_task_board(project_path)
    task_id = task_board.submit_task(
        task_type="deep_analysis",  # Changed from "think" to avoid confusion
        parameters=parameters,
        priority=TaskPriority.HIGH if priority.lower() == "high" else TaskPriority.MEDIUM
    )
    
    return f"Deep analysis task submitted with ID: {task_id}\n\nThis will analyze: '{query}'\n\nYou can check the status with get_task_status(\"{project_path}\", \"{task_id}\")"