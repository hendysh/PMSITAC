r"""
fit_seo_ford_crosswalk.py

Empirically calibrates the SEO -> FORD crosswalk matrix used to translate
government R&D budget allocations by socio-economic objective (GBARD/SEO,
as used in the PMSITAC report) into an implied distribution of research
effort by field (FORD), and applies it to New Zealand.

This directly implements "Approach #1" from the discussion of Hendy (2026)'s
critique: instead of relying on a single hand-specified heuristic crosswalk
(Hendy's Table A1), we FIT the crosswalk on the subset of countries that
report BOTH a SEO-based series (GBARD) and a directly-reported FORD-based
series (GERD by field of R&D), then apply the fitted matrix to countries
(like New Zealand) that only report SEO data.

Why this is conceptually cleaner than the GAK* proxy trick in Hendy's note:
GERD-by-FORD data classifies research by its actual content/field regardless
of how it was funded or budgeted. This means the "General Advancement of
Knowledge" (GAK) problem -- money that never gets a SEO tag because it's
block-funded to universities or arm's-length research councils -- simply
does not arise on the FORD side. Fitting SEO -> FORD on countries where we
have BOTH series lets the GAK row of the crosswalk be estimated from data,
rather than guessed.

===============================================================================
DATA YOU NEED TO SUPPLY (this script does not download anything itself --
your sandbox/environment may not have internet access, so get these first)
===============================================================================

1. gbard_seo.tsv -- Eurostat dataset GBA_NABSFIN07 (Government budget
   allocations for R&D by NABS 2007 socio-economic objective), downloaded
   in Eurostat's "classic" bulk TSV format (this is what you get from the
   bulk download facility / the estat-navtree-portlet-prod listing, and
   is also what several `eurostat` R/Python package helpers fetch by
   default). Plain .tsv or gzip-compressed .tsv.gz both work.

   This format packs ALL dimension codes into a single first column,
   comma-separated, with the header naming them before a literal
   backslash and the time dimension, e.g.:

       freq,unit,sectperf,nabs,geo\TIME_PERIOD    2021    2022    2023
       A,MIO_EUR,GOV,08,AT                        123.4   130.1 p 135.0 e
       A,MIO_EUR,GOV,08,NZ                        :       45.2    47.8 b

   Each subsequent column is one year, and values may carry a trailing
   Eurostat status flag (e = estimated, p = provisional, b = break in
   series, etc.) separated by whitespace, or ":" for not available.
   The parser below (_parse_eurostat_bulk_tsv) handles all of this.

2. gerd_ford.tsv -- Eurostat dataset rd_e_gerdsc (GERD by sector of
   performance and fields of R&D), same bulk TSV format as above.
   You want the 'sectperf' dimension restricted to {GOV, HES} (government
   + higher education sectors) to match the "public R&D" scope Hendy used
   (his HERD+GovERD denominator), NOT total GERD (which also includes
   business R&D, BES) -- the loader filters this for you.

   NOTE: Eurostat's dimension naming is not perfectly consistent across
   bulk exports over time -- e.g. you may see 'nabs' vs 'nabs07', or the
   SEO/FORD code column named differently. If load_gbard_seo() or
   load_gerd_ford() raises a KeyError telling you the expected column
   wasn't found, open the .tsv header row, check the actual dimension
   name before the backslash, and rename that column (or edit NABS_MAP /
   FORD_MAP lookups below) to match.

3. nz_seo.csv -- New Zealand's own SEO-based allocation shares (baseline
   and/or PMSITAC-proposed). The PMSITAC report's own Figures 1-3 are read
   off bar charts, not exact published numbers, so DO NOT eyeball those --
   get the underlying MBIE budget classification by NABS/SEO if it exists,
   or substitute your best available real source. Format: two columns,
   `nabs` and `share`, one row per SEO category, shares summing to 1.
   Provide as `nz_seo_baseline.csv` and optionally `nz_seo_proposed.csv`.

4. (optional but recommended) nz_ford_actual.csv -- New Zealand's own
   ACTUAL reported FORD breakdown for government + higher-education R&D,
   from the Stats NZ Research and Development Survey. This is the real
   ground-truth check: if it exists, you don't need the crosswalk for NZ
   at all for the "current state" comparison -- you only need the fitted
   crosswalk to translate the "PMSITAC proposed" SEO reallocation into an
   implied FORD shift, since no reported FORD data can exist for a
   hypothetical future budget.

===============================================================================
NABS / FORD CATEGORY CODES USED BELOW
===============================================================================
These follow the standard NABS 2007 and FORD 2015/2007 classifications as
published by Eurostat/OECD. VERIFY these against the current Eurostat
codelist before running (I was not able to fetch the live codelist to
confirm the exact current codes in the environment this script was written
in) -- see:
  https://dd.eionet.europa.eu/vocabulary/eurostat/nabs2007/
  https://dd.eionet.europa.eu/vocabulary/eurostat/ford/
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from typing import Optional

# -----------------------------------------------------------------------------
# Category definitions
# -----------------------------------------------------------------------------

# NABS 2007 socio-economic objective codes -> friendly names.
# NB: 12 (GUF) and 13 (NOR) are combined into a single "GAK" row, matching
# Hendy's GAK* = (GUF + NOR) / GBARD definition, since most countries don't
# cleanly separate these and the PMSITAC report's own Figure 2 treats them
# as excluded/undifferentiated.
NABS_MAP = {
    "01": "Earth",
    "02": "Environment",
    "03": "Space",
    "04": "TTI",          # Transport, Telecom & Infrastructure
    "05": "Energy",
    "06": "IPT",           # Industrial Production & Technology
    "07": "Health",
    "08": "Agriculture",
    "09": "Society_Edu",   # Education (folded into "Society" bucket below)
    "10": "Society_Cul",   # Culture/media (folded into "Society" bucket)
    "11": "Society_Pol",   # Political/social systems (folded into "Society")
    "12": "GAK",           # General advancement of knowledge (GUF)
    "13": "GAK",           # General advancement of knowledge (NOR)
    "14": "Defence",
}

# Collapse the three "Society_*" sub-codes into one "Society" SEO bucket,
# matching the PMSITAC report's own category list.
SOCIETY_SUBCODES = {"Society_Edu", "Society_Cul", "Society_Pol"}

SEO_CATEGORIES = [
    "Agriculture", "Defence", "Earth", "Energy", "Environment", "Health",
    "IPT", "Society", "Space", "TTI", "GAK",
]

# FORD top-level codes -> friendly names
FORD_MAP = {
    "FORD1": "Natural_sciences",
    "FORD2": "Engineering_tech",
    "FORD3": "Medical_health",
    "FORD4": "Agricultural_sciences",
    "FORD5": "Social_sciences",
    "FORD6": "Humanities",
}
FORD_CATEGORIES = list(dict.fromkeys(FORD_MAP.values()))

# Hendy's original heuristic crosswalk (his Table A1), used here as a
# regularisation prior AND as the baseline we benchmark the fitted matrix
# against in cross-validation.
HENDY_PRIOR = pd.DataFrame(
    {
        "Natural_sciences":       [0.20, 0.30, 0.80, 0.30, 0.60, 0.15, 0.20, 0.00, 0.40, 0.10, 0.30],
        "Engineering_tech":       [0.10, 0.70, 0.20, 0.70, 0.30, 0.10, 0.70, 0.00, 0.60, 0.60, 0.20],
        "Medical_health":         [0.00, 0.00, 0.00, 0.00, 0.00, 0.75, 0.00, 0.10, 0.00, 0.00, 0.25],
        "Agricultural_sciences":  [0.70, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.05],
        "Social_sciences":        [0.00, 0.00, 0.00, 0.00, 0.10, 0.00, 0.10, 0.70, 0.00, 0.30, 0.15],
        "Humanities":             [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.20, 0.00, 0.00, 0.05],
    },
    index=SEO_CATEGORIES,
)
assert np.allclose(HENDY_PRIOR.sum(axis=1), 1.0), "Prior rows must sum to 1"


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------

def _parse_eurostat_bulk_tsv(path: str) -> pd.DataFrame:
    """
    Parse a "classic" Eurostat bulk TSV download into a tidy long
    dataframe with one row per (dimension combination, time period).

    See the module docstring above for the exact layout this expects.
    Handles plain .tsv and gzip-compressed .tsv.gz transparently (pandas
    infers compression from the file extension).

    Returns columns: [<one column per dimension found in the header>,
    "TIME_PERIOD" (int), "OBS_VALUE" (float, NaN where missing/":")].
    """
    raw = pd.read_csv(path, sep="\t", dtype=str)

    # First column header looks like "freq,unit,sectperf,nabs,geo\TIME_PERIOD"
    id_col = raw.columns[0]
    dim_names = [d.strip() for d in id_col.split("\\")[0].split(",")]

    dims = raw[id_col].str.split(",", expand=True)
    if dims.shape[1] != len(dim_names):
        raise ValueError(
            f"Header declares {len(dim_names)} dimensions {dim_names} but "
            f"data rows split into {dims.shape[1]} parts for the first "
            f"column of {path}. The file may use a different separator or "
            "have been re-exported in a non-standard way -- inspect the "
            "raw header/first data row by hand."
        )
    dims.columns = dim_names
    dims = dims.apply(lambda s: s.str.strip())

    year_cols = list(raw.columns[1:])
    values = raw[year_cols].copy()
    values.columns = [c.strip() for c in year_cols]

    wide = pd.concat([dims, values], axis=1)
    long = wide.melt(id_vars=dim_names, var_name="TIME_PERIOD", value_name="OBS_VALUE")

    # Values look like "135.0 e", "45.2", ":", "130.1 p", ": c" etc.
    # Extract the leading numeric part; anything with no number (incl. ":")
    # becomes NaN.
    numeric = long["OBS_VALUE"].astype(str).str.strip().str.extract(r"^(-?\d+\.?\d*)")
    long["OBS_VALUE"] = pd.to_numeric(numeric[0], errors="coerce")

    long["TIME_PERIOD"] = pd.to_numeric(
        long["TIME_PERIOD"].astype(str).str.strip(), errors="coerce"
    ).astype("Int64")

    return long


# Common Eurostat geo aggregates that must be excluded from the country
# panel -- these are rollups (euro area, EU totals), not individual
# countries, and including them alongside their own member states would
# double-count observations and bias the crosswalk fit.
GEO_AGGREGATES_TO_EXCLUDE = {
    "EA19", "EA20", "EA21", "EA12", "EA17", "EA18",
    "EU27_2020", "EU27_2007", "EU28", "EU25", "EU15",
    "CN_X_HK",  # China excl. Hong Kong -- not a relevant comparator here
}


def _clean_nabs_code(raw: str) -> Optional[str]:
    """
    Normalise a NABS/SEO code cell to a bare 2-digit code.

    Handles both bare codes ('01') and prefixed codes ('NABS01'), which
    Eurostat has used inconsistently across export vintages.

    Returns None (i.e. "exclude this row") for:
      - aggregate/rollup pseudo-codes (TOTAL, TOTALXNABS14)
      - third-level sub-codes such as NABS121-126, NABS131-136, which are
        finer breakdowns of the GAK categories 12 (GUF) and 13 (NOR) --
        summing these alongside the top-level 12/13 rows would double-count.
    """
    code = raw.strip().upper().replace("NABS", "")
    if code in ("TOTAL", "TOTALXNABS14", ""):
        return None
    if not code.isdigit():
        return None
    if len(code) > 2:
        return None
    return code.zfill(2)


def load_gbard_seo(path: str, year: int) -> pd.DataFrame:
    """
    Load Eurostat GBA_NABSFIN07 from a bulk TSV/TSV.GZ download and return
    a countries x SEO_CATEGORIES matrix of shares (rows sum to 1).
    """
    df = _parse_eurostat_bulk_tsv(path)
    df = df[df["TIME_PERIOD"] == year].copy()
    df = df[~df["geo"].isin(GEO_AGGREGATES_TO_EXCLUDE)]

    if "unit" in df.columns:
        # Prefer a monetary unit and compute shares ourselves, rather than
        # trusting a possibly-inconsistently-defined pre-computed % field.
        preferred_units = ["MIO_EUR", "MIO_NAC", "MIO_PPS"]
        unit = next((u for u in preferred_units if u in df["unit"].unique()), None)
        if unit is not None:
            df = df[df["unit"] == unit]

    nabs_col = "nabs" if "nabs" in df.columns else next(
        (c for c in df.columns if c.lower().startswith("nabs")), None
    )
    if nabs_col is None:
        raise KeyError(
            f"Could not find a NABS/SEO dimension column in {path}. "
            f"Columns found: {list(df.columns)}. See the module docstring "
            "note on dimension-naming inconsistencies."
        )

    df["seo"] = df[nabs_col].astype(str).apply(_clean_nabs_code).map(NABS_MAP)
    df = df.dropna(subset=["seo"])

    wide = df.pivot_table(index="geo", columns="seo", values="OBS_VALUE", aggfunc="sum")

    # Collapse Society_* sub-codes into one "Society" SEO bucket
    society_cols = [c for c in wide.columns if c in SOCIETY_SUBCODES]
    if society_cols:
        wide["Society"] = wide[society_cols].sum(axis=1, min_count=1)
        wide = wide.drop(columns=society_cols)

    wide = wide.reindex(columns=SEO_CATEGORIES)
    shares = wide.div(wide.sum(axis=1), axis=0)
    return shares.dropna(how="all")


def load_gerd_ford(path: str, year: int, allow_total_sectperf: bool = False) -> pd.DataFrame:
    """
    Load Eurostat rd_e_gerdsc from a bulk TSV/TSV.GZ download, restricted
    to government + higher-education performing sectors, and return a
    countries x FORD_CATEGORIES matrix of shares (rows sum to 1).

    If your download only contains sectperf=TOTAL (i.e. it wasn't queried
    with GOV/HES broken out individually), this function will raise by
    default, because TOTAL includes business-sector R&D (BES), which is
    usually the majority of GERD in advanced economies -- silently using
    it would compare NZ's PUBLIC budget allocations against SAE peers'
    TOTAL (public + private) research effort, which is not a like-for-like
    comparison. Pass allow_total_sectperf=True to proceed anyway with a
    clearly-flagged caveat, e.g. for a preliminary run while you re-pull
    the properly disaggregated file.
    """
    df = _parse_eurostat_bulk_tsv(path)
    df = df[df["TIME_PERIOD"] == year].copy()
    df = df[~df["geo"].isin(GEO_AGGREGATES_TO_EXCLUDE)]

    sectperf_col = "sectperf" if "sectperf" in df.columns else next(
        (c for c in df.columns if "sectperf" in c.lower()), None
    )
    if sectperf_col is None:
        raise KeyError(
            f"Could not find a 'sectperf' dimension column in {path}. "
            f"Columns found: {list(df.columns)}."
        )

    available_sectors = set(df[sectperf_col].unique())
    if {"GOV", "HES"} & available_sectors:
        df = df[df[sectperf_col].isin(["GOV", "HES"])]
    elif allow_total_sectperf and "TOTAL" in available_sectors:
        print(
            "WARNING: gerd_ford data has no GOV/HES breakdown, only "
            "sectperf=TOTAL. Proceeding with TOTAL GERD (which includes "
            "business R&D) because allow_total_sectperf=True was set. "
            "This means the fitted crosswalk compares NZ's PUBLIC budget "
            "shares against SAE peers' TOTAL (public + private) research "
            "effort by field -- not a clean like-for-like comparison. "
            "Re-pull rd_e_gerdsc with sectperf split into individual "
            "sectors (GOV, HES, BES, PNP_NPISH) for a proper fit."
        )
        df = df[df[sectperf_col] == "TOTAL"]
    else:
        raise ValueError(
            f"{path} only contains sectperf values {sorted(available_sectors)} "
            "-- no GOV or HES breakdown available, so public-sector R&D "
            "by field can't be isolated. Re-download rd_e_gerdsc selecting "
            "sectperf codes GOV and HES individually (not just TOTAL), "
            "or call load_gerd_ford(..., allow_total_sectperf=True) to "
            "proceed anyway using total GERD as an approximation (see "
            "docstring for why that's a weaker comparison)."
        )

    if "unit" in df.columns:
        preferred_units = ["MIO_EUR", "MIO_NAC", "MIO_PPS"]
        unit = next((u for u in preferred_units if u in df["unit"].unique()), None)
        if unit is not None:
            df = df[df["unit"] == unit]

    ford_col = "ford" if "ford" in df.columns else next(
        (c for c in df.columns if c.lower().startswith("ford")), None
    )
    if ford_col is None:
        raise KeyError(
            f"Could not find a FORD dimension column in {path}. "
            f"Columns found: {list(df.columns)}."
        )
    df["ford"] = df[ford_col].astype(str).map(FORD_MAP)
    df = df.dropna(subset=["ford"])

    # Sum GOV + HES (or TOTAL, in the fallback case) together per country/field
    grouped = df.groupby(["geo", "ford"])["OBS_VALUE"].sum().reset_index()
    wide = grouped.pivot(index="geo", columns="ford", values="OBS_VALUE")
    wide = wide.reindex(columns=FORD_CATEGORIES)
    shares = wide.div(wide.sum(axis=1), axis=0)
    return shares.dropna(how="all")


def load_nz_seo(path: str) -> pd.Series:
    """Load a two-column (nabs_category_name, share) CSV for New Zealand."""
    df = pd.read_csv(path)
    s = df.set_index(df.columns[0])[df.columns[1]]
    s = s.reindex(SEO_CATEGORIES).fillna(0.0)
    s = s / s.sum()
    return s


# -----------------------------------------------------------------------------
# Crosswalk fitting
# -----------------------------------------------------------------------------

def fit_crosswalk(S: pd.DataFrame, F: pd.DataFrame, prior: pd.DataFrame,
                   ridge_lambda: float = 0.5) -> pd.DataFrame:
    """
    Fit W (SEO x FORD) minimising ||F - S @ W||^2 + ridge_lambda * ||W - prior||^2
    subject to each row of W summing to 1 and W >= 0.

    S: countries x SEO shares (only rows/countries with matching F used)
    F: countries x FORD shares
    prior: SEO x FORD heuristic matrix used for shrinkage (keeps the fit
        well-behaved given the panel is small relative to the number of
        free parameters -- 11 x 6 = 66 -- and pulls back toward the
        heuristic where data is uninformative).
    """
    common = S.index.intersection(F.index)
    if len(common) < 4:
        raise ValueError(
            f"Only {len(common)} countries have both SEO and FORD data "
            "after alignment -- too few to fit a 66-parameter matrix "
            "reliably. Check country-code matching between the two files."
        )
    S_arr = S.loc[common].fillna(0.0).values
    F_arr = F.loc[common].fillna(0.0).values
    W0 = prior.values

    n_seo, n_ford = W0.shape

    def unpack(x):
        return x.reshape(n_seo, n_ford)

    def objective(x):
        W = unpack(x)
        resid = F_arr - S_arr @ W
        data_term = np.sum(resid ** 2)
        prior_term = ridge_lambda * np.sum((W - W0) ** 2)
        return data_term + prior_term

    constraints = [
        {"type": "eq", "fun": (lambda x, i=i: unpack(x)[i].sum() - 1.0)}
        for i in range(n_seo)
    ]
    bounds = [(0.0, 1.0)] * (n_seo * n_ford)

    result = minimize(
        objective, W0.flatten(), method="SLSQP",
        bounds=bounds, constraints=constraints,
        options={"maxiter": 500, "ftol": 1e-10},
    )
    if not result.success:
        print(f"WARNING: optimiser did not fully converge: {result.message}")

    W_fit = pd.DataFrame(unpack(result.x), index=prior.index, columns=prior.columns)
    print(f"Fitted crosswalk on {len(common)} countries: {list(common)}")
    return W_fit


def cross_validate(S: pd.DataFrame, F: pd.DataFrame, prior: pd.DataFrame,
                    ridge_lambda: float = 0.5) -> pd.DataFrame:
    """
    Leave-one-country-out CV. For each held-out country, refit W on the
    rest, predict its FORD shares from its SEO shares, and compare the
    error against simply using the static heuristic prior with no fitting
    at all. This tells you whether fitting is actually earning its keep
    out-of-sample, or just overfitting a small panel.
    """
    common = S.index.intersection(F.index)
    rows = []
    for held_out in common:
        train_idx = [c for c in common if c != held_out]
        W_cv = fit_crosswalk(S.loc[train_idx], F.loc[train_idx], prior, ridge_lambda)

        s_i = S.loc[held_out].fillna(0.0).values
        f_true = F.loc[held_out].fillna(0.0).values

        f_pred_fitted = s_i @ W_cv.values
        f_pred_prior = s_i @ prior.values

        mae_fitted = np.mean(np.abs(f_true - f_pred_fitted))
        mae_prior = np.mean(np.abs(f_true - f_pred_prior))
        rows.append({"country": held_out, "mae_fitted": mae_fitted, "mae_heuristic": mae_prior})

    cv_df = pd.DataFrame(rows).set_index("country")
    print("\nLeave-one-country-out cross-validation (mean absolute error in FORD shares):")
    print(cv_df.round(4))
    print(f"\nMean across countries -- fitted: {cv_df['mae_fitted'].mean():.4f}, "
          f"static heuristic: {cv_df['mae_heuristic'].mean():.4f}")
    if cv_df["mae_fitted"].mean() >= cv_df["mae_heuristic"].mean():
        print("NOTE: the fitted crosswalk does NOT outperform the static heuristic "
              "out-of-sample. This would suggest the panel is too small/noisy to "
              "improve on Hendy's hand-specified matrix, and the heuristic should "
              "be preferred (or ridge_lambda increased further) rather than the fit.")
    return cv_df


# -----------------------------------------------------------------------------
# Main pipeline
# -----------------------------------------------------------------------------

def main():
    YEAR = 2023  # match the PMSITAC report's SAE reference year where possible

    print("Loading Eurostat GBARD-by-SEO data...")
    # Accepts .tsv or .tsv.gz -- adjust the filename/extension to match
    # whatever you actually downloaded.
    S = load_gbard_seo("gbard_seo.tsv", year=YEAR)

    print("Loading Eurostat GERD-by-FORD data (GOV+HES)...")
    F = load_gerd_ford("gerd_ford.tsv", year=YEAR)

    print("\n--- Cross-validating: does fitting beat the static heuristic? ---")
    cross_validate(S, F, HENDY_PRIOR, ridge_lambda=0.5)

    print("\n--- Fitting final crosswalk on full panel ---")
    W_fit = fit_crosswalk(S, F, HENDY_PRIOR, ridge_lambda=0.5)
    print("\nFitted crosswalk matrix:")
    print(W_fit.round(2))
    W_fit.to_csv("fitted_crosswalk.csv")

    print("\nComparison to Hendy's original heuristic matrix (fitted - prior):")
    print((W_fit - HENDY_PRIOR).round(2))

    # Apply to New Zealand
    print("\nLoading New Zealand SEO shares...")
    nz_baseline = load_nz_seo("nz_seo_baseline.csv")
    try:
        nz_proposed = load_nz_seo("nz_seo_proposed.csv")
    except FileNotFoundError:
        nz_proposed = None
        print("No nz_seo_proposed.csv found -- skipping the 'proposed' comparison.")

    # IMPORTANT: the "SAE average" benchmark must be restricted to actual
    # Small Advanced Economies (population < 20m, per-capita income >
    # US$30k -- the definition PMSITAC's own report and Hendy's critique
    # both use), NOT the full panel of countries used to fit the
    # crosswalk. The fitting panel deliberately includes larger/lower-
    # income countries because more data improves the crosswalk estimate;
    # but averaging SEO shares over that same panel to build the "SAE
    # average" comparison silently pulls in Germany, France, Turkey, the
    # US, Japan, etc., which have no business being called SAEs.
    TRUE_SAES = ["AT", "BE", "CH", "CY", "DK", "EE", "FI", "IE", "IS",
                 "LT", "LU", "MT", "NL", "SE"]  # matches PMSITAC's own SAE
                                                  # list minus AU/IL, which
                                                  # Eurostat doesn't report
    sae_countries = [c for c in TRUE_SAES if c in S.index]
    missing_saes = [c for c in TRUE_SAES if c not in S.index]
    if missing_saes:
        print(f"NOTE: {missing_saes} are in the true-SAE list but not in "
              "this GBARD file, so they're excluded from the average.")
    sae_avg = S.loc[sae_countries].mean(axis=0)

    results = pd.DataFrame({
        "SAE_avg_(SEO->FORD)": sae_avg @ W_fit,
        "NZ_baseline_(SEO->FORD)": nz_baseline @ W_fit,
    })
    if nz_proposed is not None:
        results["NZ_proposed_(SEO->FORD)"] = nz_proposed @ W_fit

    try:
        nz_ford_actual = pd.read_csv("nz_ford_actual.csv").set_index(
            pd.read_csv("nz_ford_actual.csv").columns[0]
        ).iloc[:, 0]
        nz_ford_actual = nz_ford_actual.reindex(FORD_CATEGORIES)
        results["NZ_actual_reported_FORD"] = nz_ford_actual
        print("\nFound nz_ford_actual.csv -- this is real ground truth, not a "
              "crosswalk estimate. Compare it to 'NZ_baseline_(SEO->FORD)' as "
              "the ultimate check on how much error the crosswalk step itself "
              "introduces for New Zealand specifically.")
    except FileNotFoundError:
        print("\nNo nz_ford_actual.csv found. If Stats NZ's R&D Survey publishes "
              "a FORD breakdown for the government + higher-education sectors, "
              "add it here -- it lets you skip the crosswalk step entirely for "
              "the 'current state' comparison.")

    print("\n=== Final comparison table (shares by field) ===")
    print(results.round(3))
    results.to_csv("nz_vs_sae_ford_comparison.csv")

    # Plot, mirroring Hendy's Figure 5 style
    ax = results.plot(kind="bar", figsize=(10, 5))
    ax.set_ylabel("Share of public R&D (GOV+HES)")
    ax.set_title("NZ vs SAE research priorities by field, empirically-fitted crosswalk")
    plt.tight_layout()
    plt.savefig("nz_vs_sae_ford_comparison.png", dpi=150)
    print("\nSaved: fitted_crosswalk.csv, nz_vs_sae_ford_comparison.csv, "
          "nz_vs_sae_ford_comparison.png")


if __name__ == "__main__":
    main()
