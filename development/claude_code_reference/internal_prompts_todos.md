# Internal Prompts for TODO Management

## Overview
These prompts replace explicit TODO tools with structured internal workflows for managing project tasks and todos.

## 1. Adding a TODO

When a user wants to create a new TODO item:

```
INTERNAL PROMPT: Add TODO
1. Extract task details from user's request
2. Generate a unique todo_id (use timestamp + short hash)
3. Use write_file to create TODO file:
   - Path: /project/.ai_reference/todos/{todo_id}.json
   - Include: description, priority, status, created_at, tags
4. If part of larger task, link to parent_id
5. Acknowledge creation with todo_id
6. IMPORTANT: Validate all required fields before saving
```

## 2. Listing TODOs

When a user asks to see their TODOs:

```
INTERNAL PROMPT: List TODOs
1. Use directory_tree on /project/.ai_reference/todos/
2. Read each TODO file using read_multiple_files for efficiency
3. Parse JSON and extract key information
4. Group by status (pending, in_progress, completed)
5. Sort by priority within each group
6. Present in organized format with:
   - Status indicators (🔴 high, 🟡 medium, 🟢 low)
   - Brief descriptions
   - Created dates
7. IMPORTANT: Handle large TODO lists by paginating if needed
```

## 3. Updating TODO Status

When a user wants to change TODO status:

```
INTERNAL PROMPT: Update TODO Status
1. Identify the TODO by id or description
2. Read the existing TODO file
3. Update the status field (pending → in_progress → completed)
4. Add status_updated_at timestamp
5. If completing, add completed_at timestamp
6. Use write_file to save updates
7. Confirm status change to user
8. IMPORTANT: Preserve all existing TODO data
```

## 4. Searching TODOs

When a user wants to find specific TODOs:

```
INTERNAL PROMPT: Search TODOs
1. Use search_files on /project/.ai_reference/todos/ directory
2. Search for keywords in description, tags, or status
3. Read matching TODO files
4. Present filtered results with context
5. IMPORTANT: Support multiple search criteria (status AND keyword)
```

## 5. Inferring TODOs from Code

When analyzing code for potential TODOs:

```
INTERNAL PROMPT: Infer TODOs
1. Use search_files to find TODO/FIXME/HACK comments
2. Parse surrounding code context
3. For each found item:
   - Extract the comment text
   - Identify the file and line number
   - Determine priority from keywords (FIXME=high, TODO=medium)
4. Create TODO entries for new items not already tracked
5. Link to code location in the TODO metadata
6. IMPORTANT: Avoid duplicate TODO creation
```

## 6. Managing Subtasks

When a user wants to break down a TODO:

```
INTERNAL PROMPT: Add Subtask
1. Read the parent TODO file
2. Create new TODO with parent_id reference
3. Update parent TODO with subtask_ids array
4. Maintain hierarchical relationship
5. Show updated task tree to user
6. IMPORTANT: Validate parent exists before creating subtask
```

## Best Practices for Claude

1. **Use consistent ID format**: {timestamp}_{random_hash}
2. **Always include metadata**: created_at, updated_at timestamps
3. **Maintain relationships**: parent_id, subtask_ids for hierarchy
4. **Support filtering**: by status, priority, tags, date ranges
5. **Handle concurrent access**: check for changes before updating
6. **Batch operations**: use read_multiple_files for efficiency

## Example TODO Structure

```json
{
  "id": "20241228_abc123",
  "description": "Implement user authentication",
  "priority": "high",
  "status": "in_progress",
  "created_at": "2024-12-28T10:00:00Z",
  "updated_at": "2024-12-28T14:30:00Z",
  "tags": ["security", "backend"],
  "parent_id": null,
  "subtask_ids": ["20241228_def456", "20241228_ghi789"],
  "code_references": [
    {
      "file": "/src/auth/login.py",
      "line": 45,
      "type": "TODO comment"
    }
  ],
  "notes": "Required for MVP release"
}
```

## Status Workflow

```
pending → in_progress → completed
         ↘ blocked ↗
```

## Priority Levels

- **high**: 🔴 Critical, blocking other work
- **medium**: 🟡 Important, should be done soon  
- **low**: 🟢 Nice to have, can wait

This structure ensures comprehensive task tracking while maintaining flexibility.