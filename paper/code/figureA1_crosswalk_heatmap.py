"""
Figure A1: The fitted SEO->FORD crosswalk matrix itself, as a heatmap.
Rows (SEO categories) sum to 1. This is the matrix used to translate NZ
and SAE SEO shares into FORD shares in Figure 3 -- showing it directly
makes the fit's structure inspectable (e.g. the near-diagonal pattern for
Health->Medical & health, Agriculture->Agricultural sciences,
Society->Social sciences is a basic sanity check on the fit).

Publication version: no title or source caption baked into the image --
see ../figure_captions.md for that text to use in the manuscript.

Reads:  ../data/crosswalk_matrix.csv
Writes: ../figures/figureA1_crosswalk_heatmap.png
"""

import pandas as pd
import matplotlib.pyplot as plt
from figure_style import apply_style, SEO_ORDER, FORD_ORDER

apply_style()

W = pd.read_csv("../data/crosswalk_matrix.csv", index_col=0)
W = W.loc[SEO_ORDER]       # consistent row order with rest of paper
W.columns = FORD_ORDER     # display names, same order as underlying columns

fig, ax = plt.subplots(figsize=(9, 8))
im = ax.imshow(W.values, cmap="Blues", vmin=0, vmax=1, aspect="auto")

ax.set_xticks(range(len(W.columns)))
ax.set_xticklabels(W.columns, rotation=30, ha="right")
ax.set_yticks(range(len(W.index)))
ax.set_yticklabels(W.index)

# Annotate each cell with its value; flip text color for readability on dark cells
for i in range(W.shape[0]):
    for j in range(W.shape[1]):
        val = W.values[i, j]
        color = "white" if val > 0.55 else "#333333"
        ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=9)

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Share of SEO category mapped to FORD field")
ax.set_xlabel("FORD field")
ax.set_ylabel("SEO category")

fig.tight_layout()
fig.savefig("../figures/figureA1_crosswalk_heatmap.png", bbox_inches="tight")
print("Saved ../figures/figureA1_crosswalk_heatmap.png")
