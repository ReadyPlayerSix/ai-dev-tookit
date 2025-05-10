# Logging Improvements Plan

This document outlines the plan for improving the logging system in the AI Dev Toolkit, specifically focusing on centralizing log file storage and ensuring consistent log management across all components.

## Current State

The AI Librarian server (`aitoolkit/librarian/server.py`) currently writes logs to:
- `ai_librarian.log` in the current working directory
- Console output (warnings and errors only)

This approach has several issues:
1. Log files are created in the current working directory, which can vary
2. No centralized location for all logs makes them harder to find and manage
3. Inconsistent with other components like Tool Index that use a dedicated logs directory

## Proposed Changes

1. Create a centralized logs directory structure:
   ```
   logs/
   ├── ai_librarian/      # AI Librarian specific logs
   ├── tool_index/        # Tool Index logs (already exists)
   ├── taskboard/         # Future TaskBoard logs
   └── server.log         # Main server log
   ```

2. Update the logging configuration in `aitoolkit/librarian/server.py`:
   - Create the logs directory if it doesn't exist
   - Write logs to `logs/ai_librarian/server.log` instead of current directory
   - Maintain the same log levels and formatting
   - Add a rolling file handler to manage log rotation

3. Add timestamp to log filenames for better tracking:
   - Use format like `server_YYYYMMDD.log` for daily rotation

## Implementation Steps

1. Create a new branch called `logging-improvements`
2. Add the centralized logging functionality
3. Test the server to ensure no functionality is broken
4. Update documentation to reflect the new logging structure
5. Merge the changes back to main branch

## Risk Mitigation

To avoid breaking the server:
- Maintain the existing logger name and log levels
- Keep the same formatting for consistent log parsing
- Ensure log directories exist before attempting to write
- Handle potential permission issues gracefully 
- Add fallback to current directory if centralized location fails

## Testing Plan

1. Start the server with the new logging configuration
2. Verify logs are created in the expected location
3. Confirm all levels of messages are logged appropriately
4. Check server functionality is unaffected
5. Test server restart to ensure log files are properly managed

## Benefits

- Easier to find and manage logs
- Consistent approach across all components
- Better organization for debugging and troubleshooting
- Prepared for future components like TaskBoard
- Improved log rotation and archiving
