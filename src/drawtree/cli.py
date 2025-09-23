"""
Command-line interface for DrawTree package.

Provides a simple CLI for generating PDFs directly from .ef files.
"""
import argparse
import sys
from pathlib import Path

from .core import draw_tree


def main() -> None:
    """Main entry point for the drawtree command-line tool."""
    parser = argparse.ArgumentParser(
        description='Generate game tree diagrams from extensive form (.ef) files',
        prog='drawtree'
    )
    
    parser.add_argument(
        'game',
        help='Path to the .ef file containing the game definition'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file name (without extension). Defaults to game filename.'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory. Defaults to the game file directory.'
    )
    
    parser.add_argument(
        '--format',
        choices=['pdf', 'png', 'tikz'],
        default='pdf',
        help='Output format (default: pdf)'
    )
    
    parser.add_argument(
        '--scale',
        type=float,
        default=1.0,
        help='Scale factor for the diagram (default: 1.0)'
    )
    
    parser.add_argument(
        '--grid',
        action='store_true',
        help='Show grid lines in the output'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    game_path = Path(args.game)
    if not game_path.exists():
        print(f"Error: Game file not found: {args.game}", file=sys.stderr)
        sys.exit(1)
    
    if not game_path.suffix.lower() == '.ef':
        print(f"Warning: File doesn't have .ef extension: {args.game}", file=sys.stderr)
    
    try:
        result = draw_tree(
            game=game_path,
            name=args.output,
            render_as=args.format,
            output_dir=args.output_dir,
            scale=args.scale,
            grid=args.grid
        )
        
        if args.format == 'tikz':
            print(result)
        else:
            if result:
                print(f"Generated: {result}")
            else:
                print("Failed to generate output", file=sys.stderr)
                sys.exit(1)
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()