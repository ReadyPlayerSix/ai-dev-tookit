# Model Context Protocol (MCP) Overview

## What is MCP?

The Model Context Protocol (MCP) is a communication protocol designed to connect large language models (LLMs) like Claude with external tools and capabilities. It provides a standardized way for AI assistants to:

- Access files and directories
- Run code and tools
- Access external resources
- Execute complex operations

## How AI Dev Toolkit Uses MCP

The AI Dev Toolkit implements an MCP server that provides:

1. **Tool Registration**: Tools are registered with the server and exposed to Claude
2. **Data Marshalling**: Converts between Python objects and MCP protocol data
3. **Request Handling**: Processes and routes tool invocation requests
4. **Result Formatting**: Formats results in a way Claude can understand

## Architecture Components

```
+----------------+      +-------------------------+      +----------------+
|                |      |                         |      |                |
|  Claude or     |      |  AI Dev Toolkit         |      |  File System   |
|  other LLM     |<---->|  MCP Server             |<---->|  & Resources   |
|                |      |                         |      |                |
+----------------+      +-------------------------+      +----------------+
                                   |
                                   |
                                   v
                        +-------------------------+
                        |                         |
                        |  Registered Tools:      |
                        |  - File System Tools    |
                        |  - AI Librarian         |
                        |  - Project Starter      |
                        |  - Think Tool           |
                        |                         |
                        +-------------------------+
```

## Connection Flow

1. User starts the AI Dev Toolkit MCP server
2. User configures Claude Desktop to connect to the local server
3. Claude connects to the server and discovers available tools
4. User asks Claude to perform tasks using the tools
5. Claude invokes the appropriate tools via MCP
6. Tools execute and return results to Claude
7. Claude interprets and communicates results to the user

## Technical Details

- **Connection**: Localhost connection (typically port 8000)
- **Authentication**: Currently using simplified authentication
- **Protocol**: JSON-based communication protocol
- **Tool Invocation**: Synchronous tool execution

## Security Considerations

- Tools execute with the permissions of the local user
- File access is limited to directories specified by the user
- MCP servers should only be run in trusted environments

## Future Enhancements

- Improved authentication and authorization
- Asynchronous tool execution
- Progress reporting for long-running tools
- Remote MCP server capabilities
