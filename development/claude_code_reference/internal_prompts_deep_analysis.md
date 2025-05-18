# Internal Prompts for Deep Analysis with Integrated TaskBoard

## Overview
These prompts merge TaskBoard functionality into the deep_analysis tool, providing asynchronous task management within the analysis framework.

## 1. Enhanced Deep Analysis

When a user requests deep analysis or complex problem solving:

```
INTERNAL PROMPT: Deep Analysis with Task Management
1. Parse the analysis request to identify:
   - Main objective
   - Subtasks required
   - Resource requirements
   - Expected duration
2. Create analysis task structure:
   - Generate unique task_id
   - Break into subtasks if needed
   - Assign priorities
3. Execute analysis:
   - For quick tasks (< 5 seconds): Execute synchronously
   - For longer tasks: Create async task and return task_id
4. Provide updates:
   - Immediate acknowledgment with task_id
   - Periodic status updates if long-running
5. IMPORTANT: Always return actionable insights, not just task status
```

## 2. Background Task Submission

When deep_analysis needs to run asynchronously:

```
INTERNAL PROMPT: Submit Background Analysis
1. Create task metadata:
   {
     "task_id": "analysis_{timestamp}_{hash}",
     "type": "deep_analysis",
     "status": "pending",
     "created_at": "timestamp",
     "priority": "high|medium|low",
     "estimated_duration": seconds,
     "subtasks": []
   }
2. Save to .ai_reference/tasks/{task_id}.json
3. Begin execution in background
4. Return task_id immediately to user
5. IMPORTANT: Provide example of how to check status
```

## 3. Task Status Checking

When user wants to check analysis progress:

```
INTERNAL PROMPT: Check Analysis Status
1. Read task file from .ai_reference/tasks/{task_id}.json
2. Provide current status:
   - pending: "Analysis queued, will begin shortly"
   - running: "Analysis in progress (X% complete)"
   - completed: "Analysis complete - retrieving results"
   - failed: "Analysis failed - {error_message}"
3. For running tasks, show:
   - Current phase
   - Completed subtasks
   - Estimated time remaining
4. IMPORTANT: If completed, automatically show results
```

## 4. Getting Analysis Results

When analysis is complete:

```
INTERNAL PROMPT: Retrieve Analysis Results
1. Read results from .ai_reference/tasks/{task_id}_results.json
2. Format results based on analysis type:
   - Code analysis: Findings, recommendations, code samples
   - Architecture review: Diagrams, issues, improvements
   - Performance analysis: Metrics, bottlenecks, optimizations
3. Provide summary first, then detailed findings
4. Include actionable next steps
5. IMPORTANT: Clean up task files after successful retrieval
```

## 5. Task Cancellation

When user wants to stop an analysis:

```
INTERNAL PROMPT: Cancel Analysis
1. Read task metadata
2. If status is "running":
   - Set status to "cancelling"
   - Stop background execution
   - Clean up partial results
   - Set final status to "cancelled"
3. Preserve any partial results if useful
4. Inform user of cancellation with any available partial insights
5. IMPORTANT: Ensure clean cancellation without resource leaks
```

## 6. Listing Active Analyses

When user wants to see all analyses:

```
INTERNAL PROMPT: List Analyses
1. Scan .ai_reference/tasks/ directory
2. Read all task files
3. Group by status:
   - Active (pending/running)
   - Completed (with results available)
   - Failed/Cancelled
4. Show for each:
   - Task ID and description
   - Status and progress
   - Created time and duration
5. IMPORTANT: Highlight any requiring attention
```

## Deep Analysis Types

1. **Code Quality Analysis**
   - Complexity metrics
   - Best practice violations
   - Refactoring opportunities

2. **Architecture Analysis**
   - Component dependencies
   - Design pattern compliance
   - Scalability assessment

3. **Security Analysis**
   - Vulnerability scanning
   - Authentication/authorization review
   - Data protection assessment

4. **Performance Analysis**
   - Bottleneck identification
   - Resource usage patterns
   - Optimization recommendations

5. **Test Coverage Analysis**
   - Missing test scenarios
   - Test quality assessment
   - Coverage improvement plan

## Task Priority Guidelines

- **High**: Blocking issues, security concerns, critical bugs
- **Medium**: Performance improvements, code quality
- **Low**: Nice-to-have features, minor refactoring

## Example Task Structure

```json
{
  "task_id": "analysis_20241228_security_abc123",
  "type": "security_analysis",
  "description": "Comprehensive security audit of authentication system",
  "status": "running",
  "priority": "high",
  "created_at": "2024-12-28T10:00:00Z",
  "started_at": "2024-12-28T10:00:05Z",
  "estimated_duration": 300,
  "progress": 45,
  "current_phase": "Analyzing access control patterns",
  "subtasks": [
    {
      "id": "sub_001",
      "description": "Scan for injection vulnerabilities",
      "status": "completed"
    },
    {
      "id": "sub_002", 
      "description": "Review authentication flow",
      "status": "running"
    }
  ]
}
```

## Best Practices

1. **Clear Communication**: Always explain what's happening
2. **Progress Updates**: Provide meaningful progress indicators
3. **Partial Results**: Share findings as they become available
4. **Error Recovery**: Gracefully handle failures with helpful messages
5. **Resource Management**: Clean up completed tasks periodically

This integrated approach provides powerful analysis capabilities while maintaining simplicity.