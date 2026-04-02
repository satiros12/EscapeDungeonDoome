"""
Pytest configuration for WebDoom tests
"""

import sys
import os

# Ensure src directory is at the front of the path for ALL tests
# This must run BEFORE any other imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, "src")

# Remove any existing config/module conflicts
for mod in list(sys.modules.keys()):
    if mod == "config" or mod.startswith("config.") or mod.startswith("src."):
        if "site-packages" not in str(getattr(sys.modules.get(mod), "__file__", "")):
            del sys.modules[mod]

# Insert src at the front
if src_path not in sys.path:
    sys.path.insert(0, src_path)
