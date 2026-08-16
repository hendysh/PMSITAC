# New Zealand vs Small Advanced Economy Research Priorities

A reanalysis of New Zealand's public R&D funding priorities against
genuine Small Advanced Economy (SAE) peers, correcting the PMSITAC (2026) 
prioritisation report's benchmarking methodology.

**This repository is a stripped-down package supporting only Figures 1,
2, 3, and A1** of the manuscript. It covers the core benchmarking
findings (GAK, and the SEO→FORD field-of-research comparison); it does
not include additional validation checks.

## Manuscript

[Impact of Refocusing](paper/Impact%20of%20Refocusing%20FINAL.pdf) 

Figure numbers in this repository (`Figure 1`, `Figure 2`, `Figure 3`, 
`Figure A1`) match the manuscript's own numbering directly.

## Reproducible code, data, and figures

All four figures can be regenerated from raw source data — see
[`paper/README.md`](paper/README.md) for the full structure, methodology
notes, and instructions to run everything, either as `.py` scripts or
`.ipynb` notebooks. Figure titles and source captions are kept separate
from the images themselves (see
[`paper/figure_captions.md`](paper/figure_captions.md)) for direct use in
the manuscript's figure caption list.

```
paper/
├── code/           reproducible scripts (.py)
├── notebooks/      the same figures as Jupyter notebooks (.ipynb)
├── data/           the exact data each figure plots
├── figures/        rendered PNG outputs
├── figure_captions.md
└── README.md       full documentation
```

## Figure summaries

- **Figure 1** — GBARD by socio-economic objective, true SAEs vs New
  Zealand, with GAK incorporated for NZ from its own real OECD-reported
  GUF+NOR figure (2011–2017 average).
- **Figure 2** — GAK (= GUF + NOR) by country, 2011–2017 average, with a
  leave-one-country-out (jackknife) uncertainty band on the SAE average
  (60.9% ± 4.4pp). NZ sits just above Luxembourg, the SAE minimum, and
  within the uncertainty band around the average.
- **Figure 3** — NZ vs SAE research priorities by field (FORD), using an
  empirically-fitted SEO→FORD crosswalk. SAE average bars carry their own
  leave-one-country-out error bars; the agriculture and social
  sciences/humanities gaps dwarf theirs, while NZ's current Engineering &
  Technology share falls inside the SAE uncertainty band.
- **Figure A1** — The fitted SEO→FORD crosswalk matrix itself, as an
  annotated heatmap, letting a reader inspect the fit's structure
  directly (Appendix figure).

## Key findings covered by these four figures

- **Agriculture overweighting** in NZ's public R&D spend is robust.
- **Social sciences and humanities are the most consistently underweighted
  fields.**
- The evidentiary case for the **Technology for Prosperity funding
  increase** does not hold up once benchmarked against a corrected
  comparator group; NZ was already near parity.
- New Zealand's **government R&D budget is genuinely more centralised**
  than peer SAEs, though within a leave-one-country-out uncertainty band
  rather than a precise point estimate.

See the manuscript for full discussion, and `paper/README.md` for the
complete methodology, including how the leave-one-country-out error bars
in Figures 2 and 3 were constructed.

## License

Code and derived data/figures in this repository are released under the
[MIT License](LICENSE). The underlying source data (Eurostat, OECD MSTI)
carries its own separate reuse and attribution terms and is not owned by
this repository.

## Citation

See [`CITATION.cff`](CITATION.cff), or use GitHub's "Cite this repository"
button once this is pushed.
