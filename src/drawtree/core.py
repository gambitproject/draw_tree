"""
Core functionality for DrawTree package.

This module provides the main API functions for generating TikZ code from 
extensive form game files.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Union

from .engine import (
    create_tikz_from_file as _create_tikz_from_file,
)


def get_macros_file_path() -> str:
    """Get the path to the bundled macros-drawtree.tex file."""
    # Try the development path first
    current_dir = Path(__file__).parent
    dev_path = current_dir / 'data' / 'macros-drawtree.tex'
    
    if dev_path.exists():
        return str(dev_path)
    
    # Fallback - return the expected path anyway
    return str(dev_path)


def create_tikz_from_file(tex_file_path: str, macros_file_path: Optional[str] = None) -> str:
    """
    Create TikZ code by combining macros and game tree content from separate files.

    Args:
        tex_file_path: Path to the .tex file containing the tikzpicture content
        macros_file_path: Path to the macros file. If None, uses bundled macros.

    Returns:
        Complete TikZ code as a string, ready for use in Jupyter notebooks or LaTeX documents.
    """
    if macros_file_path is None:
        macros_file_path = get_macros_file_path()
    
    return _create_tikz_from_file(tex_file_path, macros_file_path)


def draw_tree(
    game: Union[str, Path], 
    name: Optional[str] = None,
    render_as: str = 'tikz',
    output_dir: Optional[Union[str, Path]] = None,
    scale: float = 1.0,
    grid: bool = False
) -> Optional[str]:
    """
    Generate and optionally render a game tree from an extensive form (.ef) file.
    
    This is the main high-level API function that handles the complete workflow
    from .ef file to final output.

    Args:
        game: Path to the .ef file containing the game definition
        name: Base name for output files. If None, derived from game filename
        render_as: Output format - 'tikz', 'pdf', or 'png'
        output_dir: Directory for output files. If None, uses game file directory
        scale: Scale factor for the diagram (default: 1.0)
        grid: Whether to show grid lines (default: False)

    Returns:
        For 'tikz': Returns the TikZ code as a string
        For 'pdf'/'png': Returns path to created file, or None if creation failed

    Raises:
        FileNotFoundError: If the game file doesn't exist
        ValueError: If render_as is not supported
        RuntimeError: If PDF/PNG generation fails
    """
    game_path = Path(game)
    if not game_path.exists():
        raise FileNotFoundError(f"Game file not found: {game}")
    
    if render_as not in ['tikz', 'pdf', 'png']:
        raise ValueError(f"Unsupported render_as format: {render_as}. Use 'tikz', 'pdf', or 'png'.")
    
    # Determine output name and directory
    if name is None:
        name = game_path.stem
    
    if output_dir is None:
        output_dir = game_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create temporary file for TikZ content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as temp_tex:
        temp_tex_path = temp_tex.name
        
        try:
            # Generate TikZ content using the engine
            _generate_tex_from_ef(str(game_path), temp_tex_path, scale, grid)
            
            if render_as == 'tikz':
                # Return TikZ code directly
                return create_tikz_from_file(temp_tex_path)
            
            elif render_as in ['pdf', 'png']:
                # Generate PDF first
                pdf_path = output_dir / f"{name}.pdf"
                success = _generate_pdf(temp_tex_path, pdf_path)
                
                if not success:
                    raise RuntimeError("Failed to generate PDF")
                
                if render_as == 'pdf':
                    return str(pdf_path)
                else:  # png
                    png_path = output_dir / f"{name}.png"
                    success = _convert_pdf_to_png(pdf_path, png_path)
                    if success:
                        return str(png_path)
                    else:
                        raise RuntimeError("Failed to convert PDF to PNG")
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_tex_path)
            except OSError:
                pass
    
    return None


def _generate_tex_from_ef(ef_file: str, output_tex: str, scale_factor: float, show_grid: bool) -> None:
    """Generate TikZ content from .ef file using the original engine."""
    import sys
    from io import StringIO
    from . import engine
    
    # Save original stdout and global state
    original_stdout = sys.stdout
    original_outstream = engine.outstream.copy()
    original_stream0 = engine.stream0.copy()
    original_nodes = engine.nodes.copy()
    original_xshifts = engine.xshifts.copy()
    original_scale = engine.scale
    original_grid = engine.grid
    
    try:
        # Reset global state
        engine.outstream.clear()
        engine.stream0.clear()
        engine.nodes.clear()
        engine.xshifts.clear()
        
        # Set parameters
        engine.scale = scale_factor
        engine.grid = show_grid
        
        # Capture output
        sys.stdout = StringIO()
        
        # Process the .ef file using original logic
        ef_lines = engine.readfile(ef_file)
        
        # Start tikz picture
        engine.outs("\\begin{tikzpicture}[scale=" + str(scale_factor), engine.stream0)
        ss = "  , StealthFill/.tip={Stealth[line width=.7pt"
        engine.outs(ss+",inset=0pt,length=13pt,angle'=30]}]", engine.stream0)
        ss = ""
        if not show_grid:
            ss = "% "
        engine.outs(ss+"\\draw [help lines, color=green] (-5,0) grid (5,-6);", engine.stream0)
        
        # Process each line
        for line in ef_lines:
            engine.comment(line)
            words = line.split()
            if len(words) > 0:
                if words[0] == "player":
                    engine.player(words)
                elif words[0] == "level":
                    engine.level(words)
                elif words[0] == "iset":
                    engine.isetgen(words)
        
        # Output nodes and close
        engine.drawnodes()
        engine.outs("\\end{tikzpicture}", engine.stream0)
        
        # Write to file
        with open(output_tex, 'w') as f:
            for line in engine.stream0:
                f.write(line + '\n')
                
    finally:
        # Restore original state
        sys.stdout = original_stdout
        engine.outstream.clear()
        engine.outstream.extend(original_outstream)
        engine.stream0.clear()
        engine.stream0.extend(original_stream0)
        engine.nodes.clear()
        engine.nodes.update(original_nodes)
        engine.xshifts.clear()
        engine.xshifts.update(original_xshifts)
        engine.scale = original_scale
        engine.grid = original_grid


def _generate_pdf(tex_file: str, output_pdf: Path) -> bool:
    """Generate PDF from TikZ file using pdflatex."""
    # Create a complete LaTeX document
    tikz_content = create_tikz_from_file(tex_file)
    
    latex_document = f"""\\documentclass{{article}}
\\usepackage{{tikz}}
\\usetikzlibrary{{shapes}}
\\usetikzlibrary{{arrows.meta}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}

\\begin{{document}}
\\thispagestyle{{empty}}

{tikz_content}

\\end{{document}}
"""
    
    # Create temporary directory for LaTeX compilation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        latex_file = temp_dir_path / "document.tex"
        
        # Write LaTeX file
        with open(latex_file, 'w') as f:
            f.write(latex_document)
        
        # Run pdflatex
        try:
            result = subprocess.run([
                'pdflatex', 
                '-interaction=nonstopmode',
                '-output-directory', str(temp_dir_path),
                str(latex_file)
            ], capture_output=True, text=True, cwd=temp_dir_path)
            
            if result.returncode == 0:
                # Copy the generated PDF to final location
                generated_pdf = temp_dir_path / "document.pdf"
                if generated_pdf.exists():
                    shutil.copy2(generated_pdf, output_pdf)
                    return True
            
            print(f"pdflatex error: {result.stderr}")
            return False
            
        except FileNotFoundError:
            print("pdflatex not found. Please install LaTeX (e.g., MacTeX on macOS)")
            return False
        except Exception as e:
            print(f"Error running pdflatex: {e}")
            return False


def _convert_pdf_to_png(pdf_path: Path, png_path: Path, dpi: int = 300) -> bool:
    """Convert PDF to PNG using ImageMagick or similar."""
    try:
        # Try ImageMagick convert
        result = subprocess.run([
            'convert', 
            '-density', str(dpi),
            '-quality', '90',
            str(pdf_path),
            str(png_path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and png_path.exists():
            return True
            
    except FileNotFoundError:
        pass
    
    try:
        # Try pdftoppm (from poppler-utils)
        result = subprocess.run([
            'pdftoppm',
            '-png',
            '-r', str(dpi),
            str(pdf_path),
            str(png_path.with_suffix(''))
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # pdftoppm adds -1.png suffix, rename it
            generated_png = png_path.with_name(f"{png_path.stem}-1.png")
            if generated_png.exists():
                generated_png.rename(png_path)
                return True
                
    except FileNotFoundError:
        pass
    
    print("PNG conversion failed. Please install ImageMagick or poppler-utils.")
    return False