# draw_tree

🚧 `draw_tree` is a work in progress and not currently usable. 🚧


## CLI

By default, `draw_tree` generates TikZ code and prints it to standard output; this can copied into a LaTeX document.
There are also options to generate PDF or PNG files directly, either by specifying the desired format or by using the output filename extension:

```bash
python drawtree.py games/example.ef                                 # Prints TikZ code to stdout
python drawtree.py games/example.ef --pdf                           # Creates example.pdf
python drawtree.py games/example.ef --output=custom.pdf             # Creates custom.pdf
python drawtree.py games/example.ef --png                           # Creates example.png
python drawtree.py games/example.ef --png --dpi=600                 # Creates high-res example.png (600 DPI)
python drawtree.py games/example.ef --output=mygame.png scale=0.8   # Creates mygame.png with 0.8 scaling
```

Note: PDF and PNG generation require `pdflatex` to be installed and available in PATH.

For example, on MacOS you can install [MacTEX](https://www.tug.org/mactex/mactex-download.html)

## Python API

Note, images do not render well in VSCode, so open Jupyter Lab or Jupyter Notebook to see the images.

In a ~~Python script or~~ Jupyter notebook, run:

```python
from drawtree import draw_tree
example_tikz = draw_tree('example.ef')
get_ipython().run_cell_magic("tikz", "", example_tikz)  # Requires the jupyter-tikz extension
```

## Developer docs: Testing

The project includes a comprehensive test suite using pytest. To run the tests:

1. Create a virtual environment (tested with Python 3.13) e.g.
```bash
conda create --name draw_tree python=3.13
conda activate draw_tree
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run all tests:
```bash
pytest test_drawtree.py -v
```

4. Run tests with coverage:
```bash
pip install pytest-cov
pytest test_drawtree.py --cov=drawtree --cov-report=html
```
