# Upgrade Manager for AI Dev Toolkit

The Upgrade Manager is a comprehensive system that helps you manage AI Dev Toolkit installations across multiple projects, ensuring all projects benefit from the latest features and improvements.

## Key Features

- **Version Management**: Track and compare semantic versions across projects
- **Project Analysis**: Examine project structure to identify beneficial features
- **Intelligent Recommendations**: Get customized toolkit feature suggestions based on project characteristics
- **Configuration Backup**: Automatically back up existing configurations before upgrades
- **Incremental Upgrades**: Apply only the necessary changes to bring projects up to date
- **Git Repository Integration**: Configure Git tracking during upgrades for Git repositories
- **CLAUDE.md Management**: Create or update CLAUDE.md files with auto-initialization code
- **Command-line Interface**: Simple, scriptable interface for automation

## Usage

### Command-line Usage

The simplest way to use the Upgrade Manager is through the provided command-line script:

```bash
# Analyze a project without making changes
python scripts/upgrade_ai_toolkit.py --analyze /path/to/project

# Upgrade a project to the latest version
python scripts/upgrade_ai_toolkit.py /path/to/project

# Force upgrade even if already at latest version
python scripts/upgrade_ai_toolkit.py --force /path/to/project

# Skip creating a backup of the .ai_reference directory
python scripts/upgrade_ai_toolkit.py --no-backup /path/to/project

# Skip creating or updating CLAUDE.md
python scripts/upgrade_ai_toolkit.py --no-claude-md /path/to/project

# Skip setting up git tracking
python scripts/upgrade_ai_toolkit.py --no-git /path/to/project
```

### Programmatic Usage

You can also use the Upgrade Manager programmatically in your Python code:

```python
from aitoolkit.utils.upgrade_manager import UpgradeManager

# Check if a project needs an upgrade
needs_upgrade, current_version, latest_version = UpgradeManager.needs_upgrade("/path/to/project")
if needs_upgrade:
    print(f"Project needs upgrade from {current_version} to {latest_version}")

# Analyze a project without upgrading
analysis = UpgradeManager.analyze_project("/path/to/project")
print(f"Project characteristics: {analysis['recommendations']}")
print(f"Recommended actions: {analysis['recommendations']['recommendations']}")

# Perform an upgrade
results = UpgradeManager.upgrade(
    "/path/to/project",
    backup=True,          # Create a backup of the .ai_reference directory
    claude_md=True,       # Create or update CLAUDE.md
    git_tracking=True,    # Set up git tracking
    force=False           # Only upgrade if needed
)
print(f"Upgrade success: {results['success']}")
print(f"Message: {results['message']}")
```

## How It Works

### Project Analysis

The Upgrade Manager analyzes your project structure to identify its characteristics:

1. **Basic Analysis**:
   - Checks if the project has an existing `.ai_reference` directory
   - Checks if the project has a `CLAUDE.md` file
   - Checks if the project is a Git repository

2. **Python Project Analysis**:
   - Detects test directories and files
   - Identifies requirements files and setup scripts
   - Recognizes web frameworks (Flask, Django, FastAPI)

3. **Web Project Analysis**:
   - Identifies Node.js projects
   - Detects frontend frameworks (React, Vue, Angular)
   - Recognizes build tools (Webpack)

### Feature Recommendations

Based on the analysis, the Upgrade Manager recommends features that would benefit your project:

- **AI Reference Initialization**: For projects without an existing `.ai_reference` directory
- **CLAUDE.md Creation**: For projects without a `CLAUDE.md` file
- **Git Tracking Setup**: For Git repositories
- **Test Tools**: For projects with test directories
- **Package Tools**: For projects with requirements files or setup scripts
- **Web Tools**: For projects using web frameworks
- **Node Tools**: For Node.js projects
- **Build Tools**: For projects using build tools
- **Component Tools**: For projects using frontend component frameworks

### Upgrade Process

When performing an upgrade, the Upgrade Manager:

1. **Checks Version**: Compares the installed version with the latest version
2. **Creates Backup**: Backs up the existing `.ai_reference` directory (if requested)
3. **Initializes AI Reference**: Sets up or updates the AI reference system
4. **Updates Version Info**: Records the new version information
5. **Creates CLAUDE.md**: Sets up CLAUDE.md with auto-initialization code (if requested)
6. **Sets Up Git Tracking**: Configures Git tracking for repositories (if requested)

## Version Comparison

The Upgrade Manager uses a semantic versioning system to compare versions:

- **Major Version**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **Minor Version**: New features without breaking changes (e.g., 1.0.0 → 1.1.0)
- **Patch Version**: Bug fixes without new features (e.g., 1.0.0 → 1.0.1)
- **Suffix**: Development phase indicators (e.g., "-alpha", "-beta", "-git-integration")

When comparing versions, the Upgrade Manager considers a version without a suffix to be newer than the same version with a suffix.

## Best Practices

- **Always Analyze First**: Use the `--analyze` flag to see what would be upgraded before making changes
- **Keep Backups**: The default behavior creates backups before upgrades, but you can use `--no-backup` if space is limited
- **Regular Upgrades**: Run the upgrade script periodically to ensure all projects benefit from the latest improvements
- **Handling Failures**: If an upgrade fails, check the error message and try again with different options
- **Multiple Projects**: You can create a simple script to upgrade multiple projects at once

## Troubleshooting

- **"Version not found" Error**: The project may have an older `.ai_reference` structure. Try using `--force` to recreate it.
- **Backup Creation Failure**: Ensure you have write permissions in the parent directory of your project.
- **Initialization Errors**: Check if your project path is valid and accessible.
- **"Already at latest version" Message**: Your project is already up to date. Use `--force` to upgrade anyway.
- **Git Tracking Issues**: Ensure your project is a valid Git repository with a proper `.git` directory.