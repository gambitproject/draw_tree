"""
DrawTree: Generate game tree diagrams from extensive form files.

A Python package for creating TikZ-based game tree visualizations from 
extensive form (.ef) files, with support for Jupyter notebooks and 
command-line usage.
"""

from .version import __version__
from .core import draw_tree, create_tikz_from_file

__all__ = ['draw_tree', 'create_tikz_from_file', '__version__']