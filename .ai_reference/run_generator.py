
# Simple wrapper to run the library generator
import importlib.util
import sys
from pathlib import Path

# Path to the library generator
script_path = Path(__file__).parent / "library_generator.py"
project_root = Path(__file__).parent.parent

# Load the module
spec = importlib.util.spec_from_file_location("library_generator", script_path)
library_generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(library_generator)

# Run the generator
print(f"Running library generator for project at {project_root}")
library_generator.generate_library(project_root)
print("Library generation completed")
