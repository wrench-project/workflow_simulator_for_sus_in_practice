import os
import glob

# Automatically import all Python files in the current directory (except __init__.py)
module_files = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = []

for file in module_files:
    module_name = os.path.basename(file)[:-3]  # Remove .py extension
    if module_name != "__init__":  # Skip __init__.py itself
        __all__.append(module_name)
        exec(f"from .{module_name} import *")
