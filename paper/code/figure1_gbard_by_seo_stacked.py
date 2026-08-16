"""
Figure 1: Government budget allocations for R&D (GBARD) by socio-economic
objective, true SAEs vs New Zealand (2023).

Publication version: no title or source caption baked into the image --
see ../figure_captions.md for that text to use in the manuscript.

Reads:  ../data/figure1_gbard_by_seo_stacked.csv
Writes: ../figures/figure1_gbard_by_seo_stacked.png
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from figure_style import apply_style, SEO_COLORS, SEO_ORDER

apply_style()

df = pd.read_csv("../data/figure1_gbard_by_seo_stacked.csv", index_col="entity")

fig, ax = plt.subplots(figsize=(11.8, 6))
bottom = np.zeros(len(df))
x = np.arange(len(df))
for seo in SEO_ORDER:
    vals = df[seo].values * 100
    ax.bar(x, vals, bottom=bottom, label=seo, color=SEO_COLORS[seo],
           edgecolor="white", linewidth=0.4, width=0.68)
    bottom += vals

ax.set_xticks(x)
ax.set_xticklabels(df.index, rotation=45, ha="right")
for i, label in enumerate(df.index):
    if label in ("SAE average", "New Zealand"):
        ax.get_xticklabels()[i].set_fontweight("bold")

ax.set_ylabel("Share of GBARD (%)")
ax.set_ylim(0, 100)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=6, frameon=False, fontsize=8.5)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(rect=[0, 0.1, 1, 1])
fig.savefig("../figures/figure1_gbard_by_seo_stacked.png", bbox_inches="tight")
print("Saved ../figures/figure1_gbard_by_seo_stacked.png")
