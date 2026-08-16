"""
Generates all .ipynb files in this folder by parsing the corresponding
../code/figureN_*.py script directly, rather than duplicating each
script's logic by hand. This guarantees the notebook and script versions
of each figure can't drift apart -- a problem earlier hand-duplicated
versions of this generator ran into repeatedly.

Each script is split into three cells based on structural markers common
to all of them:
  1. imports + apply_style()
  2. data loading (through the line before "fig, ax = plt.subplots(...)")
  3. the plot-building and fig.savefig(...) code

The module docstring becomes the notebook's markdown intro cell. Run this
whenever a code/figureN_*.py script changes, to keep notebooks in sync.
"""

import re
from _nb_builder import code_cell, markdown_cell, write_notebook, src

FIGURES = [
    "figure1_gbard_by_seo_stacked",
    "figure2_gak_by_country",
    "figure3_ford_comparison",
    "figureA1_crosswalk_heatmap",
]

# Variable name holding the loaded data in each script, for the display
# line appended to the "load data" cell (defaults to "df").
DISPLAY_VAR = {
    "figureA1_crosswalk_heatmap": "W",
}


def build_notebook(fig_name):
    text = open(f"../code/{fig_name}.py").read()
    doc_match = re.match(r'"""(.*?)"""\n\n(.*)', text, re.DOTALL)
    docstring, rest = doc_match.group(1).strip(), doc_match.group(2)

    lines = rest.split("\n")
    imp_end = next(i for i, l in enumerate(lines) if l.strip() == "apply_style()")
    imports_section = "\n".join(lines[:imp_end + 1])

    remainder = lines[imp_end + 1:]
    while remainder and remainder[0].strip() == "":
        remainder.pop(0)
    plot_start = next(i for i, l in enumerate(remainder) if l.startswith("fig, ax"))
    load_section = "\n".join(remainder[:plot_start]).rstrip()
    plot_section = "\n".join(remainder[plot_start:]).rstrip()

    display_var = DISPLAY_VAR.get(fig_name, "df")
    load_section_with_display = f"{load_section}\n{display_var}"

    doc_lines = docstring.split("\n")
    title_line = doc_lines[0]
    body = "\n".join(doc_lines[1:]).strip()
    md_text = (f"# {title_line}\n\n{body}\n\n"
               "(Title and source caption for the published figure are in "
               "`../figure_captions.md`, not baked into this image.)")

    write_notebook(f"{fig_name}.ipynb", [
        markdown_cell(src(md_text)),
        code_cell(src(imports_section)),
        code_cell(src(load_section_with_display)),
        code_cell(src(plot_section + "\nplt.show()")),
    ])


if __name__ == "__main__":
    for fig_name in FIGURES:
        build_notebook(fig_name)
    print(f"\nAll {len(FIGURES)} figure notebooks generated.")
