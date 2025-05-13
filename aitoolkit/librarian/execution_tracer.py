#!/usr/bin/env python3
"""
AI Librarian Execution Tracer

This module provides execution tracing capabilities for the AI Librarian,
allowing it to learn from usage patterns and improve over time.
"""

import os
import json
import time
import datetime
import threading
import logging
from typing import Dict, List, Any, Optional, Tuple, Union

# Configure logger
logger = logging.getLogger("ai_librarian.execution_tracer")

class ExecutionTracer:
    """
    Records and analyzes AI Librarian operations to improve performance and accuracy.
    """
    
    def __init__(self, project_path: str):
        """
        Initialize the execution tracer.
        
        Args:
            project_path: The root directory of the project
        """
        self.project_path = project_path
        self.ai_ref_path = os.path.join(project_path, ".ai_reference")
        self.diagnostics_path = os.path.join(self.ai_ref_path, "diagnostics")
        self.trace_path = os.path.join(self.diagnostics_path, "execution_traces")
        
        # Create trace directory if it doesn't exist
        os.makedirs(self.trace_path, exist_ok=True)
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Current trace batch
        self.current_traces = []
        self.last_flush_time = time.time()
        
        logger.info(f"Initialized execution tracer for {project_path}")
    
    def record_operation(self, 
                        operation: str, 
                        parameters: Dict[str, Any], 
                        result_status: str,
                        execution_time_ms: float,
                        error_message: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record an operation execution.
        
        Args:
            operation: The operation name (e.g., "query_component", "find_implementation")
            parameters: The parameters passed to the operation
            result_status: The status of the execution ("success", "error", "warning")
            execution_time_ms: Execution time in milliseconds
            error_message: Error message if applicable
            metadata: Additional metadata about the execution
        """
        trace = {
            "timestamp": datetime.datetime.now().isoformat(),
            "operation": operation,
            "parameters": parameters,
            "result_status": result_status,
            "execution_time_ms": execution_time_ms,
            "error_message": error_message,
            "metadata": metadata or {}
        }
        
        with self.lock:
            self.current_traces.append(trace)
            
            # Flush if we have a lot of traces or it's been a while
            if len(self.current_traces) >= 10 or (time.time() - self.last_flush_time) > 300:
                self._flush_traces()
    
    def _flush_traces(self) -> None:
        """Flush current traces to disk."""
        if not self.current_traces:
            return
            
        try:
            # Generate a timestamped filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"trace_batch_{timestamp}.json"
            file_path = os.path.join(self.trace_path, filename)
            
            # Write traces to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "batch_id": timestamp,
                    "project_path": self.project_path,
                    "traces": self.current_traces
                }, f, indent=2)
            
            # Clear current traces and update last flush time
            self.current_traces = []
            self.last_flush_time = time.time()
            
            logger.debug(f"Flushed execution traces to {file_path}")
        except Exception as e:
            logger.error(f"Error flushing execution traces: {str(e)}")
    
    def analyze_traces(self, time_period: str = "day") -> Dict[str, Any]:
        """
        Analyze execution traces to identify patterns.
        
        Args:
            time_period: The time period to analyze ("day", "week", "all")
            
        Returns:
            Analysis results
        """
        traces = self._load_traces(time_period)
        
        if not traces:
            return {"status": "no_data", "message": "No traces found for the specified period"}
        
        # Analysis results
        results = {
            "operation_counts": {},
            "error_rates": {},
            "average_execution_times": {},
            "most_queried_components": {},
            "common_errors": [],
            "optimization_opportunities": []
        }
        
        # Analyze operations
        for trace in traces:
            op = trace["operation"]
            status = trace["result_status"]
            exec_time = trace["execution_time_ms"]
            
            # Count operations
            if op not in results["operation_counts"]:
                results["operation_counts"][op] = 0
                results["error_rates"][op] = {"total": 0, "errors": 0}
                results["average_execution_times"][op] = {"total_time": 0, "count": 0}
            
            results["operation_counts"][op] += 1
            results["error_rates"][op]["total"] += 1
            
            if status == "error":
                results["error_rates"][op]["errors"] += 1
                
                # Track common errors
                if trace.get("error_message"):
                    results["common_errors"].append({
                        "operation": op,
                        "message": trace["error_message"],
                        "parameters": trace["parameters"]
                    })
            
            # Track execution times
            results["average_execution_times"][op]["total_time"] += exec_time
            results["average_execution_times"][op]["count"] += 1
            
            # Track queried components
            if op == "query_component" and "component_name" in trace["parameters"]:
                component = trace["parameters"]["component_name"]
                if component not in results["most_queried_components"]:
                    results["most_queried_components"][component] = 0
                results["most_queried_components"][component] += 1
        
        # Calculate error rates and average execution times
        for op in results["error_rates"]:
            total = results["error_rates"][op]["total"]
            errors = results["error_rates"][op]["errors"]
            results["error_rates"][op] = round((errors / total) * 100, 2) if total > 0 else 0
            
            total_time = results["average_execution_times"][op]["total_time"]
            count = results["average_execution_times"][op]["count"]
            results["average_execution_times"][op] = round(total_time / count, 2) if count > 0 else 0
        
        # Sort most queried components
        results["most_queried_components"] = dict(
            sorted(
                results["most_queried_components"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        )
        
        # Identify optimization opportunities
        for op, error_rate in results["error_rates"].items():
            if error_rate > 10:
                results["optimization_opportunities"].append({
                    "operation": op,
                    "issue": "high_error_rate",
                    "error_rate": error_rate,
                    "suggestion": "Review error patterns and improve error handling"
                })
        
        for op, avg_time in results["average_execution_times"].items():
            if avg_time > 1000:  # more than 1 second
                results["optimization_opportunities"].append({
                    "operation": op,
                    "issue": "slow_execution",
                    "avg_time_ms": avg_time,
                    "suggestion": "Optimize for better performance"
                })
        
        return {
            "status": "success",
            "period": time_period,
            "trace_count": len(traces),
            "results": results
        }
    
    def _load_traces(self, time_period: str) -> List[Dict[str, Any]]:
        """
        Load traces for the specified time period.
        
        Args:
            time_period: The time period to load traces for
            
        Returns:
            List of traces
        """
        traces = []
        
        try:
            # Flush any pending traces
            with self.lock:
                self._flush_traces()
            
            # Calculate the cutoff time
            now = datetime.datetime.now()
            if time_period == "day":
                cutoff = now - datetime.timedelta(days=1)
            elif time_period == "week":
                cutoff = now - datetime.timedelta(weeks=1)
            else:  # all
                cutoff = datetime.datetime.min
            
            # Load trace files
            for filename in os.listdir(self.trace_path):
                if not filename.endswith('.json'):
                    continue
                
                file_path = os.path.join(self.trace_path, filename)
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_time >= cutoff:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "traces" in data:
                            traces.extend(data["traces"])
        
        except Exception as e:
            logger.error(f"Error loading traces: {str(e)}")
        
        return traces
    
    def generate_diagnostics_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive diagnostics report based on execution traces.
        
        Returns:
            Diagnostics report
        """
        # Analyze recent traces
        day_analysis = self.analyze_traces("day")
        week_analysis = self.analyze_traces("week")
        all_analysis = self.analyze_traces("all")
        
        # Generate report
        report = {
            "generated_at": datetime.datetime.now().isoformat(),
            "project_path": self.project_path,
            "daily_analysis": day_analysis,
            "weekly_analysis": week_analysis,
            "all_time_analysis": all_analysis,
            "recommendations": []
        }
        
        # Add recommendations based on analyses
        if day_analysis["status"] == "success":
            for opportunity in day_analysis["results"].get("optimization_opportunities", []):
                report["recommendations"].append({
                    "priority": "high" if opportunity["issue"] == "high_error_rate" else "medium",
                    "operation": opportunity["operation"],
                    "issue": opportunity["issue"],
                    "suggestion": opportunity["suggestion"]
                })
        
        # Save report
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.diagnostics_path, f"execution_analysis_{timestamp}.json")
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Generated diagnostics report at {report_path}")
        except Exception as e:
            logger.error(f"Error saving diagnostics report: {str(e)}")
        
        return report

# Singleton pattern for the tracer
_tracers = {}

def get_tracer(project_path: str) -> ExecutionTracer:
    """
    Get or create an execution tracer for the specified project.
    
    Args:
        project_path: The root directory of the project
        
    Returns:
        ExecutionTracer instance
    """
    if project_path not in _tracers:
        _tracers[project_path] = ExecutionTracer(project_path)
    
    return _tracers[project_path]

def trace_execution(project_path: str, operation: str):
    """
    Decorator to trace execution of AI Librarian operations.
    
    Args:
        project_path: The project path (can be a function that returns the path)
        operation: The operation name
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get the actual project path
            actual_path = project_path
            if callable(project_path):
                actual_path = project_path(*args, **kwargs)
            
            # Get parameters
            # For most functions, we expect the first arg to be project_path
            # and the second to be the main parameter (e.g., component_name)
            parameters = {}
            if len(args) > 1:
                parameters["main_parameter"] = args[1]
            parameters.update({k: v for k, v in kwargs.items() if k != "project_path"})
            
            # Get tracer
            tracer = get_tracer(actual_path)
            
            # Record start time
            start_time = time.time()
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Calculate execution time
                execution_time_ms = (time.time() - start_time) * 1000
                
                # Record successful operation
                tracer.record_operation(
                    operation=operation,
                    parameters=parameters,
                    result_status="success",
                    execution_time_ms=execution_time_ms,
                    metadata={"result_type": type(result).__name__}
                )
                
                return result
                
            except Exception as e:
                # Calculate execution time
                execution_time_ms = (time.time() - start_time) * 1000
                
                # Record failed operation
                tracer.record_operation(
                    operation=operation,
                    parameters=parameters,
                    result_status="error",
                    execution_time_ms=execution_time_ms,
                    error_message=str(e)
                )
                
                # Re-raise the exception
                raise
        
        return wrapper
    
    return decorator
