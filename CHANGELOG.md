# Changelog

All notable changes to this project will be documented in this file.

## [0.7.5-alpha-tool-optimization] - 2025-05-18

### Added
- Alpha/Pre-Beta testing phase notice in README
- Real screenshots from docs/images directory
- MCP extensions module for enhanced Claude integration
- Internal advisors system for context management
- Prompt tools for dynamic guidance generation
- Timeout configuration and prevention guides
- Hierarchical tool selection documentation

### Changed
- Updated README with prominent testing phase warnings
- Enhanced modern GUI interface components
- Improved timeout handling with detailed guides
- Updated all version references for consistency
- Added tool limitation notice for testers

### Fixed
- Version consistency across all modules
- Tool timeout issues with optimization patterns

## [0.5.8-improved-gui] - 2025-05-15

### Added
- Developer tab with terminal functionality
- Help & Troubleshooting tab with documentation links
- Color Mode selection (Light/Match System/Dark) in Settings
- Font selection and size adjustment in Settings
- Text size slider control for adjustable UI font sizes
- Settings persistence through save/load functionality 
- Auto Save Notes toggle with Ctrl+S shortcut
- Log file explorer with filtering capabilities
- Documentation browser with direct access to docs folder
- Icon-based action buttons throughout the interface

### Changed
- Replaced Claude Desktop refresh icon with llama icon (🦙)
- Upgraded "Upgrade Toolkit" to "Check for Updates" with warning icon (⚠️)
- Changed notes and log font to Consolas for better monospace display
- Fixed uneven button widths between left and right columns
- Fixed "Error saving notes" issue with proper error handling and persistent notes storage
- Moved Help & Troubleshooting content from Dashboard to dedicated tab
- Replaced Save Notes button with enhanced Auto Save Notes toggle with real-time saving
- Made all headers use accent blue color for consistent styling
- Updated button hover colors to match accent blue theme
- Standardized all buttons to use the same consistent action button style with icons
- Expanded notes section for more writing space

### Removed
- Removed real-time server status monitoring to prevent interference with Claude Desktop
- Eliminated sidebar status indicator for cleaner interface
- Replaced constant log monitoring with on-demand log explorer
- Removed MCP Server Management text and simplified interface

## [0.5.7-gui-enhancements] - 2025-05-14

### Added
- "Restart Claude Desktop" button in GUI Dashboard with process management
- "Filter Server Log" functionality with customizable filtering options
- GUI Dashboard reorganization for better usability
- Process detection and management through psutil integration

### Changed
- Renamed "Open Claude Desktop Location" to "Open Claude Config Directory"
- Removed "Clean Legacy Files" button from Quick Actions
- Updated requirements.txt with psutil dependency
- Improved error handling for process management operations

## [0.5.6-upgrade-manager] - 2025-05-14

### Added
- Comprehensive upgrade management system for AI Development Toolkit
- Project analysis to recommend features based on codebase structure
- Automatic backup of existing configurations before upgrades
- Version comparison system with semantic versioning support
- Command-line upgrade script for easy execution
- "Upgrade Toolkit" button in GUI Dashboard
- "Clear Request Queue" button in GUI Dashboard
- Documentation for the upgrade manager

### Changed
- Enhanced tooling for project maintainability and upgrades
- Moved Think Tool from server list to capabilities in GUI
- Improved documentation with upgrade instructions
- Simplified version management across multiple projects

## [0.5.5-git-integration] - 2025-05-14

### Added
- Git repository tracking and analysis capabilities
- New MCP tools for working with git repositories:
  - `get_git_info`: Retrieves comprehensive git repository information
  - `update_git_history`: Creates human and machine-readable git history files
- Caching system for git information to improve performance
- Git history output in JSON and human-readable formats
- Documentation for git tracking functionality in upgrading_ai_reference.md

### Changed
- Enhanced librarian_context to store git repository information
- Improved cache management for repeated git information requests
- Extended documentation with git tracking usage guidelines

## [0.5.4-optimized-tool-usage] - 2025-05-14

### Added
- Enhanced CLAUDE.md with optimized tool usage guidelines to prevent timeouts
- New hierarchical tool selection approach for improved performance
- Comprehensive documentation on using the .ai_reference index efficiently
- Internal prompts for Claude to utilize indexed data structures
- Added new section in README.md on optimized tool usage
- Added specific timeout avoidance strategies documentation
- Expanded upgrading_ai_reference.md with AI Reference usage guide

### Changed
- Updated documentation to promote index-first approach vs filesystem walks
- Provided code examples for proper .ai_reference utilization
- Added TaskBoard recommendations for long-running operations
- Improved troubleshooting section with tool performance guidance

## [0.5.4-timeout-robustness] - 2025-05-14

### Added
- Automatic detection and upgrade of existing .ai_reference directories in the installer
- Operation-specific timeout management for different types of operations
- Improved documentation for upgrading projects with existing .ai_reference directories
- MCP protocol-level timeout configuration to prevent connection issues
- Phased tool registration to prevent MCP server timeouts during startup
- Enhanced MCP installation documentation (MCP_INSTALLATION.md)
- Explicit MCP package requirement documentation in README.md

### Changed
- Replaced signal-based timeout mechanism with more reliable threading-based implementation
- Increased default timeouts for write operations (120s) and search operations (120s)
- Enhanced CLAUDE.md automatic initialization for reliable toolkit startup
- Extended MCP protocol default timeout from 30s to 120s
- Implemented lazy tool registration for improved server reliability
- Added dedicated MCP tool registration timeout (10 minutes)

### Fixed
- Fixed timeout issues in write_tool and search_tool operations
- Improved cross-platform compatibility for timeout handling (Windows support)
- Enhanced error recovery for long-running operations
- Addressed MCP server disconnection issues in Claude Desktop
- Fixed tool registration timeout issues during server startup

## [0.5.2-tool-integration] - 2025-05-13

### Added
- TaskBoard integration for Tool Reference system
- Asynchronous processing for tool indexing operations
- Bidirectional cross-references between .ai_reference and .tool_reference
- Tool-to-component and component-to-tool mapping functionality
- Improved component navigation with tool awareness
- New MCP tools for asynchronous tool reference management

### Changed
- Optimized server startup with lazy-loading of security analyzer
- Improved tool indexing performance through TaskBoard integration
- Enhanced component-to-tool relationship tracking

## [0.5.1-security-analyzer] - 2025-05-13

### Added
- Professional security analyzer for codebase vulnerability assessment
- Pattern-based security scanning for common vulnerability patterns
- AST-based security analysis for more sophisticated vulnerability detection
- Security issue categorization by severity (Critical, High, Medium, Low, Info)
- CWE ID mapping for standardized vulnerability tracking
- Enhanced sanity_check with optional security analysis integration
- Dedicated security_analyze tool for comprehensive security reports

### Changed
- Improved server integration with modular security analyzer component
- Enhanced diagnostic capabilities for sanity_check tool
- Added security-specific patterns for AI Dev Toolkit components

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