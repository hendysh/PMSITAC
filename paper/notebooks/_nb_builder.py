"""Minimal .ipynb builder -- constructs valid Jupyter notebook JSON directly,
since nbformat isn't installable in this environment. The notebook schema
used here (nbformat 4.5) is what current Jupyter/JupyterLab/VS Code expect."""

import json


def code_cell(source_lines):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_lines,
    }


def markdown_cell(source_lines):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source_lines,
    }


def build_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {
                "name": "python", "version": "3.11", "mimetype": "text/x-python",
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py", "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def src(text):
    """Split a multi-line string into the list-of-lines-with-\\n format
    the notebook JSON schema expects, dropping a possible trailing newline
    on the last line (Jupyter convention)."""
    lines = text.strip("\n").split("\n")
    return [line + "\n" for line in lines[:-1]] + [lines[-1]] if lines else []


def write_notebook(path, cells):
    nb = build_notebook(cells)
    with open(path, "w") as f:
        json.dump(nb, f, indent=1)
    print(f"Wrote {path}")
