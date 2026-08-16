"""
Figure 3: NZ vs SAE research priorities by field, using the empirically-
fitted SEO->FORD crosswalk (see 00_prepare_data.py for how this table and
the crosswalk matrix itself were derived) and the 14-country true-SAE
benchmark.

The SAE average bars carry a leave-one-country-out (jackknife) error bar:
for each of the 14 true SAEs, the SAE SEO average is recomputed excluding
that country, then pushed through the same already-fitted crosswalk. This
tests sensitivity of the benchmark to which SAEs happen to be in the
sample -- NOT sensitivity of the crosswalk fit itself (that's a separate
question, already assessed via the leave-one-country-out cross-validation
reported in Figure A1's caption, MAE 0.047 vs 0.055 for the static heuristic). NZ
current/proposed bars carry no error bars: each is a single country's own
SEO shares pushed through the same fixed crosswalk, so excluding an SAE
from the benchmark doesn't change NZ's own value.

Publication version: no title or source caption baked into the image --
see ../figure_captions.md for that text to use in the manuscript.

Reads:  ../data/figure3_ford_comparison.csv
Writes: ../figures/figure3_ford_comparison.png
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from figure_style import apply_style, BLUE, ORANGE, GREEN, FORD_ORDER

apply_style()

df = pd.read_csv("../data/figure3_ford_comparison.csv", index_col="ford_category")
df.index = FORD_ORDER  # relabel from underscore codes to display names, same order
se = df["SAE_average_jackknife_SE"].values

fig, ax = plt.subplots(figsize=(10, 5.5))
x = np.arange(len(df))
width = 0.26

ax.bar(x - width, df["SAE_average"], width, label="SAE average", color=BLUE,
       yerr=se, capsize=3, error_kw={"linewidth": 1.2, "ecolor": "#333333"})
ax.bar(x, df["NZ_current"], width, label="NZ current", color=ORANGE)
ax.bar(x + width, df["NZ_proposed"], width, label="NZ proposed", color=GREEN)

ax.set_xticks(x)
ax.set_xticklabels(df.index, rotation=20, ha="right")
ax.set_ylabel("Share of public R&D (GOV+HES), by field")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("../figures/figure3_ford_comparison.png", bbox_inches="tight")
print("Saved ../figures/figure3_ford_comparison.png")
