# Limitations of this re-audit

> **Cross-reference note (added when the manuscript was scoped to H1/H2 only).**
> The manuscript currently in preparation, *"Convergence Without Divergence,"*
> restates item 1 (`sem_distance` provenance) and item 4 (first-spell restriction)
> below as its own "Boundary Conditions and Directions for Future Research"
> (Section 8), reframed there as a forward-looking research agenda rather than as
> unresolved problems. Items 2 (SAR model), 3 (`dataset_0322.xlsx`), 5
> (quarter-count discrepancy), and the H3 split-instability finding referenced in
> item 6 are **not** restated in the manuscript — Section 8 mentions only, in
> passing, that the panel does not support a spatial extension. The full
> diagnostic trail for *why* H3 and the SAR model fail — the actual subgroup
> coefficients, the split-sensitivity check across three district-handling rules
> (Figure S1), the district-imbalance numbers — lives only here. Read this file
> as the superset of the manuscript's Section 8: everything load-bearing in the
> manuscript traces back to a point below, but not everything below made it into
> the manuscript.

This document lists, in one place, everything this repository does and does
not resolve about the data and results it works with. It is meant to be read
alongside the main README, not as a replacement for it. Nothing here should
be treated as settled — several items are open questions this repository
raises but cannot close on its own.

## 1. `sem_distance` could not be independently reconstructed

`IV_panel.csv` ships with pre-computed `sem_distance`, `sem_std`, and
`delta_sem_distance` columns, plus 32-dimensional embedding columns
(`listing_embed_1..32`, `review_embed_1..32_qtr`, `amenity_embed_1..32`). An
attempt was made to reconstruct `sem_distance` directly from the embedding
columns using the district-quarter centroid cosine-distance definition
described in the manuscript this repository audits. The reconstructed series
correlated with the original `sem_distance` column at **r = −0.009** — no
better than chance.

This means one of the following is true, and this repository cannot
determine which:

- the released embedding columns are not the ones actually used to compute
  `sem_distance` (e.g., a different normalization, a different centroid
  definition, or a different embedding model version was used upstream), or
- `sem_distance` was computed correctly from these embeddings but with a
  transformation not recoverable from the columns alone, or
- `sem_distance` was not computed from these embeddings at all.

**Decision made here:** rather than substitute a self-generated variable that
does not behave like the original (which would silently change what every
downstream H1/H2 coefficient means), this repository uses the original
`sem_distance` / `sem_std` / `delta_sem_distance` columns as released,
including their own pre-existing missingness (independent of the district
defect described in the README). This is the more conservative choice, but
it is still a choice, and it means:

- H1 and H2 samples are smaller than they would be if this missingness were
  resolved,
- no claim is made in this repository about *how* `sem_distance` was
  originally computed, only that it is used unmodified, and
- anyone attempting to extend this repository should treat the embedding
  columns and `sem_distance` as two pieces of evidence that currently do not
  reconcile, not as a validated measurement pipeline.

## 2. The SAR / spatial-lag model is not re-estimated

The manuscript being audited reports a spatial autoregressive model over an
18-district cross-section with in-sample R² = 0.808. The repaired panel in
this repository contains **13** districts, one of which (Yau Tsim Mong)
accounts for roughly two-thirds of all listing-quarter rows even after
repair (Figure 1b). Several districts have single-digit row counts.

Re-estimating a K-nearest-neighbors spatial-lag model on 13 units with this
degree of imbalance would not be a like-for-like re-audit of the original
SAR claim — it would be a structurally different, much weaker analysis that
happens to share a name with the original. This repository therefore does
**not** attempt it. The correct summary is: *the SAR result, as specified in
the original manuscript, cannot be verified or refuted from the data
released with that manuscript* — not that it is confirmed, and not that it
is disconfirmed, at a smaller N.

Resolving this would require either (a) recovering the missing quarterly
snapshot data for the 5 districts absent from the released panel, or (b)
obtaining a corrected, complete 18-district version of `IV_panel.csv` from
whoever produced it originally.

## 3. `dataset_0322.xlsx` was not used as an input to any result

The two-sheet workbook (`H12`, `H3`) referenced by the original manuscript's
R module is retained in `data/` for provenance only. Every result in this
repository is built independently from `IV_panel.csv` via the Python
pipeline in `src/`, so that every intermediate step is auditable in one
language. Whether `dataset_0322.xlsx` is internally consistent with
`IV_panel.csv`, or with the original manuscript's reported numbers, is a
**separate, still-open question** this repository does not address. Anyone
wanting to check that consistency should treat it as new work, not something
already covered here.

## 4. First-spell restriction is a disclosed choice, not a discovered fact

152 of 400 listings (38%) have at least one gap in the quarterly panel —
i.e., more than one observation "spell." Both `02_h1_lifetime_ols.py` and
`03_h2_momentum_logit.py` restrict to each listing's *first* continuous
spell, matching the original manuscript's stated restriction for H1.

This is a defensible choice but not the only one. A gap in the panel could
mean the listing was actually delisted and relisted (a real exit event,
arguably relevant to H2), or it could mean the listing was active but simply
absent from a given quarterly snapshot for reasons unrelated to platform
exit (e.g., a scraping gap on Inside Airbnb's end). This repository does not
attempt to distinguish these two cases. A different, equally defensible
choice — e.g., treating gaps under some threshold as temporary absence
rather than exit, and stitching spells together — would change both N and
some point estimates in H1 and H2. This has not been tested here and should
be treated as an open robustness check, not a settled methodological
decision.

## 5. Quarter-count discrepancy

The manuscript being audited describes a "seventeen-quarter panel." The
released `IV_panel.csv` contains **18** distinct `period_qtr` values
(2021Q1–2025Q2 inclusive). This is a minor discrepancy relative to items 1–4
above, but it is disclosed here because it is one more instance of a stated
fact about the data not matching the data itself, and because the reader
should not have to re-derive it independently to notice it.

## 6. What this repository does *not* claim

To be explicit about scope: this repository does not claim to have produced
a publishable, hypothesis-confirming re-analysis. Its purpose is narrower —
to establish, transparently and reproducibly, what can and cannot be
recovered from the two data files that were said to support the original
manuscript's claims. Three of six original hypotheses (H1a, H1b, and the
directional component of H2) find support broadly consistent with the
original manuscript after the district-merge defect is repaired. H3 does
not survive the repair. The SAR/spatial model is not re-estimable as
specified. Anyone using this repository as a basis for further work should
treat items 1–5 above as prerequisites to resolve, not footnotes to skip.

---

*See `figures/supplementary/fig_s1_h3_subgroup_and_split_sensitivity.png` for
the H3 subgroup coefficients and the three-way split-composition comparison
("as reported in paper" 188/129 vs. "raw district, no repair" 342/58 vs.
"repaired district, this pipeline" 299/50) referenced in item 6 above and in
the README's H3 row. This figure is not reproduced anywhere in the
manuscript.*
