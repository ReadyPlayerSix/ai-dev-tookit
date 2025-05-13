# Testing the Think Tool in Claude Desktop

This guide will help you test the newly implemented standalone Think Tool in Claude Desktop.

## Prerequisites

1. Claude Desktop is properly configured and running
2. AI Dev Toolkit is installed in Claude Desktop
3. The updated code has been deployed

## Step 1: Install the Updated Toolkit in Claude Desktop

Make sure the latest version of the AI Dev Toolkit is installed in Claude Desktop:

```bash
# Navigate to the toolkit directory
cd path/to/ai-dev-toolkit

# Install dependencies
pip install -r requirements.txt

# Install to Claude Desktop
python development/install_to_claude.py

# Restart Claude Desktop to apply changes
# (Close and reopen the application)
```

## Step 2: Verify the Tool Registration

To verify that the standalone think tool is properly registered, ask Claude to list the available tools. You should see the think tool in the list, with a description matching our new implementation.

Example prompt:
> "Please list all the tools you have available, especially the think tool."

## Step 3: Test Basic Functionality

Try a simple test of the think tool:

Example prompt:
> "Use the think tool to break down the steps needed to implement a user authentication system."

Claude should respond by using the think tool to create a structured reflection of the steps, without affecting any files or actually implementing anything.

## Step 4: Test Complex Reflection

Test the think tool with a more complex example that involves rule checking and requirements verification:

Example prompt:
> "I want to import user data from a CSV file into our database. Use the think tool to analyze the risks and requirements of this task."

Claude should use the think tool to methodically analyze:
- Required information
- Data validation needs
- Security considerations
- Implementation steps
- Potential risks

## Step 5: Test Separation from TaskBoard

Verify that the think tool is now completely separate from the TaskBoard system:

Example prompt:
> "Use the think tool to analyze a problem, and then check if there are any tasks running in the TaskBoard system."

The think tool should perform immediate reflection, while listing tasks should show no think-related tasks in the TaskBoard system.

## Step 6: Advanced Usage Patterns

Test the more advanced usage patterns:

Example prompt:
> "I need to refactor our data processing pipeline. Use the think tool to compare different approaches and help me decide on the best strategy."

Claude should use the think tool to:
1. List multiple possible approaches
2. Compare pros and cons
3. Evaluate each option against criteria
4. Make a recommendation

## Step 7: Report Results

After testing, please document:

1. Whether the think tool operates as expected (immediate reflection vs. asynchronous processing)
2. Any errors or unexpected behavior
3. The quality of reflection provided by the think tool
4. Whether the reflection output format is clear and useful

## Troubleshooting

If you encounter issues:

1. **Tool Not Available**: Verify the installation completed successfully and restart Claude Desktop
2. **Wrong Implementation**: Check if Claude is still trying to use the old TaskBoard-based implementation (will return a task ID instead of actual reflection)
3. **Import Errors**: Check the Claude Desktop logs for any import errors related to the think_tool module
4. **Format Issues**: Verify that the reflection output is properly formatted with the expected tags

## Example Expected Output

When properly implemented, the think tool output should look something like:

```
<reflection>
Breaking down implementation of authentication system:

1. Requirements gathering:
   - User roles and permissions needed
   - Authentication method (password, SSO, MFA?)
   - Session management requirements

2. Technical design:
   - Database schema for users and roles
   - Authentication flow diagram
   - API endpoints needed

3. Security considerations:
   - Password hashing strategy
   - Protection against common attacks
   - Rate limiting and lockout policies

4. Implementation steps:
   - Set up user database tables
   - Create authentication controller
   - Implement login/logout flow
   - Add middleware for route protection

5. Testing approach:
   - Unit tests for authentication logic
   - Integration tests for full flow
   - Security testing (penetration tests)
</reflection>
```

The reflection should be immediate (not returning a task ID), comprehensive, and properly structured.