"""
Draw Tree - Game tree drawing tool

This package provides functionality to generate TikZ code for game trees
from extensive form (.ef) files, with support for Jupyter notebooks.
"""

__version__ = "0.1.0"

from .core import (
    draw_tree,
    generate_tex,
    generate_pdf,
    generate_png,
    ef_to_tex,
    latex_wrapper
)

__all__ = [
    "draw_tree",
    "generate_tex", 
    "generate_pdf",
    "generate_png",
    "ef_to_tex",
    "latex_wrapper"
]