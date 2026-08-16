"""
Figure 2: General Advancement of Knowledge (GAK, = GUF+NOR) as a share of
government R&D budget, true SAEs vs New Zealand -- averaged over 2011-2017,
the last years New Zealand reported this split to OECD. Averaging (rather
than using 2017 alone) smooths substantial year-to-year volatility in NZ's
NOR share specifically (6.7%-24.1% across these years) and is the more
defensible comparison: on a single-year (2017) basis NZ sits below every
true SAE, but on this multi-year basis it sits just above Luxembourg, the
SAE minimum.

The SAE average is shown with a leave-one-country-out (jackknife)
uncertainty band: for each of the 12 true SAEs, recompute the average
excluding that country, then use the standard jackknife SE formula across
the 12 replicate averages. This operationalizes the "small-N caveat" this
project has flagged repeatedly as an actual visual technique, rather than
leaving it as prose -- a single country entering or leaving the sample can
move the benchmark by several percentage points (excluding Luxembourg
alone pushes the average from 60.9% to 62.9%; excluding Switzerland pulls
it to 58.2%). Individual country bars do NOT get their own error bars:
each is a direct multi-year measurement for that country alone, and
leave-one-country-out has no meaningful effect on a country's own value --
only the aggregate average is sensitive to sample composition.

Publication version: no title or source caption baked into the image --
see ../figure_captions.md for that text to use in the manuscript.

Reads:  ../data/figure2_gak_2011_2017_avg.csv
Writes: ../figures/figure2_gak_by_country.png
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from figure_style import apply_style, NAVY, GREY, ORANGE

apply_style()

df = pd.read_csv("../data/figure2_gak_2011_2017_avg.csv").set_index("entity")
df = df.sort_values("GAK_percent")

sae_vals = df.loc[df.index != "New Zealand", "GAK_percent"].values
n = len(sae_vals)
sae_avg = sae_vals.mean()

# Leave-one-country-out jackknife: recompute the average excluding each SAE
# in turn, then use the standard jackknife SE formula on those n replicates.
loo_avgs = np.array([np.mean(np.delete(sae_vals, i)) for i in range(n)])
jack_se = np.sqrt((n - 1) / n * np.sum((loo_avgs - loo_avgs.mean()) ** 2))

colors = [ORANGE if e == "New Zealand" else GREY for e in df.index]

fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.bar(df.index, df["GAK_percent"], color=colors, edgecolor="white", linewidth=0.5)

ax.axhspan(sae_avg - jack_se, sae_avg + jack_se, color=NAVY, alpha=0.12, zorder=0)
ax.axhline(sae_avg, color=NAVY, linestyle="--", linewidth=1.2)
ax.text(-0.5, sae_avg + jack_se + 1.5,
        f"SAE average = {sae_avg:.0f}% \u00b1 {jack_se:.1f}pp (leave-one-country-out SE)",
        color=NAVY, fontsize=8.5, ha="left", fontweight="bold")

ax.set_ylabel("GAK (GUF+NOR) share of GBARD (%), 2011\u20132017 average")
plt.xticks(rotation=45, ha="right")
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(0, df["GAK_percent"].max() * 1.15)
fig.tight_layout()
fig.savefig("../figures/figure2_gak_by_country.png", bbox_inches="tight")
print(f"Jackknife SE: {jack_se:.2f}pp (range across LOO replicates: {loo_avgs.min():.1f}%-{loo_avgs.max():.1f}%)")
print("Saved ../figures/figure2_gak_by_country.png")
