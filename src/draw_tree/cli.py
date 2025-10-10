#!/usr/bin/env python3
"""
Command-line interface for draw_tree package.
"""
import sys
from pathlib import Path
from .core import (
    commandline, draw_tree, generate_pdf, generate_png, generate_tex
)


def main():
    """Main entry point for the draw_tree CLI."""
    # Display help if no arguments provided
    if len(sys.argv) == 1:
        print("DrawTree - Game tree drawing tool")
        print()
        print("Usage:")
        print("  draw_tree <file.ef> [options]           # Generate TikZ code")
        print("  draw_tree <file.ef> --pdf [options]     # Generate PDF (requires pdflatex)")
        print("  draw_tree <file.ef> --png [options]     # Generate PNG (requires pdflatex + imagemagick/ghostscript)")
        print("  draw_tree <file.ef> --tex [options]     # Generate LaTeX document")
        print("  draw_tree <file.ef> --output=name.ext   # Generate with custom filename (.pdf, .png, or .tex)")
        print()
        print("Options:")
        print("  scale=X.X    Set scale factor (0.01 to 100)")
        print("  grid         Show helper grid")
        print("  --pdf        Generate PDF output instead of TikZ")
        print("  --png        Generate PNG output instead of TikZ")
        print("  --tex        Generate LaTeX document instead of TikZ")
        print("  --output=X   Specify output filename (.pdf, .png, or .tex extension determines format)")
        print("  --dpi=X      Set PNG resolution in DPI (72-2400, default: 300)")
        print()
        print("Examples:")
        print("  draw_tree games/example.ef --pdf")
        print("  draw_tree games/example.ef --png --dpi=600")
        print("  draw_tree games/example.ef --tex")
        print("  draw_tree games/example.ef --output=mygame.tex scale=0.8")
        print()
        print("Note: PDF/PNG generation requires pdflatex. PNG also needs ImageMagick or Ghostscript.")
        sys.exit(0)
    
    # Process command-line arguments
    output_mode, pdf_requested, png_requested, tex_requested, output_file, dpi = commandline(sys.argv)
    
    # Import the core module to access global variables after commandline() has set them
    from . import core
    current_ef_file = core.ef_file
    current_scale = core.scale
    current_grid = core.grid
    
    try:
        if output_mode == "pdf":
            print(f"Generating PDF: {output_file}")
            pdf_path = generate_pdf(
                ef_file=current_ef_file,
                output_pdf=output_file,
                scale_factor=current_scale,
                show_grid=current_grid
            )
            print(f"PDF generated successfully: {pdf_path}")
        
        elif output_mode == "png":
            # Use default PNG filename if none specified
            if output_file is None:
                base_name = Path(current_ef_file).stem
                output_file = f"{base_name}.png"
            print(f"Generating PNG: {output_file}")
            png_path = generate_png(
                ef_file=current_ef_file,
                output_png=output_file,
                scale_factor=current_scale,
                show_grid=current_grid,
                dpi=dpi if dpi is not None else 300
            )
            print(f"PNG generated successfully: {png_path}")
        
        elif output_mode == "tex":
            # Use default TEX filename if none specified
            if output_file is None:
                base_name = Path(current_ef_file).stem
                output_file = f"{base_name}.tex"
            print(f"Generating LaTeX: {output_file}")
            tex_path = generate_tex(
                ef_file=current_ef_file,
                output_tex=output_file,
                scale_factor=current_scale,
                show_grid=current_grid
            )
            print(f"LaTeX generated successfully: {tex_path}")
        
        else:
            # Generate TikZ code (original behavior)
            tikz_code = draw_tree(
                ef_file=current_ef_file, 
                scale_factor=current_scale, 
                show_grid=current_grid
            )
            
            # Output the complete TikZ code
            print(tikz_code)
        
    except FileNotFoundError:
        print(f"Error: Could not find file {current_ef_file}", file=sys.stderr)
        print("Make sure the .ef file exists in the current directory", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing {current_ef_file}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()