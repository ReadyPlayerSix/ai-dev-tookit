"""
Enhanced help prompts for AI Librarian server.

This module provides enhanced help text explaining the AI Librarian's capabilities.
These prompts can be used in the server to provide better guidance to users.
"""

def ai_librarian_help() -> str:
    """
    Provide detailed help with AI Librarian functionality.
    """
    return """
    # AI Librarian - Enhanced Code Understanding

    The AI Librarian helps me understand your codebase at a much deeper level, providing rich context
    and component relationships. Here's how to use it:

    ## Basic Commands

    1. **Initialize Library**: `initialize_librarian("path/to/project")`
       - Creates a comprehensive context system for your project
       - Analyzes code structure, components, and relationships
       - Builds persistent context that lasts across conversations

    2. **Component Lookup**: `query_component("path/to/project", "ComponentName")`
       - Retrieves detailed information about a specific component
       - Shows source code, relationships, and dependencies
       - Provides context to understand the component's role

    3. **Code Search**: `find_implementation("path/to/project", "search text")`
       - Searches through the codebase for specific text
       - Shows matching code with surrounding context
       - Helps locate implementations of specific functionality

    4. **Update Library**: `generate_librarian("path/to/project")`
       - Updates the AI Librarian with latest code changes
       - Refreshes component relationships and dependencies
       - Ensures context remains current as code evolves

    ## Enhanced Features

    The AI Librarian analyzes your codebase to understand:

    - Component relationships and dependencies
    - Primary workflows and entry points
    - Code structure and organization patterns
    - Key components and their responsibilities

    This deeper understanding lets me provide more targeted assistance with:

    - Understanding code relationships
    - Identifying the right components for changes
    - Finding relevant code examples
    - Suggesting optimization opportunities

    Would you like me to explain a specific aspect of the AI Librarian in more detail?
    """

def enhanced_capabilities_help() -> str:
    """
    Provide information about enhanced AI Librarian capabilities.
    """
    return """
    # Enhanced AI Librarian Capabilities

    The AI Librarian now has enhanced capabilities for deeper code understanding:

    ## Rich Component Registry

    The component registry now includes:
    - Detailed component descriptions
    - Specific responsibilities for each component
    - Component relationships and dependencies
    - Workflow documentation

    ## Comprehensive Diagnostics

    The diagnostics system provides:
    - Component analysis with relationship mapping
    - Code structure and organization insights
    - Integration pattern documentation
    - Workflow analysis

    ## Project Context

    The project context includes:
    - Main entry points and workflows
    - Key components and their roles
    - Critical dependencies
    - Recent code changes

    ## Continuous Monitoring

    The monitoring system:
    - Detects code changes in real time
    - Updates component relationships
    - Maintains context accuracy
    - Preserves change history

    These enhancements enable me to provide much better assistance with your codebase,
    maintaining context across conversations and understanding the project at a deeper level.
    """

def workflow_help() -> str:
    """
    Provide help about AI Librarian workflows.
    """
    return """
    # AI Librarian Workflows

    The AI Librarian implements several key workflows:

    ## 1. Library Initialization

    ```
    initialize_librarian("path/to/project")
    ```

    This workflow:
    - Scans your project for code files
    - Parses and analyzes code structure
    - Identifies components and relationships
    - Generates comprehensive context
    - Creates the `.ai_reference` directory structure

    ## 2. Component Query

    ```
    query_component("path/to/project", "ComponentName")
    ```

    This workflow:
    - Searches for the component in the codebase
    - Retrieves source code and documentation
    - Provides dependency information
    - Shows usage examples where available

    ## 3. Implementation Search

    ```
    find_implementation("path/to/project", "search text")
    ```

    This workflow:
    - Searches all code files for the text
    - Provides surrounding context for matches
    - Filters by file type if specified
    - Shows line numbers for precise location

    ## 4. Library Update

    ```
    generate_librarian("path/to/project")
    ```

    This workflow:
    - Updates the AI Librarian with the latest code
    - Refreshes all context information
    - Updates component relationships
    - Records changes in the diagnostic logs

    These workflows enable me to maintain a deep understanding of your codebase
    and provide more effective assistance.
    """

if __name__ == "__main__":
    print("Enhanced help prompts for AI Librarian")
    print("--------------------------------------")
    print("\nBasic help:")
    print(ai_librarian_help())
    
    print("\nEnhanced capabilities:")
    print(enhanced_capabilities_help())
    
    print("\nWorkflow help:")
    print(workflow_help())
