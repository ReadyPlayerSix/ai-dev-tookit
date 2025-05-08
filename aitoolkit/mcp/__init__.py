"""MCP connector module for AI Dev Toolkit."""

try:
    from .connector import MCPConnector, FastMCP, Context
    # Try to import the integrated server, but don't fail if it doesn't exist yet
    try:
        # Export the integrated server for easy access
        from .integrated_server import IntegratedServer, create_server
        __all__ = ['MCPConnector', 'IntegratedServer', 'create_server', 'FastMCP', 'Context']
    except ImportError:
        # If the integrated server isn't available yet, just export the connector
        __all__ = ['MCPConnector', 'FastMCP', 'Context']
except ImportError as e:
    import logging
    logging.warning(f"Could not import some MCP components: {e}")
    __all__ = []
