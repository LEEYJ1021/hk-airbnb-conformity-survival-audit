# Convergence Without Divergence: Asymmetric Effects of Representational Fit on Platform Listing Survival

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data: Inside Airbnb](https://img.shields.io/badge/Data-Inside%20Airbnb-orange.svg)](http://insideairbnb.com/)
[![Status: re-audited](https://img.shields.io/badge/status-independently%20re--audited-critical.svg)](#)

> **This repository is a full re-audit of a prior analysis, not a restatement of it.**
> It starts from the same two raw data files (`data/IV_panel.csv`, `data/dataset_0322.xlsx`)
> that circulated with an earlier manuscript, diagnoses a data-quality defect in them,
> repairs it, and re-estimates every hypothesis from scratch. Several headline results
> from the earlier manuscript **do not survive** this re-audit. This README reports
> what was found, not what was hoped for.

---

## This repository vs. the manuscript

This repository documents the **full audit**: all three original hypotheses (H1, H2,
H3) plus the SAR spatial model, including the parts that turned out not to be
estimable on the released data. The manuscript currently being prepared for
submission, *"Convergence Without Divergence"*, reports only the **temporal**
slice of this audit — H1 and H2 — because those are the two hypotheses that survive
the district-repair audit cleanly enough to support a clean, single-mechanism paper.

Concretely:

- **H1 and H2** below correspond directly to the manuscript's Sections 5–6
  (Tables 3–5, Figures 2–5 in the manuscript map onto `fig2`–`fig5` here).
- **H3 and the SAR model** are *not* in the manuscript. They are kept in this
  repository, unresolved, because the repository's job is to document the audit
  trail in full — including the finding that the spatial extension cannot be
  supported by the data as released. The manuscript's Section 8 ("Boundary
  Conditions and Directions for Future Research") summarizes this in two sentences;
  the full diagnostic detail — *why* the 188/129 split doesn't reproduce, *why* the
  SAR model can't be re-run — lives only here, in `docs/LIMITATIONS.md` and
  `results/h3_*.csv`.
- The manuscript's abstract, as currently drafted, is reproduced verbatim in
  [`manuscript/ABSTRACT.md`](manuscript/ABSTRACT.md); the manuscript file itself
  lives in `manuscript/`.

If you are here because you read the manuscript and want to check a specific H1/H2
number: everything you need is in the table below. If you are here because you want
to know what happened to the spatial story (H3, SAR, the 18-district claim): that is
covered in full in `docs/LIMITATIONS.md`, not in the manuscript.

---

## Why this repository exists

An earlier manuscript (five near-identical drafts, in fact, submitted in parallel to
different journals) reported:

- 18 Hong Kong administrative districts in the panel,
- a tourist-core / non-tourist subgroup split of 188 / 129 listings with a
  statistically significant, sign-reversing interaction (H3),
- a 4-quarter cumulative "recovery" effect on exit risk of OR = 0.714 (*p* < .05)
  with an accompanying "gain-sensitivity" narrative, and
- a spatial autoregressive (SAR) model with in-sample R² = 0.808.

Opening the two data files that were said to produce these numbers and rerunning the
pipeline from scratch surfaces three problems, in order of severity:

1. **A quarterly-snapshot merge defect.** `neighbourhood_cleansed` (and the
   co-located `latitude`/`longitude`) is missing for 746 of 3,614 listing-quarter
   rows (20.6%). Because physical location cannot change quarter to quarter, this
   is diagnosable directly: for 285 of 401 listings (71%), the *same* listing has a
   known district in some quarters and a missing district in others. That is the
   signature of a failed join against a subset of the quarterly snapshot files, not
   real missingness. See `src/01_fix_district.py` and Figure 1.
2. **The panel covers 13 districts, not 18.** This is not an artifact of the merge
   defect — it is true of the raw file before any repair. The "18 administrative
   districts" claim in the earlier manuscript is not supported by the released data.
3. **The reported 188/129 tourist-core split cannot be reproduced from the raw
   file under any district-assignment rule tried here** — not the repaired
   assignment (299/50 before covariate-driven listwise deletion, 270/47 after), and
   not the raw, unrepaired assignment taken at face value (342/58). See
   `figures/supplementary/fig_s1_h3_subgroup_and_split_sensitivity.png`, panel (b).

Fixing (1) — the only one of the three that is actually fixable from the released
data — and re-estimating every hypothesis on the repaired panel changes the
empirical picture substantially. **H1 survives with almost identical coefficients.
H3 collapses entirely. H2 survives but the associated "gain-sensitivity /
loss-aversion" magnitude story does not** — the earlier manuscript emphasized a
specific 4-quarter window result; a full sensitivity sweep here (2–8 quarters) shows
the *direction* is fairly stable (convergence lowers exit risk; divergence does not
reliably raise it) but the significance of any single window is not something that
should be reported without also reporting the sweep, given how fast N and event
counts shrink as the window widens.

---

## Headline results (this repository)

| Hypothesis | Earlier manuscript | This re-audit | Verdict |
|---|---|---|---|
| **H1a** fit → shorter lifetime | β = −0.928, *p* = .088, N = 317 | β = **−0.941**, *p* = **.085**, N = **317** | Reproduces closely |
| **H1b** variability → longer lifetime | β = −0.869, n.s. | β = **−0.898**, n.s. | Reproduces closely (still not supported) |
| **H2a** convergence → lower exit risk | OR = 0.714, *p* < .05 (4Q window only) | OR = 0.42–0.71 across 2–6Q, **significant (p<.10) at 2Q, 4Q, 6Q**; direction consistent at every window tested | Directionally supported; magnitude is window-sensitive — see Figure 3 |
| **H2b** divergence → higher exit risk | OR = 1.050, n.s. | OR = 0.96–1.55 across windows, **never significant**, sign not even stable | Not supported at any window |
| **H3a/H3b** spatial reversal | β = −1.318\* (tourist) / β = −4.474† (non-tourist), reported as a clean sign reversal | β = −0.605, n.s. (tourist) / β = −1.137, n.s. (non-tourist) — **no significant effect in either subgroup**, no reversal | **Does not survive** the district repair — not carried into the manuscript |
| SAR spatial model (N=18 districts) | in-sample R² = 0.808 | not re-estimated here — **the panel does not contain 18 districts**, so the model as specified cannot be run on real data at all | Unresolved / not re-estimable as specified — not carried into the manuscript |

H1 and H2 are the two rows the manuscript reports. H3 and the SAR row are audit
findings retained here for transparency; see `docs/LIMITATIONS.md` for why they
were scoped out rather than forced into a weaker version of the original claim.

> **Note on manuscript table numbering.** The manuscript's tables were renumbered
> when the descriptive-statistics table was moved earlier in the text (from
> Section 6 to Section 3). Descriptive stats are now **Table 1** (was Table 6);
> variable definitions are now **Table 2** (was Table 1); the data-quality audit
> summary is now **Table 3** (was Table 2); the H1 lifetime-model results are now
> **Table 4** (was Table 3); the H2 window-sensitivity summary is now **Table 5**
> (was Table 4); and the full H2 window-by-window estimates are now **Table 6**
> (was Table 5). The correspondences below use the current (post-renumbering)
> table numbers.

Full numeric output: [`results/h1_ols_results.csv`](results/h1_ols_results.csv)
— corresponds to manuscript **Table 4**,
[`results/h2_momentum_by_window.csv`](results/h2_momentum_by_window.csv)
— corresponds to manuscript **Table 6** (full window-by-window estimates),
[`results/h3_subgroup_results.csv`](results/h3_subgroup_results.csv),
[`results/h3_split_comparison.csv`](results/h3_split_comparison.csv) — audit-only,
not in the manuscript,
[`results/district_repair_diagnostics.csv`](results/district_repair_diagnostics.csv)
— corresponds to manuscript **Table 3** (data-quality audit summary),
[`results/descriptive_stats.csv`](results/descriptive_stats.csv) — corresponds to
manuscript **Table 1**.

[`results/variable_definitions.csv`](results/variable_definitions.csv) —
corresponds to manuscript **Table 2** (variable definitions: `sem_distance`,
`fit_init`, `variability_init`, `pos_step`/`neg_step`, `Lifetime`, `Exit`,
`District`, their level of observation, and construction).

---

## Figures

All figures are grayscale (no color channel used for encoding — pattern, marker
shape, and fill are used instead), serif-typeset, 300 dpi. `fig1`–`fig3` are
generated by `src/05_make_figures.py`; `fig4`–`fig5` are generated by
`src/06_make_manuscript_figures.py`, added when the manuscript's specification-curve
and attrition figures were introduced.

| File | Content |
|---|---|
| `figures/fig1_district_repair_diagnostic.png` | (a) % of rows with missing district, before/after repair. (b) Row counts by district, before/after — showing the true 13-district coverage and the size of the recovered "missing" block. |
| `figures/fig2_h1_forest_plot.png` | H1a/H1b coefficients (M1–M3) with 90%/95% CI, forest-plot style. Corresponds to manuscript Figure 2. |
| `figures/fig3_h2_momentum_sensitivity.png` | Odds ratios (with 95% CI) for convergence and divergence momentum across 2–8 quarter accumulation windows, with N and event count k annotated at every point. Corresponds to manuscript Figure 3. |
| `figures/fig4_specification_curve.png` | All 12 H2 specifications (6 windows × 2 directions) pooled into a single sorted specification curve — convergence estimates cluster below OR=1, divergence estimates straddle it. Corresponds to manuscript Figure 4. |
| `figures/fig5_attrition_diagram.png` | Estimation-sample size (N) and exit-event count (k) across the H2 window sweep, with the 6Q/8Q sparse-event range flagged for future Firth re-estimation. Corresponds to manuscript Figure 5. |
| `figures/supplementary/fig_s1_h3_subgroup_and_split_sensitivity.png` | (a) H3 subgroup coefficients under the repaired district assignment — no significant effects. (b) The tourist-core/non-tourist split under three different district-handling methods, showing how unstable the earlier manuscript's 188/129 split is relative to anything reproducible from the raw file. **Not in the manuscript** — kept here as part of the H3 audit trail. Formerly `figures/fig4_h3_subgroup_and_split_sensitivity.png`; renumbered to avoid colliding with the manuscript's own Figure 4. |

---

## Repository structure

```
.
├── README.md
├── requirements.txt
├── LICENSE
├── run_all.sh                          # runs the full pipeline end-to-end
│
├── data/
│   ├── IV_panel.csv                    # raw panel, as released (3,614 rows, 401 listings)
│   ├── dataset_0322.xlsx               # raw two-sheet workbook, as released
│   └── panel_fixed.csv                 # generated by 01_fix_district.py (repaired district)
│
├── manuscript/
│   ├── ABSTRACT.md                     # verbatim manuscript abstract + keywords
│   └── convergence_without_divergence.docx   # current manuscript draft
│
├── src/
│   ├── 01_fix_district.py              # diagnoses + repairs the merge defect
│   ├── 02_h1_lifetime_ols.py           # H1a/H1b: OLS on first-spell lifetime
│   ├── 03_h2_momentum_logit.py         # H2a/H2b: discrete-time logit, 2-8Q window sweep
│   ├── 04_h3_spatial_subgroup.py       # H3a/H3b: subgroup OLS + split-sensitivity check (audit-only, not in manuscript)
│   ├── 05_make_figures.py              # grayscale journal-style figures 1-3 from results/*.csv
│   └── 06_make_manuscript_figures.py   # figures 4-5: specification curve + attrition diagram
│
├── results/
│   ├── district_repair_diagnostics.csv # corresponds to manuscript Table 3
│   ├── district_coverage_before_after.csv
│   ├── descriptive_stats.csv           # corresponds to manuscript Table 1
│   ├── variable_definitions.csv        # corresponds to manuscript Table 2
│   ├── h1_analysis_sample.csv          # listing-level analysis sample (N=349 pre-, 317 post-listwise-deletion)
│   ├── h1_ols_results.csv              # corresponds to manuscript Table 4
│   ├── h2_momentum_by_window.csv       # corresponds to manuscript Table 6 (full window-by-window)
│   ├── h3_subgroup_results.csv         # audit-only, not in manuscript
│   └── h3_split_comparison.csv         # audit-only, not in manuscript
│
├── figures/
│   ├── fig1_district_repair_diagnostic.png
│   ├── fig2_h1_forest_plot.png
│   ├── fig3_h2_momentum_sensitivity.png
│   ├── fig4_specification_curve.png
│   ├── fig5_attrition_diagram.png
│   └── supplementary/
│       └── fig_s1_h3_subgroup_and_split_sensitivity.png   # formerly fig4; audit-only, not in manuscript
│
└── docs/
    └── LIMITATIONS.md                  # what this re-audit does and does not resolve;
                                         # see top of file for how this maps onto the
                                         # manuscript's own Section 8
```

---

## Reproducing everything

```bash
git clone <this-repo>
cd <this-repo>
pip install -r requirements.txt
bash run_all.sh
```

`run_all.sh` runs `src/01` → `06` in order, printing each script's console diagnostics
and regenerating every file under `results/` and `figures/` from the two raw files in
`data/`. Nothing under `results/` or `figures/` is hand-edited; if you change a
script, rerun `run_all.sh` and every downstream number and figure updates.

Runtime: under 30 seconds end-to-end on a standard laptop (no embedding model is
re-run; the pipeline consumes the pre-computed `sem_distance` / `sem_std` /
embedding columns already present in `IV_panel.csv`).

---

## What was *not* fixed, and why

This is the most important section of this README. Read it before citing any number above.
The same four points, with additional diagnostic detail and the H3/SAR audit trail,
are maintained in full in [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md).

1. **`sem_distance` (the core "representational fit" measure) is used as-is,
   including its own pre-existing missingness (21% of rows, independent of the
   district defect).** An attempt was made to recompute it from the raw embedding
   columns (`listing_embed_1..32`, `review_embed_1..32_qtr`) already present in
   `IV_panel.csv`, using the district-quarter centroid definition described in the
   associated manuscript. The recomputed values correlated at **r = −0.009** with
   the original column — i.e., not at all — meaning whatever normalization or
   aggregation procedure originally produced `sem_distance` could not be reverse-engineered
   from the released panel alone. Rather than silently substitute a
   self-generated variable that behaves nothing like the original, this repository
   uses the original `sem_distance` / `sem_std` / `delta_sem_distance` columns
   unchanged, missingness and all. This is a materially different (and more
   defensible) choice than either (a) fabricating a replacement or (b) leaving the
   district bug in place, but it is still a limitation: it means H2's sample size
   (N = 516–1,021 depending on window, vs. the 1,798 claimed in the earlier
   manuscript) is constrained by missingness this repository did not create and
   cannot resolve without the original embedding pipeline.
2. **The SAR / Moran's I spatial model is not re-estimated in this repository.**
   It requires the full 18-district cross-section the earlier manuscript assumed;
   the actual data contain 13 districts, several with fewer than 10 listing-quarter
   observations even after repair (see Figure 1b). Re-running a spatial-lag model
   on 13 badly-imbalanced units (one district, Yau Tsim Mong, accounts for ~64% of
   all rows) would not be a meaningful re-audit of the original SAR claim — it would
   be a different, weaker analysis wearing the same name. The honest conclusion is
   that **the SAR result cannot be verified or refuted from the released data as
   specified**, not that it is confirmed at a smaller N. This is why no spatial
   extension appears in the current manuscript.
3. **`dataset_0322.xlsx`'s `H12`/`H3` sheets were not used as the basis for any
   number in this README.** They are retained in `data/` because the earlier
   manuscript's R module reads from them, but this repository's Python pipeline
   rebuilds the H1/H2/H3 analysis samples independently from `IV_panel.csv` so that
   every intermediate step is auditable in one language and one set of scripts.
   Anyone wanting to cross-check `dataset_0322.xlsx` directly should treat that as
   a separate, still-open task.
4. **First-spell restriction.** Both H1 and H2 here are estimated on each listing's
   first continuous run of quarters (matching the earlier manuscript's stated
   restriction for H1). 152 of 400 listings (38%) have at least one gap in the
   panel and therefore more than one "spell"; only the first is used. This is a
   defensible, disclosed choice, not a discovered fact about the data — a different
   defensible choice (e.g., treating gaps as temporary absence rather than exit)
   would change N and possibly some point estimates.

See [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) for the full list with more detail,
including the H3/SAR audit trail that the manuscript itself only summarizes.

---

## Data

### Source
Panel data originate from [Inside Airbnb](http://insideairbnb.com/) quarterly
snapshots for Hong Kong, 2021Q1–2025Q2 (18 calendar quarters, not 17 — the earlier
manuscript's "seventeen-quarter panel" phrasing is also inconsistent with the
released file, which contains 18 distinct `period_qtr` values).

### `data/IV_panel.csv`
3,614 rows × 153 columns. One row per listing-quarter. 401 unique listings, 13
unique non-null districts pre-repair (18 claimed, not observed). Contains
pre-computed SBERT-derived embedding columns (`listing_embed_1..32`,
`review_embed_1..32_qtr`, `amenity_embed_1..32`), the derived `sem_distance` /
`sem_std` / `delta_sem_distance` semantic-fit measures, and standard listing
metadata (price, superhost flag, amenity count, review counts, VADER sentiment).

### `data/dataset_0322.xlsx`
Two-sheet workbook (`H12`, `H3`) referenced by the earlier manuscript's R module as
pre-aggregated model-ready samples. Retained for provenance; not used to generate
any figure or result in this repository (see point 3 above).

### `data/panel_fixed.csv`
Generated by `src/01_fix_district.py`. Identical to `IV_panel.csv` except: (a)
`neighbourhood_cleansed`, `latitude`, `longitude` are forward/backward-filled within
`listing_id` (location is time-invariant, so this is lossless recovery, not
imputation, for the 738/746 rows where at least one other quarter for that listing
has a known district); (b) `platform_activity_loo` is recomputed against the
repaired district; (c) 8 rows belonging to a single listing with *no* recoverable
district in *any* quarter are dropped.

---

## Methods (as re-implemented here)

### H1 — Representational fit/variability → listing lifetime
OLS on each listing's first continuous spell. `fit_init` / `variability_init` are
the mean of `sem_distance` / `sem_std` over the spell's first four quarters.
Entry-quarter fixed effects, HC1 heteroscedasticity-robust SE. `src/02_h1_lifetime_ols.py`.

### H2 — Representational momentum → exit risk
Discrete-time logit on the same first-spell panel. `pos_step` / `neg_step` are the
signed quarter-on-quarter change in `sem_distance` (convergence / divergence),
rolled up over trailing windows of 2, 3, 4, 5, 6, and 8 quarters, z-scored, lagged
one quarter. Listing-clustered SE. A linear quarter-index trend is used in place of
full quarter fixed effects because the latter fails to converge (quasi-separation)
at the 6Q and 8Q windows, where fewer than 20 exit events remain. `src/03_h2_momentum_logit.py`.

Estimated across the full window sweep W = {2, 3, 4, 5, 6, 8} rather than at a
single pre-chosen window, following specification-curve logic (Simonsohn, Simmons,
& Nelson, 2020); `src/06_make_manuscript_figures.py` pools all twelve resulting
estimates into the sorted specification curve reported as manuscript Figure 4.

### H3 — Spatial subgroup extension (audit-only; not in the manuscript)
The H1 specification re-estimated separately for tourist-core districts (Yau Tsim
Mong, Wan Chai, Central & Western) and the remaining districts, using the *repaired*
district assignment, plus a full-sample interaction model. `src/04_h3_spatial_subgroup.py`.
Retained in this repository as an audit finding — see `docs/LIMITATIONS.md` for why
it does not appear in the manuscript.

---

## Requirements

```
pandas>=2.0
numpy>=1.24
statsmodels>=0.14
matplotlib>=3.7
openpyxl>=3.1
```

See `requirements.txt`.

---

## License

MIT License (see `LICENSE`). Underlying Inside Airbnb data are subject to their own
[terms of use](http://insideairbnb.com/about/).

## Provenance note

This repository's data files (`IV_panel.csv`, `dataset_0322.xlsx`) are unmodified
copies of the files circulated with an earlier, non-peer-reviewed manuscript draft
that has not been published. That manuscript's specific numeric claims (18
districts, N=1,798 H2 panel, OR=0.714 as a headline single-window result, the
188/129 H3 split, SAR R²=0.808) are addressed point-by-point above and are not
repeated here as established findings. The current manuscript, scoped to H1/H2 only,
is the peer-review-track output of this audit; see "This repository vs. the
manuscript" above.
