# Internal Prompts for Bookmark Management

## Overview
These prompts replace explicit bookmark tools with structured internal workflows that Claude can follow to manage code bookmarks efficiently.

## 1. Creating a Bookmark

When a user wants to bookmark code or create a reference point:

```
INTERNAL PROMPT: Create Bookmark
1. Identify the file and location the user wants to bookmark
2. Extract the relevant context (function, class, or code block)
3. Use write_file to create a bookmark file:
   - Path: /project/.ai_reference/bookmarks/{timestamp}_{descriptive_name}.json
   - Content: JSON with file_path, line_number, context, description
4. Acknowledge bookmark creation with location details
5. IMPORTANT: Wait for file write confirmation before proceeding
```

## 2. Listing Bookmarks

When a user asks to see their bookmarks:

```
INTERNAL PROMPT: List Bookmarks
1. Use directory_tree on /project/.ai_reference/bookmarks/
2. For each bookmark file found:
   - Read the JSON file using read_file
   - Extract and display: name, file, line number, description
3. Present in a clean, organized format
4. IMPORTANT: Complete all reads before summarizing
```

## 3. Applying/Jumping to a Bookmark

When a user wants to go to a bookmarked location:

```
INTERNAL PROMPT: Apply Bookmark
1. Read the bookmark file from .ai_reference/bookmarks/
2. Extract file_path and line_number from the JSON
3. Use read_file with offset parameter to show code at bookmarked location
4. Provide context about surrounding code
5. IMPORTANT: Verify file exists before attempting to read
```

## 4. Removing a Bookmark

When a user wants to delete a bookmark:

```
INTERNAL PROMPT: Remove Bookmark
1. Identify the bookmark to remove (by name or selection)
2. Use directory_tree to confirm bookmark exists
3. Delete the bookmark file using move_file to /dev/null or a trash directory
4. Confirm deletion to user
5. IMPORTANT: Verify bookmark exists before attempting removal
```

## 5. Updating a Bookmark

When a user wants to modify a bookmark:

```
INTERNAL PROMPT: Update Bookmark
1. Read the existing bookmark file
2. Parse the JSON content
3. Apply the requested changes (description, context, etc.)
4. Use write_file to save the updated bookmark
5. Confirm changes to user
6. IMPORTANT: Preserve all existing fields not being updated
```

## Best Practices for Claude

1. **Always verify paths exist** before operations
2. **Use consistent naming**: {timestamp}_{descriptive_name}.json
3. **Include context** in bookmarks for better understanding
4. **Wait for confirmations** before proceeding to next step
5. **Handle errors gracefully** - if bookmark doesn't exist, inform user
6. **Batch operations** when dealing with multiple bookmarks

## Example Bookmark Structure

```json
{
  "name": "login_function",
  "file_path": "/project/src/auth/login.py",
  "line_number": 45,
  "context": "def login(username, password):",
  "description": "Main login function that handles user authentication",
  "created_at": "2024-12-28T10:30:00Z",
  "tags": ["auth", "critical"]
}
```

This structure ensures all necessary information is preserved for future reference.