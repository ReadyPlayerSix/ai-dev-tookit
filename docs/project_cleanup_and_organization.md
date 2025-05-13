# Project Cleanup and Organization Guide

## Overview

This document provides guidance on cleaning up the AI Dev Toolkit project structure in preparation for implementing the TaskBoard system. It identifies unnecessary files, duplicate functionality, and recommends a cleaner project structure.

## Current Project State

The AI Dev Toolkit has evolved from separate components (AI Librarian, File System Tools) to a unified server architecture. This evolution has left some redundant files and structures that should be cleaned up before implementing new features.

## Files and Directories to Clean Up

### Unnecessary Files

1. **Backup/temporary files**:
   - `aitoolkit/librarian/server.py.bak`
   - `aitoolkit/gui/configurator.py.backup`
   - `aitoolkit/gui/configurator.py.fixed`
   - `aitoolkit/gui/configurator_new.py.fixed`
   - `aitoolkit/gui/__init__.py.old`
   - `aitoolkit/gui/configurator.py.updated`

2. **Duplicate/legacy GUI files**:
   - `aitoolkit/gui/configurator_fixed.py`
   - `aitoolkit/gui/configurator_legacy.py`
   - `aitoolkit/gui/configurator_test.py`

3. **Test files**:
   - `aitoolkit/test_file.txt`

### Unnecessary Directories

1. **Legacy directories**:
   - `aitoolkit/librarian/filesystem_old` (superseded by `aitoolkit/librarian/filesystem.py`)

2. **Test directories**:
   - `test_directory` (test files that aren't necessary for production)

## Recommended Project Structure

### Core Structure

```
ai-dev-toolkit/
├── aitoolkit/
│   ├── gui/                    # GUI configuration and setup
│   ├── librarian/              # AI Librarian functionality
│   │   ├── taskboard/          # NEW: TaskBoard implementation
│   │   ├── todos.py            # Todo management functionality
│   │   └── ...
│   ├── mcp/                    # MCP server implementation
│   ├── server/                 # Server tools and utilities
│   └── utils/                  # Utility functions
├── config/                     # Configuration examples
├── docs/                       # Documentation
├── examples/                   # Example usage
├── legacy/                     # Legacy code (for reference)
├── scripts/                    # Utility scripts
│   ├── cleanup.py              # Cleanup script
│   └── ...
├── src/                        # Source code (being migrated to aitoolkit)
└── tests/                      # Test suite
```

## Consolidation Recommendations

1. **Code Duplication**:
   - `src/librarian` vs `aitoolkit/librarian`: Code in `src/librarian` should either be moved to `aitoolkit/librarian` or to `legacy/` if no longer needed.

2. **MCP Implementation**:
   - Consolidate MCP functionality to `aitoolkit/mcp` and remove or move `src/mcp` to `legacy/`.

3. **Filesystem Functionality**:
   - Ensure all filesystem functionality is in `aitoolkit/librarian/filesystem.py` and remove any duplicates.

## TaskBoard Implementation Path

The TaskBoard system should be implemented as a new module in the existing structure:

1. Create `aitoolkit/librarian/taskboard/` directory with:
   - `__init__.py`: Module initialization
   - `task_manager.py`: Core task management functionality
   - `mini_librarian.py`: Base class for mini-librarians
   - `component_analyzer.py`: Component analysis mini-librarian
   - `file_indexer.py`: File indexing mini-librarian
   - `digest_manager.py`: Task result digest management
   - `utils.py`: Utility functions for the TaskBoard

2. Update the "think" tool in `aitoolkit/unified_server.py` to use the TaskBoard system.

3. Update the initialization process in `initialize_librarian()` to set up the TaskBoard directory structure.

## Implementation Steps

1. **Clean up the project**:
   - Run the cleanup script: `python scripts/cleanup.py`
   - Review and commit the changes

2. **Prepare the TaskBoard structure**:
   - Create the necessary directories and files
   - Implement the TaskBoard system according to the specification

3. **Update the unified server**:
   - Integrate the TaskBoard system with the existing server
   - Update the "think" tool to use the TaskBoard functionality

4. **Update documentation**:
   - Add TaskBoard documentation
   - Update existing documentation to reference the new functionality

5. **Create example usage scenarios**:
   - Add example usage of the TaskBoard and "think" tool
   - Include examples in the documentation

## Backward Compatibility

When implementing the TaskBoard system, ensure backward compatibility with existing functionality:

1. **Tool Interface**:
   - Maintain the interface for existing tools
   - Add new tools with clear documentation

2. **Data Storage**:
   - The TaskBoard should have its own data storage separate from existing systems
   - Ensure operations on existing data structures do not affect the TaskBoard

3. **User Experience**:
   - Update help prompts to include the new functionality
   - Ensure the user is guided through usage of the new features

## Conclusion

By cleaning up the project structure and organizing the codebase, we'll be better prepared to implement the TaskBoard system. This will make the implementation process smoother and result in a more maintainable codebase.
