#!/usr/bin/env python3
"""
Project Generator Script

This script parses a project plan markdown file and generates the project structure,
including directories, placeholder files, and GitHub setup instructions.

Usage:
    python project_generator.py <project_plan.md> <output_directory>

Example:
    python project_generator.py ai-librarian-project-plan.md ./ai-librarian
"""

import os
import re
import sys
import json
import shutil
from pathlib import Path
import argparse
from datetime import datetime

# Templates for generated files
TEMPLATES = {
    "README.md": """# {project_name}

{project_description}

## Overview

{project_tagline}

## Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/{project_dir}.git
cd {project_dir}

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Usage

[Usage instructions will go here]

## Project Structure

```
{project_structure}
```

## Development

[Development instructions will go here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the {license} License - see the LICENSE file for details.
""",
    
    "setup.py": """from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    install_requires=[
        # Add your dependencies here
    ],
    entry_points={{
        'console_scripts': [
            '{command_name}={package_name}.cli:main',
        ],
    }},
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="{project_description}",
    keywords="{keywords}",
    url="https://github.com/yourusername/{project_dir}",
    project_urls={{
        "Bug Tracker": "https://github.com/yourusername/{project_dir}/issues",
    }},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: {license} License",
        "Operating System :: OS Independent",
    ],
)
""",
    
    "requirements.txt": """# Core dependencies
pytest>=7.0.0
black>=23.0.0
flake8>=6.0.0
# Add project-specific dependencies here
""",
    
    "GITHUB_SETUP.md": """# GitHub Setup Instructions

Follow these steps to set up your GitHub repository for {project_name}.

## 1. Create a new repository

1. Go to [GitHub](https://github.com) and sign in to your account.
2. Click the "+" icon in the top right corner and select "New repository".
3. Enter "{project_dir}" as the repository name.
4. Add a description: "{project_description}"
5. Choose visibility (public or private).
6. Check "Add a README file", "Add .gitignore" (choose Python), and "Choose a license" (choose {license}).
7. Click "Create repository".

## 2. Clone the repository locally

```bash
git clone https://github.com/yourusername/{project_dir}.git
cd {project_dir}
```

## 3. Initialize the project structure

Either copy the files from this generated project directory, or run:

```bash
# Assuming you're in the repository root directory
python project_generator.py path/to/project-plan.md .
```

## 4. Initial commit

```bash
git add .
git commit -m "Initial project structure"
git push origin main
```

## 5. Set up GitHub Actions (optional)

1. Create a `.github/workflows` directory in your repository.
2. Add workflow files for CI/CD, such as Python testing and linting.

## 6. Set up branch protection (optional)

1. Go to the repository settings on GitHub.
2. Under "Branches", click "Add rule".
3. Enter "main" as the branch name pattern.
4. Configure the protection rules as needed (e.g., require pull request reviews).
5. Click "Create".

## Next Steps

1. Add detailed documentation in the `docs` directory.
2. Implement the core functionality.
3. Write tests in the `tests` directory.
4. Update the README.md with more detailed information.
""",
    
    "LICENSE-MIT": """MIT License

Copyright (c) {year} Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",

    ".gitignore": """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE specific files
.idea/
.vscode/
*.swp
*.swo

# Project specific
*.log
.DS_Store
""",

    "python_module_init": """\"\"\"
{module_description}
\"\"\"

__version__ = "0.1.0"
""",

    "python_module": """\"\"\"
{module_description}
\"\"\"

def main():
    \"\"\"Main entry point for the module.\"\"\"
    print("Hello from {module_name}!")

if __name__ == "__main__":
    main()
""",

    "python_test": """\"\"\"
Tests for the {module_name} module.
\"\"\"

import pytest
from {package_name}.{module_name} import main

def test_main():
    \"\"\"Test the main function.\"\"\"
    # This is just a placeholder test
    assert True
"""
}

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate project structure from a project plan.")
    parser.add_argument("plan_file", help="Path to the project plan markdown file")
    parser.add_argument("output_dir", help="Directory where the project will be created")
    parser.add_argument("--package-name", help="Python package name (default: derived from project name)")
    parser.add_argument("--license", default="MIT", help="License to use (default: MIT)")
    return parser.parse_args()


def extract_project_info(content):
    """Extract project name, tagline, and description from the project plan."""
    project_info = {
        "project_name": None,
        "project_tagline": None,
        "project_description": None
    }
    
    # Look for project name in "# Project Name" or "**Name**: Project Name"
    name_match = re.search(r'^#\s+(.+?)(?:\s+Project Plan)?$', content, re.MULTILINE)
    if name_match:
        project_info["project_name"] = name_match.group(1).strip()
    else:
        name_match = re.search(r'\*\*Name\*\*:\s*(.+?)$', content, re.MULTILINE)
        if name_match:
            project_info["project_name"] = name_match.group(1).strip()
    
    # Look for tagline in "**Tagline**: ..." or after project name
    tagline_match = re.search(r'\*\*Tagline\*\*:\s*(.+?)$', content, re.MULTILINE)
    if tagline_match:
        project_info["project_tagline"] = tagline_match.group(1).strip()
    elif project_info["project_name"]:
        # Try to find a tagline in the text right after the project name
        sections = content.split('\n\n')
        for i, section in enumerate(sections):
            if project_info["project_name"] in section and i + 1 < len(sections):
                potential_tagline = sections[i + 1].strip()
                if not potential_tagline.startswith('#') and not potential_tagline.startswith('*'):
                    project_info["project_tagline"] = potential_tagline
                    break
    
    # Look for description in "**Description**: ..." or after tagline
    desc_match = re.search(r'\*\*Description\*\*:\s*(.+?)$', content, re.MULTILINE)
    if desc_match:
        project_info["project_description"] = desc_match.group(1).strip()
    elif project_info["project_tagline"]:
        # Try to find a description in the text right after the tagline
        tagline_index = content.find(project_info["project_tagline"])
        if tagline_index >= 0:
            next_section = content[tagline_index + len(project_info["project_tagline"]):].strip()
            next_section = next_section.split('\n\n')[0].strip()
            if next_section and not next_section.startswith('#') and not next_section.startswith('*'):
                project_info["project_description"] = next_section
    
    return project_info


def extract_project_structure(content):
    """Extract project structure from the markdown file."""
    # Look for structure in triple backtick code blocks after "Project Structure"
    structure_match = re.search(r'##?\s+Project\s+Structure.*?```.*?\n(.*?)```', content, re.DOTALL | re.IGNORECASE)
    
    if structure_match:
        structure_text = structure_match.group(1).strip()
        return structure_text
    
    return None


def parse_structure(structure_text):
    """Parse the project structure text into a dictionary."""
    if not structure_text:
        return {}
    
    # Process lines and build structure
    structure = {}
    current_path = []
    
    for line in structure_text.split('\n'):
        if not line.strip():
            continue
            
        # Count leading spaces/indentation to determine level
        indent = len(line) - len(line.lstrip())
        level = indent // 4  # Assuming 4 spaces per indent level
        
        # Clean up the entry
        entry = line.strip().rstrip('/')
        
        # Check if it's a directory or file
        is_dir = '/' in entry or entry.endswith('/') or not '.' in entry.split('/')[-1]
        
        # Adjust current path based on level
        if level < len(current_path):
            current_path = current_path[:level]
        
        # Add to current path
        current_path.append(entry)
        
        # Build the full path
        full_path = '/'.join(current_path[:level+1])
        
        # Add to structure
        if is_dir:
            structure[full_path] = {"type": "directory", "files": {}}
        else:
            parent_path = '/'.join(current_path[:level])
            if parent_path in structure:
                structure[parent_path]["files"][entry] = {"type": "file"}
            else:
                structure[parent_path] = {"type": "directory", "files": {entry: {"type": "file"}}}
    
    return structure


def generate_project_structure(structure, base_dir, project_info, package_name, license_name):
    """Generate the project structure on disk."""
    # Track all created directories to help with module initialization
    created_dirs = []
    
    # First pass: create directories
    for path, info in structure.items():
        if info["type"] == "directory":
            full_path = os.path.join(base_dir, path)
            os.makedirs(full_path, exist_ok=True)
            created_dirs.append(path)
    
    # Second pass: create placeholder files
    for path, info in structure.items():
        if info["type"] == "directory":
            dir_path = os.path.join(base_dir, path)
            for filename, file_info in info["files"].items():
                file_path = os.path.join(dir_path, filename)
                with open(file_path, 'w') as f:
                    f.write(f"# {filename}\n\nPlaceholder for {filename}\n")
    
    # Create Python package structure if there's a src directory
    if "src" in created_dirs:
        src_path = os.path.join(base_dir, "src")
        package_path = os.path.join(src_path, package_name)
        os.makedirs(package_path, exist_ok=True)
        
        # Create __init__.py in the package directory
        with open(os.path.join(package_path, "__init__.py"), 'w') as f:
            f.write(TEMPLATES["python_module_init"].format(
                module_description=f"{project_info['project_name']} package"
            ))
        
        # Create core modules
        for module in ["core", "models", "tools", "cli"]:
            module_dir = os.path.join(package_path, module)
            os.makedirs(module_dir, exist_ok=True)
            
            # Create __init__.py in each module directory
            with open(os.path.join(module_dir, "__init__.py"), 'w') as f:
                f.write(TEMPLATES["python_module_init"].format(
                    module_description=f"{module} module for {project_info['project_name']}"
                ))
            
            # Create a placeholder module file
            with open(os.path.join(module_dir, f"{module}.py"), 'w') as f:
                f.write(TEMPLATES["python_module"].format(
                    module_description=f"Core {module} functionality for {project_info['project_name']}",
                    module_name=module,
                    package_name=package_name
                ))
    
    # Create tests if there's a tests directory
    if "tests" in created_dirs:
        tests_path = os.path.join(base_dir, "tests")
        # Create test_core.py as an example
        with open(os.path.join(tests_path, "test_core.py"), 'w') as f:
            f.write(TEMPLATES["python_test"].format(
                module_name="core",
                package_name=package_name
            ))
    
    # Create key project files
    create_key_files(base_dir, project_info, package_name, license_name, structure_text)


def create_key_files(base_dir, project_info, package_name, license_name, structure_text):
    """Create key project files like README, setup.py, etc."""
    # Format the project structure for README.md
    project_structure = structure_text if structure_text else "Generated project structure will appear here"
    
    # Get project directory name from base_dir
    project_dir = os.path.basename(os.path.abspath(base_dir))
    
    # Create README.md
    with open(os.path.join(base_dir, "README.md"), 'w') as f:
        f.write(TEMPLATES["README.md"].format(
            project_name=project_info["project_name"],
            project_description=project_info["project_description"] or project_info["project_name"],
            project_tagline=project_info["project_tagline"] or "",
            project_structure=project_structure,
            project_dir=project_dir,
            license=license_name
        ))
    
    # Create setup.py
    with open(os.path.join(base_dir, "setup.py"), 'w') as f:
        f.write(TEMPLATES["setup.py"].format(
            package_name=package_name,
            project_description=project_info["project_description"] or project_info["project_name"],
            project_dir=project_dir,
            license=license_name,
            command_name=package_name.replace("_", "-"),
            keywords=package_name.replace("_", ", ")
        ))
    
    # Create requirements.txt
    with open(os.path.join(base_dir, "requirements.txt"), 'w') as f:
        f.write(TEMPLATES["requirements.txt"])
    
    # Create .gitignore
    with open(os.path.join(base_dir, ".gitignore"), 'w') as f:
        f.write(TEMPLATES[".gitignore"])
    
    # Create LICENSE file
    with open(os.path.join(base_dir, "LICENSE"), 'w') as f:
        f.write(TEMPLATES[f"LICENSE-{license_name}"].format(
            year=datetime.now().year
        ))
    
    # Create GitHub setup instructions
    with open(os.path.join(base_dir, "GITHUB_SETUP.md"), 'w') as f:
        f.write(TEMPLATES["GITHUB_SETUP.md"].format(
            project_name=project_info["project_name"],
            project_description=project_info["project_description"] or project_info["project_name"],
            project_dir=project_dir,
            license=license_name
        ))


def main():
    """Main entry point for the script."""
    args = parse_args()
    
    # Read the project plan markdown file
    with open(args.plan_file, 'r') as f:
        content = f.read()
    
    # Extract project information
    project_info = extract_project_info(content)
    
    # Determine package name if not provided
    if args.package_name:
        package_name = args.package_name
    else:
        # Convert project name to a valid package name
        if project_info["project_name"]:
            package_name = project_info["project_name"].lower().replace('-', '_').replace(' ', '_')
            # Remove any non-alphanumeric characters
            package_name = re.sub(r'[^a-z0-9_]', '', package_name)
        else:
            # Use the output directory name as fallback
            package_name = os.path.basename(os.path.abspath(args.output_dir)).lower().replace('-', '_').replace(' ', '_')
    
    # Extract and parse project structure
    structure_text = extract_project_structure(content)
    structure = parse_structure(structure_text)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate project structure
    generate_project_structure(structure, args.output_dir, project_info, package_name, args.license)
    
    print(f"Project structure generated in {args.output_dir}")
    print(f"Package name: {package_name}")
    print(f"Check GITHUB_SETUP.md for instructions on setting up the GitHub repository")


if __name__ == "__main__":
    main()
