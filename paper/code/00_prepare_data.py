"""
00_prepare_data.py

Documents and reproduces how every CSV in ../data/ was derived from the raw
source files. This is a Methods-section script, not a figure script: the
figureN_*.py scripts each only need their own small CSV and do not call
this. Run this only if you need to regenerate the data CSVs from scratch
(e.g. after re-pulling updated source data).

This is the STRIPPED-DOWN version of this script, supporting only Figures
1, 2, 3, and A1 (the crosswalk heatmap). The full analysis covers
additional cross-checks and comparisons not included here.

Raw inputs required (not included in this package -- see paper Methods for
exact download instructions):
  - gbard_seo.tsv         Eurostat GBA_NABSFIN07, bulk TSV export
  - gerd_ford.tsv          Eurostat rd_e_gerdsc, bulk TSV export
  - nz_seo_baseline.csv    NZ current SEO shares, from MBIE budget classification
  - nz_seo_proposed.csv    NZ PMSITAC-proposed SEO shares, from MBIE budget classification
  - MSTI_March2026.xlsx    OECD Main Science and Technology Indicators, March 2026 edition

This script assumes those five files sit alongside fit_seo_ford_crosswalk.py
(the crosswalk-fitting module) in the working directory it's run from --
adjust paths as needed for your environment.
"""

import sys
import numpy as np
import openpyxl
import pandas as pd

sys.path.insert(0, ".")  # adjust to wherever fit_seo_ford_crosswalk.py lives
from fit_seo_ford_crosswalk import (
    load_gbard_seo, load_gerd_ford, fit_crosswalk, load_nz_seo,
    HENDY_PRIOR, SEO_CATEGORIES,
)

TRUE_SAES = ["AT", "BE", "CH", "CY", "DK", "EE", "FI", "IE", "IS", "LT", "LU", "MT", "NL", "SE"]
COUNTRY_NAMES = {"AT": "Austria", "BE": "Belgium", "CH": "Switzerland", "CY": "Cyprus",
                 "DK": "Denmark", "EE": "Estonia", "FI": "Finland", "IE": "Ireland",
                 "IS": "Iceland", "LT": "Lithuania", "LU": "Luxembourg", "MT": "Malta",
                 "NL": "Netherlands", "SE": "Sweden"}
YEAR = 2023

# --- Load raw sources -----------------------------------------------------
S = load_gbard_seo("gbard_seo.tsv", year=YEAR)
F = load_gerd_ford("gerd_ford.tsv", year=YEAR)
nz_baseline = load_nz_seo("nz_seo_baseline.csv")
nz_proposed = load_nz_seo("nz_seo_proposed.csv")
sae_avg_seo = S.loc[TRUE_SAES].mean(axis=0)

wb = openpyxl.load_workbook("MSTI_March2026.xlsx", read_only=True, data_only=True)


def get_mstiseries(sheet, country):
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    years = [(i, int(v)) for i, v in enumerate(rows[2]) if isinstance(v, (int, str)) and str(v).isdigit()]
    for r in rows[3:]:
        if r[0] == country:
            return {yr: r[idx] for idx, yr in years if idx < len(r) and r[idx] not in (None, "", "..")}
    return {}


# --- Figure 1: GBARD by SEO, stacked, true SAEs + SAE avg + NZ ------------
fig1 = pd.DataFrame(index=[COUNTRY_NAMES[c] for c in TRUE_SAES] + ["SAE average", "New Zealand"],
                     columns=SEO_CATEGORIES, dtype=float)
for c in TRUE_SAES:
    fig1.loc[COUNTRY_NAMES[c]] = S.loc[c, SEO_CATEGORIES].values
fig1.loc["SAE average"] = sae_avg_seo[SEO_CATEGORIES].values

# --- Figure 2 data + Figure 1's GAK*-adjusted NZ row ------------------------
# GAK is not a directly-reported quantity for ANYONE in this analysis -- it
# is always GUF+NOR summed (see NABS_MAP in fit_seo_ford_crosswalk.py, where
# NABS12 and NABS13 both map to "GAK"). For the true SAEs this sum comes
# from Eurostat; New Zealand doesn't report to Eurostat at all, so its
# GUF+NOR sum instead comes from OECD MSTI, which only has this NZ split
# through 2017. A single-year (2017) comparison is noisy -- NZ's NOR share
# alone ranged 6.7%-24.1% across 2011-2017 -- so both Figure 2 and Figure
# 1's GAK*-adjusted NZ row use the 2011-2017 average instead, computed
# identically for NZ and every true SAE from the same OECD MSTI series.
# NOTE: this means Figure 1's "New Zealand" bar mixes a 2011-2017 OECD
# MSTI-derived GAK figure with 2023 MBIE-derived figures for every other
# category in that same bar, and compares against SAE bars whose GAK
# component is single-year 2023 Eurostat data -- Figure 2 is the properly
# year-matched comparison; Figure 1 trades that precision for showing the
# full SEO breakdown in one chart.
TRUE_SAE_NAMES = ["Austria", "Belgium", "Switzerland", "Denmark", "Estonia", "Finland",
                   "Ireland", "Iceland", "Lithuania", "Luxembourg", "Netherlands", "Sweden"]
rows = []
for c in TRUE_SAE_NAMES + ["New Zealand"]:
    guf_s = get_mstiseries("C_GUFXCV", c)
    nor_s = get_mstiseries("C_NORXCV", c)
    cv_s = get_mstiseries("C_CVXTT", c)
    guf_vals = [guf_s[y] for y in range(2011, 2018) if y in guf_s]
    nor_vals = [nor_s[y] for y in range(2011, 2018) if y in nor_s]
    cv_vals = [cv_s[y] for y in range(2011, 2018) if y in cv_s]
    guf_avg = sum(guf_vals) / len(guf_vals)
    nor_avg = sum(nor_vals) / len(nor_vals)
    cv_avg = sum(cv_vals) / len(cv_vals) if cv_vals else 100
    rows.append({"entity": c, "GAK_percent": (guf_avg + nor_avg) * cv_avg / 100, "n_years": len(guf_vals)})
fig2 = pd.DataFrame(rows).sort_values("GAK_percent")
fig2.to_csv("../data/figure2_gak_2011_2017_avg.csv", index=False)

nz_gak_avg = fig2.loc[fig2["entity"] == "New Zealand", "GAK_percent"].iloc[0] / 100
nz_with_gak = nz_baseline * (1 - nz_gak_avg)
nz_with_gak["GAK"] = nz_gak_avg
fig1.loc["New Zealand"] = nz_with_gak[SEO_CATEGORIES].values

fig1.index.name = "entity"
fig1.to_csv("../data/figure1_gbard_by_seo_stacked.csv")

# --- Crosswalk matrix + Figure 3: FORD comparison ---------------------------
W_fit = fit_crosswalk(S, F, HENDY_PRIOR, ridge_lambda=0.5)
W_fit.to_csv("../data/crosswalk_matrix.csv")  # also Figure A1's data (heatmap of this matrix)

fig3 = pd.DataFrame({
    "SAE_average": sae_avg_seo[SEO_CATEGORIES] @ W_fit,
    "NZ_current": nz_baseline[SEO_CATEGORIES] @ W_fit,
    "NZ_proposed": nz_proposed[SEO_CATEGORIES] @ W_fit,
})

# Leave-one-country-out (jackknife) SE on the SAE average only: recompute
# the SAE SEO average excluding each true SAE in turn, then push through
# the SAME already-fitted crosswalk (only the benchmark composition
# varies here, not the crosswalk fit itself -- that would be a different,
# separate question about the fit's own sensitivity, not covered by this
# stripped-down package, which doesn't include the full analysis's
# separate crosswalk cross-validation figure). NZ current/proposed don't
# get error bars: each is a single country's own SEO shares through the
# same fixed crosswalk, so leaving out an SAE country doesn't affect NZ's
# own value.
sae_seo_full = S.loc[TRUE_SAES, SEO_CATEGORIES]
n_sae = len(sae_seo_full)
loo_ford = np.array([
    (sae_seo_full.drop(index=c).mean(axis=0) @ W_fit).values for c in sae_seo_full.index
])
fig3["SAE_average_jackknife_SE"] = np.sqrt(
    (n_sae - 1) / n_sae * np.sum((loo_ford - loo_ford.mean(axis=0)) ** 2, axis=0)
)

fig3.index.name = "ford_category"
fig3.to_csv("../data/figure3_ford_comparison.csv")

print("All data CSVs regenerated in ../data/ (Figures 1, 2, 3, A1 only -- "
      "stripped-down package)")
