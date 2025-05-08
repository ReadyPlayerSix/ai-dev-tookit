# Changelog

## v0.4.0 - TaskBoard System (Coming Soon)

### Added
- **TaskBoard System**: Persistent AI-optimized task management system
  - Mini-Librarian architecture for specialized task processing
  - Asynchronous background processing for information gathering
  - AI-optimized shorthand format for efficient AI-to-AI communication
  - Task queue system for requesting and tracking information
- **Think Tool**: Enhanced capability for Claude to reason through complex problems
  - Task delegation to mini-librarians
  - Knowledge synthesis from multiple information sources
  - Contextual memory across conversations
- **Advanced AI Task Management**:
  - Richer task context with code references
  - Task dependencies and relationships
  - Progress tracking and reporting

### Changed
- Refactored task management system for improved performance
- Enhanced AI Librarian to integrate with TaskBoard
- Updated documentation with new features and examples

## v0.3.0 - Integrated Server (2025-05-07)

### Added
- **Integrated Server**: Combined AI Librarian and File System functionality into a single MCP server
- **Enhanced File Operations**:
  - `find_related_files`: Find files related to a specific file based on imports and references
  - `find_references`: Find all references to a component across the codebase
  - `get_file_overview`: Get comprehensive analysis of a file including structure and metrics
  - `optimized_query_component`: Improved version of query_component with better performance
- **Easy Installation**: Added `install_unified.py` to simplify Claude Desktop integration
- **Launcher Script**: Added `launch_unified.py` for easy server startup

### Changed
- Updated MCP connector to expose the integrated server
- Moved legacy files to dedicated directory for better organization
- Improved error handling and stability

## v0.2.0 - AI Librarian Enhancements (2025-04-15)

### Added
- Enhanced indexer for improved code understanding
- AI-optimized task system for better task tracking
- Improved diagnostic tools

### Changed
- Refactored filesystem utilities for better performance
- Updated AI Librarian interface for better usability

## v0.1.0 - Initial Release (2025-03-01)

### Added
- Basic AI Librarian functionality
- File System tools for file access
- GUI configurator for setup
- Claude Desktop integration
