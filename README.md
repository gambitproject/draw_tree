# draw_tree

🚧 `draw_tree` is a work in progress and not currently usable. 🚧


## CLI

By default, `draw_tree` generates TikZ code and prints it to standard output.
This can copied into a LaTeX document. **TODO:** is this accurate?

To generate TikZ code from an EF file:

```bash
python drawtree.py games/example.ef
```

You can also create a PDF from the EF file:

```bash
python drawtree.py games/example.ef --pdf                    # Creates example.pdf
python drawtree.py games/example.ef --output=custom.pdf      # Creates custom.pdf
```

Note: PDF generation requires `pdflatex` to be installed and available in PATH.

For example, on MacOS you can install [MacTEX](https://www.tug.org/mactex/mactex-download.html)

## Python API

Note, images do not render well in VSCode, so open Jupyter Lab or Jupyter Notebook to see the images.

In a ~~Python script or~~ Jupyter notebook, run:

```python
from drawtree import draw_tree
example_tikz = draw_tree('example.ef')
get_ipython().run_cell_magic("tikz", "", example_tikz)
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
