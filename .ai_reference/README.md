# AI Reference System

This directory contains the AI Librarian system, a key component of the AI Dev Toolkit. The AI Librarian helps AI assistants efficiently navigate and understand codebases.

## Components

- **script_index.json** - Central registry of all source files and their relationships
- **component_registry.json** - Catalog of components, classes, and methods
- **generate_mini_librarians.py** - Script to generate mini-librarians for source files
- **library_generator.py** - Core logic for analyzing code and generating librarian files
- **run_generator.py** - Entry point for regenerating the librarian system

## Directories

- **context/** - Stores compressed conversation history for AI assistants (gitignored)
- **diagnostics/** - Contains diagnostic information about code analysis (gitignored)
- **scripts/** - Helper scripts for the librarian system

## Usage

Run `scripts/run_librarian_generator.bat` to update the AI Librarian after making changes to your codebase. This will:

1. Scan your source files
2. Extract classes, methods, and relationships
3. Generate an updated script_index.json
4. Create mini-librarians for efficient code navigation

AI assistants working with your codebase can use this structured information to provide more accurate and efficient assistance.
