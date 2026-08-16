# Reproducible figures: reanalysis of PMSITAC (2026)

**This is a stripped-down package supporting only Figures 1, 2, 3, and A1**
(the crosswalk heatmap) from a larger reanalysis of New Zealand's public
R&D funding priorities against genuine Small Advanced Economy (SAE)
peers, correcting the PMSITAC prioritisation report's GBARD/GAK benchmarking. 

**Publication-ready**: figure images have no titles or source captions
baked in (journals typeset captions separately) -- that text lives in
`figure_captions.md` instead, ready to paste into a manuscript's figure
caption list.

## Structure

```
paper/
├── figure_captions.md                     title + full caption text for each figure, for the manuscript
├── code/                                  scripts, as .py
│   ├── figure_style.py                    shared plotting style, imported by all figure scripts
│   ├── figure1_gbard_by_seo_stacked.py    Figure 1
│   ├── figure2_gak_by_country.py          Figure 2
│   ├── figure3_ford_comparison.py         Figure 3
│   ├── figureA1_crosswalk_heatmap.py      Figure A1
│   ├── 00_prepare_data.py                 regenerates all data/*.csv from raw sources (Methods step, not a figure script)
│   └── fit_seo_ford_crosswalk.py          crosswalk-fitting module used by 00_prepare_data.py
├── notebooks/                             identical figures, as .ipynb
│   ├── figure_style.py                    same shared style module, copied here so notebooks are standalone
│   ├── fit_seo_ford_crosswalk.py          same crosswalk module (not used by the figure notebooks themselves)
│   ├── figure1_gbard_by_seo_stacked.ipynb
│   ├── figure2_gak_by_country.ipynb
│   ├── figure3_ford_comparison.ipynb
│   ├── figureA1_crosswalk_heatmap.ipynb
│   ├── _nb_builder.py                     utility used to construct the .ipynb JSON (no nbformat dependency)
│   └── _generate_notebooks.py             parses each code/figureN_*.py script directly into a matching notebook
├── data/
│   ├── figure1_gbard_by_seo_stacked.csv
│   ├── figure2_gak_2011_2017_avg.csv
│   ├── figure3_ford_comparison.csv
│   └── crosswalk_matrix.csv               the fitted 11x6 SEO->FORD matrix; also Figure A1's data
└── figures/                               PNG outputs (300dpi), written by either code/ or notebooks/
```

Each `figureN_*` script/notebook is self-contained: it reads only its own
small CSV from `../data/` and writes a PNG to `../figures/`. None of them
need the raw Eurostat/OECD source files, and none call
`fit_seo_ford_crosswalk.py` directly.

Run the scripts from inside `code/`:

```bash
cd code
python3 figure1_gbard_by_seo_stacked.py
python3 figure2_gak_by_country.py
python3 figure3_ford_comparison.py
python3 figureA1_crosswalk_heatmap.py
```

Or open any notebook in `notebooks/` directly in Jupyter/JupyterLab/VS
Code -- each has the same logic split into cells (imports/style → load
data → build & save plot), with a markdown cell up top explaining the
figure and its sources.

## Figure summaries

**Figure 1** — GBARD by socio-economic objective (SEO), stacked 100% bars,
all 14 true SAEs individually plus the SAE average and New Zealand (bold),
with GAK incorporated for NZ using its own real OECD-reported GUF+NOR
figure, averaged 2011-2017 (40.9%) to smooth substantial year-to-year
volatility. NZ remains below the SAE average, though close to the SAE
minimum (see Figure 2).

**Figure 2** — GAK (= GUF + NOR) by country, averaged over 2011-2017 — the
last years New Zealand reported this split to OECD, and the multi-year
average is used rather than 2017 alone because NZ's NOR share swung
6.7%-24.1% year to year across that window. Uses real reported NZ data
throughout, not a proxy. On a single-year (2017) basis NZ sat below every
true SAE; on this multi-year basis NZ (40.9%) sits just above Luxembourg
(38.2%), the SAE minimum -- a materially different conclusion, and the
reason the multi-year average is used as the headline figure rather than
the single-year snapshot. The SAE average is shown with a leave-one-
country-out (jackknife) uncertainty band (60.9% ± 4.4pp) rather than as a
bare point estimate -- excluding Luxembourg or Switzerland alone shifts
it by several percentage points, and NZ falls within the band rather than
clearly outside it.

**Figure 3** — NZ vs SAE research priorities translated into field-of-
research (FORD) terms, using a SEO→FORD crosswalk matrix *fitted*
empirically on a 32-country panel (not hand-specified, unlike Hendy's
original heuristic matrix) and cross-validated leave-one-country-out.
SAE average bars carry a separate leave-one-country-out (jackknife) error
bar on benchmark composition (a different question from the crosswalk's
own cross-validation) -- the agriculture and social sciences/humanities
gaps dwarf their error bands, while NZ's current Engineering & Technology
share falls inside the SAE uncertainty band rather than just being
numerically close to it.

**Figure A1** — The fitted SEO→FORD crosswalk matrix itself, as an
annotated heatmap (rows sum to 1). This is the matrix Figure 3 uses to
translate NZ and SAE SEO shares into FORD shares -- showing it directly
lets a reader inspect the fit's structure, e.g. the near-diagonal pattern
(Health→Medical & health 0.75, Agriculture→Agricultural sciences 0.69,
Society→Social sciences 0.68) as a basic sanity check that the fit found
sensible mappings rather than an uninterpretable result.

## Raw source files (needed only for 00_prepare_data.py, not for the figure scripts)

- `gbard_seo.tsv` — Eurostat GBA_NABSFIN07 bulk export (Government budget
  allocations for R&D by NABS 2007 socio-economic objective)
- `gerd_ford.tsv` — Eurostat rd_e_gerdsc bulk export (GERD by sector of
  performance and field of R&D)
- `nz_seo_baseline.csv` / `nz_seo_proposed.csv` — NZ's current and
  PMSITAC-proposed SEO shares, from MBIE's own budget classification
- `MSTI_March2026.xlsx` — OECD Main Science and Technology Indicators,
  March 2026 edition

(Stats NZ's R&D Survey workbook, needed elsewhere in the fuller analysis,
is not required for any of these four figures.)

## Key methodological notes

- **True SAE definition**: population <20m, per-capita income >US$30k,
  matching PMSITAC's own 16-country list. 14 of 16 are used throughout
  (Australia and Israel excluded — neither reports the required breakdowns
  to Eurostat or OECD on a like-for-like basis).
- **Crosswalk fitting**: SEO→FORD translation matrix estimated by
  constrained least squares (rows non-negative, sum to 1) with L2
  shrinkage toward an initial guess, fit on a 32-country
  panel, validated leave-one-country-out.
- **GAK for New Zealand**: MBIE's own budget classification reports 0% to
  GAK, but this reflects the scope of that specific $839m dataset, not a
  genuine absence of untargeted research funding. Figures 1 and 2 instead
  use NZ's own OECD-reported GUF+NOR figure, averaged over 2011-2017
  (40.9%) rather than the single most recent year (2017 alone: 34.4%),
  since NZ's NOR share specifically swung 6.7%-24.1% year to year across
  that window. Note that GAK is GUF+NOR summed for every entity in this
  analysis, not directly reported by anyone -- for the true SAEs it's
  sourced from Eurostat, for NZ from OECD MSTI (Eurostat doesn't cover NZ
  at all).
- **Leave-one-country-out error bars** (Figures 2 and 3): a jackknife
  standard error on the SAE average/benchmark only, testing sensitivity
  to which countries happen to be in the 12-14 country sample. This is
  distinct from the crosswalk's own leave-one-country-out cross-validation
  (Figure 3's caption, MAE 0.047 vs 0.055), which tests the fitted
  matrix's predictive accuracy, not benchmark composition. Individual
  country bars never carry error bars, since a country's own directly-
  measured value doesn't change based on which other countries are
  included in the sample.
