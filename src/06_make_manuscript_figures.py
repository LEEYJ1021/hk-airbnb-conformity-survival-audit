"""
06_make_manuscript_figures.py

Generates the two figures added when the manuscript's H2 window-sensitivity
sweep was recast as a specification-curve analysis:

    figures/fig4_specification_curve.png
        All 12 H2 specifications (windows {2,3,4,5,6,8} x {convergence,
        divergence}) pooled into a single odds-ratio curve, sorted by point
        estimate, following Simonsohn, Simmons, & Nelson (2020).

    figures/fig5_attrition_diagram.png
        Estimation-sample size (N) and exit-event count (k) across the same
        six windows, with the sparse-event range (6Q, 8Q) shaded and flagged
        for future Firth (1993) bias-corrected re-estimation.

Both figures are read directly from results/h2_momentum_by_window.csv, which
is produced by 03_h2_momentum_logit.py. This script performs no new
estimation -- it only re-visualizes existing results, consistent with the
rest of this repository's separation between estimation scripts (01-04) and
figure scripts (05-06).

Grayscale only; no color channel is used to encode meaning (marker fill and
shape carry significance and window information instead), matching fig1-fig3.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

IN_PATH = "results/h2_momentum_by_window.csv"
FIG4_OUT = "figures/fig4_specification_curve.png"
FIG5_OUT = "figures/fig5_attrition_diagram.png"

SPARSE_EVENT_WINDOWS = {6, 8}
ALPHA = 0.10  # significance threshold used throughout the manuscript (p < .10)


def load_long_format(path: str) -> pd.DataFrame:
    """
    Expects results/h2_momentum_by_window.csv in long format with columns:
        window, effect (convergence/divergence), n, k, odds_ratio, ci_low, ci_high, p_value
    Adjust the melt/parsing logic here if the upstream CSV schema differs.
    """
    df = pd.read_csv(path)
    required = {"window", "effect", "n", "k", "odds_ratio", "ci_low", "ci_high", "p_value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"{path} is missing expected columns {missing}. "
            "Update 06_make_manuscript_figures.py to match the current "
            "h2_momentum_by_window.csv schema before regenerating fig4/fig5."
        )
    return df


def make_fig4_specification_curve(df: pd.DataFrame, out_path: str) -> None:
    plot_df = df.copy()
    plot_df["sig"] = (plot_df["p_value"] < ALPHA) & (plot_df["effect"] == "convergence")
    plot_df = plot_df.sort_values("odds_ratio").reset_index(drop=True)
    plot_df["x"] = range(len(plot_df))

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(9, 6), sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )

    for _, row in plot_df.iterrows():
        marker = "s" if row["effect"] == "divergence" else ("o" if not row["sig"] else "o")
        facecolor = "black" if (row["effect"] == "convergence" and row["sig"]) else "white"
        ax_top.plot([row["x"], row["x"]], [row["ci_low"], row["ci_high"]], color="black", lw=1)
        ax_top.scatter(
            row["x"], row["odds_ratio"],
            marker=marker, facecolor=facecolor, edgecolor="black", s=60, zorder=3,
        )

    ax_top.axhline(1.0, color="black", linestyle="--", lw=1)
    ax_top.set_ylabel("Odds ratio (exit next quarter)")
    ax_top.set_title("Figure 4. Specification curve across the full H2 window x effect space\n"
                      "(12 independently estimated specifications, sorted by point estimate)")

    ax_bot.scatter(plot_df["x"], plot_df["window"], marker="s", color="black", s=30)
    ax_bot.set_ylabel("Window")
    ax_bot.set_xlabel("Specification (sorted by estimated odds ratio, left to right)")
    ax_bot.set_xticks([])
    ax_bot.yaxis.set_major_locator(mticker.FixedLocator(sorted(plot_df["window"].unique())))

    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def make_fig5_attrition_diagram(df: pd.DataFrame, out_path: str) -> None:
    # N and k are identical across effect (convergence/divergence) within a window,
    # so collapse to one row per window.
    attrition = (
        df.drop_duplicates(subset=["window"])[["window", "n", "k"]]
        .sort_values("window")
        .reset_index(drop=True)
    )

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(attrition["window"].astype(str), attrition["n"], color="lightgray", edgecolor="black")
    ax1.set_xlabel("Momentum accumulation window (quarters)")
    ax1.set_ylabel("Listing-quarter observations (N)")

    ax2 = ax1.twinx()
    ax2.plot(attrition["window"].astype(str), attrition["k"], color="black", marker="o")
    ax2.set_ylabel("Number of exit events (k)")

    sparse_mask = attrition["window"].isin(SPARSE_EVENT_WINDOWS)
    if sparse_mask.any():
        first_sparse_idx = attrition.index[sparse_mask].min()
        ax1.axvspan(first_sparse_idx - 0.5, len(attrition) - 0.5, color="lightgray", alpha=0.3)
        ax1.text(
            len(attrition) - 1, attrition["n"].max() * 0.9,
            "Sparse-event range\n(flagged for bias-corrected\nfollow-up estimation)",
            ha="right", va="top", fontsize=8, style="italic",
        )

    ax1.set_title("Figure 5. Estimation-sample size and exit-event count\nacross the H2 window sweep")
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def main() -> None:
    df = load_long_format(IN_PATH)
    make_fig4_specification_curve(df, FIG4_OUT)
    make_fig5_attrition_diagram(df, FIG5_OUT)
    print(f"Wrote {FIG4_OUT}")
    print(f"Wrote {FIG5_OUT}")


if __name__ == "__main__":
    main()
