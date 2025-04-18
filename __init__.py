"""
Notegold: Meeting Notes to Content Flywheel

A modular system for transforming meeting notes into valuable content assets.
"""

__version__ = "0.1.0"

# Enable transparent imports
# This allows code to use "src.something" even though the package is "notegold"
import sys
import importlib

# Import the notegold.src module first, then create the alias
if 'notegold.src' not in sys.modules:
    importlib.import_module('notegold.src')

# Now create the alias from src to notegold.src
if 'src' not in sys.modules:
    sys.modules['src'] = sys.modules['notegold.src']
