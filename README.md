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