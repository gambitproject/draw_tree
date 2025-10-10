# draw_tree

🚧 `draw_tree` is a work in progress and not currently usable. 🚧

## Requirements

- Python 3.7+
- LaTeX with TikZ (for PDF/PNG generation)
- (optional) ImageMagick or Ghostscript or Poppler (for PNG generation)

### Installing LaTeX

Note: PDF and PNG generation require `pdflatex` to be installed and available in PATH. For example, on MacOS you can install [MacTEX](https://www.tug.org/mactex/mactex-download.html). Other options include:

- macOS: `brew install --cask mactex` (may require adding `/Library/TeX/texbin` to your PATH)
- Ubuntu: `sudo apt-get install texlive-full`
- Windows: `Install MiKTeX from https://miktex.org/download`

### PNG generation

PNG generation also requires either ImageMagick or Ghostscript or Poppler to be installed. For example:
- macOS: `brew install imagemagick ghostscript poppler`
- Ubuntu: `sudo apt-get install imagemagick ghostscript poppler-utils`
- Windows: `Install ImageMagick or Ghostscript from their websites`

## CLI

By default, `draw_tree` generates TikZ code and prints it to standard output.
There are also options to generate a complete LaTeX document, a PDF or a PNG directly, either by specifying the desired format or by using the output filename extension:

```bash
python drawtree.py games/example.ef                                 # Prints TikZ code to stdout
python drawtree.py games/example.ef --tex                           # Creates example.tex
python drawtree.py games/example.ef --output=custom.tex             # Creates custom.tex
python drawtree.py games/example.ef --pdf                           # Creates example.pdf
python drawtree.py games/example.ef --png                           # Creates example.png
python drawtree.py games/example.ef --png --dpi=600                 # Creates high-res example.png (72-2400, default: 300)
python drawtree.py games/example.ef --output=mygame.png scale=0.8   # Creates mygame.png with 0.8 scaling (0.01 to 100)
```

## Displaying in Jupyter Notebooks

Note, images do not render well in VSCode, so open Jupyter Lab or Jupyter Notebook to see the images.

In a Jupyter notebook, run:

```python
%load_ext jupyter_tikz
from drawtree import draw_tree
example_tikz = draw_tree('example.ef')
get_ipython().run_cell_magic("tikz", "", example_tikz)  # Requires the jupyter-tikz extension
```

## Developer docs: Testing

The project includes a comprehensive test suite using pytest. To run the tests:

Install dependencies:
```bash
pip install -r requirements.txt
```

Run all tests:
```bash
pytest test_drawtree.py -v
```

Run tests with coverage:
```bash
pytest test_drawtree.py --cov=drawtree --cov-report=html
```
