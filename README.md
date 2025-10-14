# draw_tree

Game tree drawing tool for extensive form games that generates TikZ code, LaTeX documents, PDFs, and PNGs.

## Installation

Clone the repo and install the package using pip:

```bash
git clone https://github.com/gambitproject/draw_tree
cd draw_tree
pip install -e .
```

## Requirements

- Python 3.7+ (tested on 3.13)
- LaTeX with TikZ (for PDF/PNG generation)
- (optional) ImageMagick or Ghostscript or Poppler (for PNG generation)

### Installing LaTeX

Note: PDF and PNG generation require `pdflatex` to be installed and available in PATH. Tested methods have a ✅ next to them. Methods include:

- macOS:
    - Install [MacTEX](https://www.tug.org/mactex/mactex-download.html) ✅
    - `brew install --cask mactex`
- Ubuntu:
    - `sudo apt-get install texlive-full` ✅
- Windows: Install [MiKTeX](https://miktex.org/download)

### PNG generation

PNG generation will default to using any of ImageMagick or Ghostscript or Poppler that are installed. If none are installed, try one of the following:
- macOS:
    - `brew install imagemagick`
    - `brew install ghostscript`
    - `brew install poppler`
- Ubuntu:
    - `sudo apt-get install imagemagick`
    - `sudo apt-get install ghostscript`
    - `sudo apt-get install poppler-utils`
- Windows: Install ImageMagick or Ghostscript from their websites

## CLI

By default, `draw_tree` generates TikZ code and prints it to standard output.
There are also options to generate a complete LaTeX document, a PDF or a PNG directly, either by specifying the desired format or by using the output filename extension:

```bash
draw_tree games/example.ef                                 # Prints TikZ code to stdout
draw_tree games/example.ef --tex                           # Creates example.tex
draw_tree games/example.ef --output=custom.tex             # Creates custom.tex
draw_tree games/example.ef --pdf                           # Creates example.pdf
draw_tree games/example.ef --png                           # Creates example.png
draw_tree games/example.ef --png --dpi=600                 # Creates high-res example.png (72-2400, default: 300)
draw_tree games/example.ef --output=mygame.png scale=0.8   # Creates mygame.png with 0.8 scaling (0.01 to 100)
```

## Python API

You can also use `draw_tree` as a Python library:

```python
from draw_tree import generate_tex, generate_pdf, generate_png
generate_tex('games/example.ef')                                    # Creates example.tex
generate_tex('games/example.ef', output_tex='custom.tex')           # Creates custom.tex
generate_pdf('games/example.ef')                                    # Creates example.pdf
generate_png('games/example.ef')                                    # Creates example.png
generate_png('games/example.ef', dpi=600)                           # Creates high-res example.png (72-2400, default: 300)
generate_png('games/example.ef', output_png='mygame.png', scale_factor=0.8)    # Creates mygame.png with 0.8 scaling (0.01 to 100)
```

### Rendering in Jupyter Notebooks

First install the requirements, which include the `jupyter-tikz` extension:
```bash
pip install -r requirements.txt
```

In a Jupyter notebook, run:

```python
%load_ext jupyter_tikz
from draw_tree import draw_tree
example_tikz = draw_tree('games/example.ef')
get_ipython().run_cell_magic("tikz", "", example_tikz)
```

## Developer docs: Testing

The project includes a comprehensive test suite using pytest. To run the tests:

Install requirements:
```bash
pip install -r requirements.txt
```

Run all tests:
```bash
pytest tests/ -v
```

Run tests with coverage:
```bash
pytest tests/ --cov=draw_tree --cov-report=html
```
