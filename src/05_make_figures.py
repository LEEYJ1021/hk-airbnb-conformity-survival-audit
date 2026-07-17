"""
05_make_figures.py

Generates grayscale, journal-style figures (matplotlib, serif type,
300 dpi, no color -- pattern/marker/linestyle used to distinguish
series) from the outputs of scripts 01-04. Run after 01-04.

Figures:
  fig1_district_repair_diagnostic.png  -- before/after data-quality repair
  fig2_h1_forest_plot.png              -- H1a/H1b coefficients, M1-M3
  fig3_h2_momentum_sensitivity.png     -- H2 odds ratios across windows
  fig4_h3_subgroup_and_split_sensitivity.png -- H3 subgroup coefficients
                                                  + split-method sensitivity
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGDIR = ROOT / "figures"
FIGDIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- style ----
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif", "Georgia"],
    "font.size": 9.5,
    "axes.edgecolor": "black",
    "axes.linewidth": 0.8,
    "axes.grid": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": "black",
    "ytick.color": "black",
    "text.color": "black",
    "axes.labelcolor": "black",
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

BLACK = "#000000"
DGRAY = "#4d4d4d"
MGRAY = "#8c8c8c"
LGRAY = "#bfbfbf"


def savefig(fig, name):
    path = FIGDIR / name
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print(f"  wrote {path}")


# ============================================================ FIGURE 1 =====
def fig1_district_repair():
    diag = pd.read_csv(RESULTS / "district_repair_diagnostics.csv")
    cov = pd.read_csv(RESULTS / "district_coverage_before_after.csv")
    cov = cov.sort_values("n_rows_fixed", ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4))

    # --- panel a: missingness before/after ---
    ax = axes[0]
    before = diag.loc[diag.stage == "before_fix"].iloc[0]
    after = diag.loc[diag.stage == "after_fix"].iloc[0]
    vals = [before["pct_district_null"], after["pct_district_null"]]
    bars = ax.bar([0, 1], vals, width=0.5, color=[LGRAY, BLACK], edgecolor="black", linewidth=0.8)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Raw panel\n(as released)", "After district\nrepair"])
    ax.set_ylabel("District field missing (%)")
    ax.set_ylim(0, max(vals) * 1.35)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + max(vals) * 0.03, f"{v:.1f}%",
                 ha="center", va="bottom", fontsize=9)
    n_mixed = int(before["n_listings_with_inconsistent_district_across_quarters"])
    ax.set_title(f"(a) Same-listing district inconsistency:\n{n_mixed}/401 listings (71%) affected",
                 fontsize=9, loc="left")

    # --- panel b: district coverage before/after (row counts, sorted) ---
    ax = axes[1]
    y = np.arange(len(cov))
    ax.barh(y - 0.19, cov["n_rows_raw"], height=0.36, color=LGRAY, edgecolor="black",
             linewidth=0.6, label="Raw (as released)")
    ax.barh(y + 0.19, cov["n_rows_fixed"], height=0.36, color=BLACK, edgecolor="black",
             linewidth=0.6, label="Repaired")
    ax.set_yticks(y)
    ax.set_yticklabels(cov["neighbourhood_cleansed"], fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlabel("Listing-quarter observations")
    ax.set_title(f"(b) District coverage: {before['n_distinct_districts_observed']:.0f} districts observed,\nnot 18 as claimed",
                 fontsize=9, loc="left")
    ax.legend(frameon=False, fontsize=8, loc="lower right")

    fig.suptitle("Figure 1. Diagnosis and repair of the quarterly-snapshot merge defect",
                  fontsize=10.5, y=1.03)
    fig.tight_layout()
    savefig(fig, "fig1_district_repair_diagnostic.png")


# ============================================================ FIGURE 2 =====
def fig2_h1_forest():
    h1 = pd.read_csv(RESULTS / "h1_ols_results.csv")
    h1["ci_lo"] = h1["beta"] - 1.96 * h1["se"]
    h1["ci_hi"] = h1["beta"] + 1.96 * h1["se"]
    h1["ci90_lo"] = h1["beta"] - 1.645 * h1["se"]
    h1["ci90_hi"] = h1["beta"] + 1.645 * h1["se"]

    order = [
        ("M1_baseline", "fit_init", "Representational fit\n(M1, joint model)"),
        ("M2_fit_only", "fit_init", "Representational fit\n(M2, fit only)"),
        ("M1_baseline", "variability_init", "Representational variability\n(M1, joint model)"),
        ("M3_variability_only", "variability_init", "Representational variability\n(M3, variability only)"),
    ]

    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    y_positions = np.arange(len(order))[::-1]

    for y, (model, term, label) in zip(y_positions, order):
        row = h1[(h1.model == model) & (h1.term == term)].iloc[0]
        marker = "o" if term == "fit_init" else "s"
        ax.plot([row.ci_lo, row.ci_hi], [y, y], color=DGRAY, linewidth=1.1, zorder=1)
        ax.plot([row.ci90_lo, row.ci90_hi], [y, y], color=BLACK, linewidth=2.6, zorder=2)
        ax.scatter([row.beta], [y], color=BLACK, marker=marker, s=55, zorder=3, edgecolor="white", linewidth=0.6)
        sig = "†" if row.p < 0.10 else ("*" if row.p < 0.05 else "")
        ax.text(row.ci_hi + 0.15, y, f"β = {row.beta:.3f}{sig}  (p = {row.p:.3f}, N = {int(row.N)})",
                 va="center", fontsize=8)

    ax.axvline(0, color="black", linewidth=0.8, linestyle="--", zorder=0)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([lbl for _, _, lbl in order], fontsize=8.5)
    ax.set_xlabel("OLS coefficient on listing lifetime (quarters)")
    ax.set_xlim(-4.5, 5.5)
    ax.set_title("Figure 2. H1 fit and variability effects on listing lifetime\n"
                  "(thick bar = 90% CI, thin bar = 95% CI; independently rebuilt from repaired panel)",
                  fontsize=9.5, loc="left")
    fig.tight_layout()
    savefig(fig, "fig2_h1_forest_plot.png")


# ============================================================ FIGURE 3 =====
def fig3_h2_sensitivity():
    h2 = pd.read_csv(RESULTS / "h2_momentum_by_window.csv")
    h2 = h2[h2.status == "ok"].copy()

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.4), sharey=True)

    for ax, prefix, title, marker in [
        (axes[0], "pos", "(a) Positive momentum (convergence / \u201crecovery\u201d)", "o"),
        (axes[1], "neg", "(b) Negative momentum (divergence / \u201cdeterioration\u201d)", "s"),
    ]:
        x = h2["window_q"]
        OR = h2[f"{prefix}_OR"]
        lo = h2[f"{prefix}_OR_lo"]
        hi = h2[f"{prefix}_OR_hi"]
        p = h2[f"{prefix}_p"]

        for xi, ori, loi, hii in zip(x, OR, lo, hi):
            ax.plot([xi, xi], [loi, hii], color=DGRAY, linewidth=1.2, zorder=1)
        sig_mask = p < 0.10
        ax.scatter(x[sig_mask], OR[sig_mask], marker=marker, s=70, color=BLACK, zorder=3,
                   label="p < .10")
        ax.scatter(x[~sig_mask], OR[~sig_mask], marker=marker, s=70, facecolor="white",
                   edgecolor=BLACK, linewidth=1.1, zorder=3, label="n.s.")
        ax.plot(x, OR, color=MGRAY, linewidth=0.9, linestyle=":", zorder=2)
        ax.axhline(1.0, color="black", linewidth=0.8, linestyle="--", zorder=0)
        ax.set_xticks(x)
        ax.set_xlabel("Momentum accumulation window (quarters)")
        ax.set_title(title, fontsize=9, loc="left")
        ax.set_ylim(0, 4.5)

        for xi, ori, ni, ei in zip(x, OR, h2["N"], h2["events"]):
            ax.text(xi, 4.15, f"N={int(ni)}\nk={int(ei)}", ha="center", fontsize=6.3, color=DGRAY)

    axes[0].set_ylabel("Odds ratio (exit next quarter)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False, fontsize=8,
               bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("Figure 3. Momentum\u2013exit risk odds ratios across accumulation windows\n"
                 "(independently rebuilt; N and event count k shrink sharply as window widens)",
                 fontsize=9.5, y=1.06)
    fig.tight_layout()
    savefig(fig, "fig3_h2_momentum_sensitivity.png")


# ============================================================ FIGURE 4 =====
def fig4_h3():
    h3 = pd.read_csv(RESULTS / "h3_subgroup_results.csv")
    split = pd.read_csv(RESULTS / "h3_split_comparison.csv")

    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.4))

    # --- panel a: subgroup coefficients (corrected district) ---
    ax = axes[0]
    sub = h3[h3.subgroup.isin(["tourist_core (corrected)", "non_tourist (corrected)"])].copy()
    sub["ci_lo"] = sub["beta"] - 1.96 * sub["se"]
    sub["ci_hi"] = sub["beta"] + 1.96 * sub["se"]
    labels = []
    y_positions = []
    y = 0
    for grp, grp_label in [("tourist_core (corrected)", "Tourist-core"), ("non_tourist (corrected)", "Non-tourist")]:
        for term, marker in [("fit_init", "o"), ("variability_init", "s")]:
            row = sub[(sub.subgroup == grp) & (sub.term == term)].iloc[0]
            ax.plot([row.ci_lo, row.ci_hi], [y, y], color=DGRAY, linewidth=1.3)
            ax.scatter([row.beta], [y], marker=marker, s=60, color=BLACK, zorder=3,
                       edgecolor="white", linewidth=0.5)
            term_lbl = "Fit" if term == "fit_init" else "Variability"
            labels.append(f"{grp_label} \u2013 {term_lbl}  (N={int(row.N)})")
            y_positions.append(y)
            y += 1
        y += 0.6

    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=7.8)
    ax.invert_yaxis()
    ax.set_xlabel("OLS coefficient on listing lifetime")
    ax.set_title("(a) H3 subgroup coefficients\n(corrected district; none significant at p<.05)",
                 fontsize=8.8, loc="left")

    # --- panel b: split composition sensitivity ---
    ax = axes[1]
    x = np.arange(len(split))
    ax.bar(x - 0.2, split["tourist_core_n"], width=0.4, color=BLACK, edgecolor="black",
           label="Tourist-core n")
    ax.bar(x + 0.2, split["non_tourist_n"], width=0.4, color=LGRAY, edgecolor="black",
           label="Non-tourist n")
    method_labels = ["As reported\nin paper", "Raw district,\nno repair", "Repaired\ndistrict\n(this pipeline)"]
    ax.set_xticks(x)
    ax.set_xticklabels(method_labels, fontsize=7.8)
    ax.set_ylabel("Listings in subgroup")
    ax.set_ylim(0, split[["tourist_core_n", "non_tourist_n"]].values.max() * 1.28)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.set_title("(b) Subgroup composition is unstable\nacross district-handling methods",
                 fontsize=8.8, loc="left")
    for xi, t, n in zip(x, split["tourist_core_n"], split["non_tourist_n"]):
        ax.text(xi - 0.2, t + 5, str(t), ha="center", fontsize=7.5)
        ax.text(xi + 0.2, n + 5, str(n), ha="center", fontsize=7.5)

    fig.suptitle("Figure 4. H3 spatial subgroup results collapse once district assignment is corrected",
                 fontsize=9.8, y=1.04)
    fig.tight_layout()
    savefig(fig, "fig4_h3_subgroup_and_split_sensitivity.png")


def main():
    print("Generating figures...")
    fig1_district_repair()
    fig2_h1_forest()
    fig3_h2_sensitivity()
    fig4_h3()
    print("Done.")


if __name__ == "__main__":
    main()
