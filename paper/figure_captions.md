# Figure captions

Titles and source/methodology notes have been removed from the figure
images themselves for publication (journals typeset captions separately).
This file holds that text so it isn't lost -- paste the relevant entry
into the manuscript's figure caption list.

---

## Figure 1

**Title:** Government budget allocations for R&D (GBARD) by socio-economic
objective, true SAEs vs New Zealand (2023)

**Caption:** Source: Eurostat GBA_NABSFIN07 (2023); NZ from MBIE budget
classification. SAE = population <20m, per-capita income >US$30k (14 of
PMSITAC's 16 SAEs; Australia and Israel excluded, see Methods). GAK is
GUF+NOR summed throughout (not directly reported by anyone); for the SAEs
this is 2023 Eurostat data, for New Zealand it is OECD MSTI data averaged
2011-2017 (NZ's only years available), applied to the current (2023) SEO
composition of NZ's other categories. This mixes data vintages within the
NZ bar and compares a multi-year NZ figure against single-year SAE
figures; see Figure 2 for the properly year-matched multi-year comparison
on both sides.

---

## Figure 2

**Title:** General Advancement of Knowledge, 2011–2017 average: true SAEs
vs New Zealand (real OECD-reported data, both sides)

**Caption:** Source: OECD MSTI, series C_GUFXCV/C_NORXCV/C_CVXTT, averaged
over 2011-2017 (the last years New Zealand reported this split;
Switzerland has only 4 years, 2014-2017 -- see data file's n_years
column). Averaging smooths substantial year-to-year volatility (NZ's NOR
alone ranged 6.7%-24.1% across these years). On a single-year (2017)
basis NZ (34.4%) sat below every SAE including Luxembourg (41.2%); on
this multi-year basis NZ (40.9%) sits just above Luxembourg (38.2%),
though still well below the SAE average. The shaded band around the SAE
average line shows a leave-one-country-out (jackknife) standard error
(60.9% ± 4.4pp): excluding Luxembourg alone shifts the average to 62.9%;
excluding Switzerland shifts it to 58.2%. NZ falls within this band, not
confidently above or below it -- a single country entering or leaving the
comparator group moves the benchmark by several percentage points, which
is the point of showing it rather than a bare point estimate. Individual
country bars do not carry their own error bars, since leave-one-country-out
has no meaningful effect on a country's own directly-measured value --
only the aggregate average is sensitive to sample composition.

---

## Figure 3

**Title:** NZ vs SAE research priorities by field (empirically-fitted
SEO→FORD crosswalk, true 14-SAE benchmark)

**Caption:** Source: Eurostat GBA_NABSFIN07 + rd_e_gerdsc (2023,
32-country fitting panel, 14-country SAE benchmark). Crosswalk fitted by
constrained least squares with ridge shrinkage toward Hendy (2026)'s
heuristic matrix, cross-validated leave-one-country-out (MAE 0.047 vs
0.055 for the static heuristic). SAE average bars carry a separate
leave-one-country-out (jackknife) error bar, testing sensitivity of the
SAE benchmark to which of the 14 true SAEs happen to be in the sample
(distinct from the crosswalk's own cross-validation above, which tests
the fitted matrix's out-of-sample accuracy, not benchmark composition).
NZ current/proposed bars carry no error bars, since excluding an SAE from
the benchmark doesn't affect NZ's own SEO shares. The agriculture and
social sciences/humanities gaps are many times larger than their
corresponding SAE uncertainty bands; Engineering & Technology's NZ-current
value (0.209) falls inside the SAE band (0.216 ± 0.014), a more careful
statement of the "near parity" finding than the bare point estimate.

---

## Figure A1

**Title:** Fitted SEO→FORD crosswalk matrix (rows sum to 1; constrained
least squares, 32-country panel)

**Caption:** Source: fitted on Eurostat GBA_NABSFIN07 + rd_e_gerdsc (2023,
32-country panel) by constrained least squares with ridge shrinkage
toward Hendy (2026)'s heuristic matrix, cross-validated leave-one-
country-out (MAE 0.047 vs 0.055 for the static heuristic). Used to
translate NZ and SAE SEO shares into FORD shares in Figure 3.
