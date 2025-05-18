"""
DEPRECATED: This module provides a compatibility layer for the old configurator_new module.

Please use aitoolkit.gui.legacy.configurator_unified instead.
"""

import sys
import warnings

# Emit a deprecation warning
warnings.warn(
    "The configurator_new module is deprecated. "
    "Please use aitoolkit.gui.legacy.configurator_unified instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import the AIDevToolkitGUI class from the new location
from aitoolkit.gui.legacy.configurator_unified import AIDevToolkitGUI

# Ensure we re-export anything that might have been imported
__all__ = ['AIDevToolkitGUI']