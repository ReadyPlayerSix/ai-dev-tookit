# Changelog

All notable changes to this project will be documented in this file.

## [0.5.0-taskboard-release] - 2025-05-13

### Added
- TaskBoard system for asynchronous task processing
- Background worker threads with configurable pool size
- Prioritized task queue with automatic timeout handling
- Think Tool for complex reasoning tasks
- Task persistence and recovery mechanisms
- Comprehensive task management API (submit, status, results, cancel, list)
- Integration with existing mini-librarian system

### Changed
- Updated server implementation to support asynchronous operations
- Improved timeout handling for long-running operations
- Enhanced Claude Code compatibility with adapter patterns
- Added detailed documentation for TaskBoard and Think Tool
- Integrated TaskBoard directly into server for seamless experience
- Simplified user experience with automatic tool registration
- Eliminated need for separate installation scripts

## [0.4.8-claude-code-adapters] - 2025-05-13

### Added
- Claude Code adapter pattern support
- Installation scripts for direct GitHub installation
- Comprehensive documentation for Claude Code users
- Comparison table showing Claude Desktop vs Code functionality

### Changed
- Updated architecture diagrams to show both environments
- Enhanced README with feature status indicators
- Added Claude Code badges and compatibility information

## [0.4.7-claude-code-integration] - 2025-05-13

### Added
- Claude Code compatibility layer
- Installation scripts for Claude Code users
- Reference documentation for Claude Code
- Desktop shortcuts creation for GUI

### Changed
- Updated README with Claude Code installation instructions
- Modified architecture to support both Claude Desktop and Code

## [0.4.6-simple-tool-index] - 2025-05-12

### Added
- Simple Tool Index system with improved performance
- Direct function discovery with no subprocess handling
- AI-optimized tool profiles for better tool selection

### Changed
- Single-pass indexing replaces complex multi-phase processing
- Simplified output format for better maintainability
- Up to 10x faster execution for tool indexing

## [0.4.5-pre-fix] - 2025-05-11

### Fixed
- Critical bug in find_related_files function
- Type validation issues in file processing

## [0.4.2] - 2025-05-10

### Added
- Edit Bookmark system for complex code section editing
- Persistent bookmarks with metadata storage
- Tools for creating, updating, applying and removing bookmarks
- Improved docstrings and error handling

### Changed
- Enhanced AI Librarian initialization to support bookmark directories
- Updated README with edit bookmark documentation and examples
- Simplified project contribution guidelines

## [0.4.0] - 2025-05-09

### Added
- Unified Context System integrating AI Librarian and Tool Reference
- Bidirectional cross-references between components and tools
- Enhanced component analysis with relationship mapping
- Tool recommendation based on component context

### Changed
- Improved code analysis capabilities
- More robust error handling throughout the system
- Better performance for large codebases

## [0.3.0] - 2025-05-08

### Added
- Unified Server implementation combining AI Librarian and FileSystem
- Enhanced Todo Management System with persistent storage
- Component Registry for code understanding
- Diagnostic system for AI Librarian verification

### Changed
- Reorganized project structure for better maintainability
- Improved documentation with usage examples
- Updated GUI configurator for better user experience

## [0.2.0-alpha] - 2025-05-07

### Added
- Initial AI Librarian implementation
- Basic filesystem operations
- Command line interface
- Preliminary GUI configurator

### Changed
- Project structure refactoring
- Updated documentation

## [0.1.0-stable] - 2025-05-06

### Added
- Initial project structure
- Documentation framework
- Basic server implementation
