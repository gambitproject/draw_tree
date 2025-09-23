# Steps to run (on MacOS)

1. Install [MacTEX](https://www.tug.org/mactex/mactex-download.html)
    - This took ages because it's 5.9 GB...
    - Is there an easier way to package LaTeX with PyGambit?
2. Create the tex from the ef file:

    ```
    python drawtree.py games/example.ef > o.tex
    ```
3. Run this command to process the wrapper tex file:

    ```
    pdflatex q.tex
    ```
4. Open the resulting PDF file `q.pdf`


## Python API

Note, images do not render well in VSCode, so open Jupyter Lab or Jupyter Notebook to see the images.

1. Create a virtual environment (tested with Python 3.13) e.g.

    ```
    conda create --name draw_tree python=3.13
    conda activate draw_tree
    ```
2. Install dependencies

    ```
    pip install -r requirements.txt
    ```
3. In a Python script or Jupyter notebook, run:

    ```python
    from drawtree import draw_tree
    draw_tree(
        game='games/example.ef',
        name='example',
        render_as='pdf'
    )
    ```
    The `render_as` argument can be 'pdf', 'png', or 'tikz'. The first two will create files `example.pdf` or `example.png` in the current directory. The last will return a string with the TikZ code that you can use in your own LaTeX documents, or view in your Jupyter notebook with.