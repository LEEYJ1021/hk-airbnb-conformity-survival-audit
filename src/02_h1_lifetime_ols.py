"""
02_h1_lifetime_ols.py

H1a/H1b: representational fit and variability as predictors of listing
lifetime, estimated on the first continuous observation spell of each
listing (early-window averages, entry-quarter fixed effects, HC1 SE).

Runs three specifications (M1 joint, M2 fit-only, M3 variability-only)
and writes results/h1_ols_results.csv.

This script consumes data/panel_fixed.csv (output of 01_fix_district.py).
It does NOT alter sem_distance / sem_std -- only the district assignment
and platform_activity control were corrected upstream.
"""
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = ROOT / "data" / "panel_fixed.csv"
H1_SAMPLE_PATH = ROOT / "results" / "h1_analysis_sample.csv"
H1_RESULTS_PATH = ROOT / "results" / "h1_ols_results.csv"

Q_ORDER = ['2021Q1','2021Q2','2021Q3','2021Q4','2022Q1','2022Q2','2022Q3','2022Q4',
           '2023Q1','2023Q2','2023Q3','2023Q4','2024Q1','2024Q2','2024Q3','2024Q4',
           '2025Q1','2025Q2']

CONTROLS = "activity_init + reviews_pq + price_log + superhost + amenity_count + sentiment"


def assign_first_spell(df: pd.DataFrame) -> pd.DataFrame:
    """A listing's 'first spell' is its longest-observed run of
    consecutive quarters starting from its first appearance. A gap
    (missing quarter row) starts a new spell; only the first spell is
    retained, matching the paper's stated restriction to a clean
    entry-to-exit trajectory uncontaminated by re-entry."""
    df = df.sort_values(['listing_id', 'q_idx']).reset_index(drop=True)
    same_listing = df['listing_id'] == df['listing_id'].shift(1)
    gap = df['q_idx'] - df['q_idx'].shift(1)
    new_spell = ~(same_listing & (gap == 1))
    df['spell_id'] = new_spell.cumsum()
    first_spell_id = df.groupby('listing_id')['spell_id'].transform('min')
    df['is_first_spell'] = df['spell_id'] == first_spell_id
    fs = df[df['is_first_spell']].copy()
    fs['lifetime'] = fs.groupby('listing_id')['q_idx'].transform('count')
    max_q = fs.groupby('listing_id')['q_idx'].transform('max')
    fs['censored'] = (max_q == fs['q_idx'].max()).astype(int)
    return fs


def build_h1_sample(fs: pd.DataFrame) -> pd.DataFrame:
    fs = fs.sort_values(['listing_id', 'q_idx'])
    fs['rank_in_spell'] = fs.groupby('listing_id').cumcount()
    early = fs[fs['rank_in_spell'] < 4]

    agg = early.groupby('listing_id').agg(
        fit_init=('sem_distance', 'mean'),
        variability_init=('sem_std', 'mean'),
        activity_init=('platform_activity_loo', 'mean'),
        reviews_pq=('n_reviews_qtr', 'mean'),
        price_log=('price_log', 'mean'),
        superhost=('superhost_flag', 'max'),
        amenity_count=('amenity_count', 'mean'),
        sentiment=('sentiment_mean_qtr', 'mean'),
        entry_qtr=('period_qtr', 'first'),
    ).reset_index()

    meta = fs.groupby('listing_id').agg(
        lifetime=('lifetime', 'first'),
        censored=('censored', 'first'),
        district=('neighbourhood_cleansed', 'first'),
        is_tourist=('is_tourist', 'first'),
    ).reset_index()

    h1 = agg.merge(meta, on='listing_id')
    h1 = h1.dropna(subset=['fit_init', 'variability_init']).copy()
    h1['entry_q'] = h1['entry_qtr'].astype(str)
    return h1


def run_models(h1: pd.DataFrame) -> pd.DataFrame:
    specs = {
        "M1_baseline": f"lifetime ~ fit_init + variability_init + {CONTROLS} + C(entry_q)",
        "M2_fit_only": f"lifetime ~ fit_init + {CONTROLS} + C(entry_q)",
        "M3_variability_only": f"lifetime ~ variability_init + {CONTROLS} + C(entry_q)",
    }
    rows = []
    for name, formula in specs.items():
        m = smf.ols(formula, data=h1).fit(cov_type='HC1')
        for var in ['fit_init', 'variability_init']:
            if var in m.params.index:
                rows.append({
                    'model': name, 'term': var,
                    'beta': m.params[var], 'se': m.bse[var], 'p': m.pvalues[var],
                    'N': int(m.nobs), 'R2': m.rsquared, 'adj_R2': m.rsquared_adj,
                })
    return pd.DataFrame(rows)


def main():
    df = pd.read_csv(PANEL_PATH)
    df['q_idx'] = df['period_qtr'].map({q: i for i, q in enumerate(Q_ORDER)})

    fs = assign_first_spell(df)
    h1 = build_h1_sample(fs)
    h1.to_csv(H1_SAMPLE_PATH, index=False)

    results = run_models(h1)
    results.to_csv(H1_RESULTS_PATH, index=False)

    print(f"H1 analysis sample: N={len(h1)} listings -> {H1_SAMPLE_PATH}")
    print(results.to_string(index=False))
    print(f"\nWrote -> {H1_RESULTS_PATH}")


if __name__ == "__main__":
    main()
