"""
01_fix_district.py

Diagnoses and repairs a quarterly-snapshot merge defect in IV_panel.csv:
`neighbourhood_cleansed` (and the co-located `latitude`/`longitude`) are
missing for 746 of 3,614 listing-quarter rows (20.6%), even though a
listing's physical location cannot change across quarters. For 285 of
401 listings (71%), the same listing has a known district in some
quarters and a missing district in others -- the signature of a failed
join against a subset of Inside Airbnb's quarterly snapshot files,
not genuine non-response.

This script:
  1. Quantifies the defect (before/after diagnostics -> results/district_repair_diagnostics.csv)
  2. Repairs it via within-listing forward/backward fill (location is
     time-invariant, so this is a lossless recovery, not imputation)
  3. Recomputes `platform_activity_loo` (leave-one-out log review volume
     within district-quarter), which depends on the corrected district
  4. Writes data/panel_fixed.csv for all downstream scripts

IMPORTANT: `sem_distance` and `sem_std` are NOT recomputed here. An
independent attempt to reconstruct sem_distance from the raw
embedding columns (review_embed_*_qtr, listing_embed_*) produced
values essentially uncorrelated with the original column (r = -0.009),
indicating the original normalization/aggregation procedure could not
be reverse-engineered from the released panel alone. The original
sem_distance / sem_std / delta columns are therefore used as-is,
including their pre-existing (district-independent) missingness.
"""
import pandas as pd
import numpy as np
from pathlib import Path

RAW_PATH = Path(__file__).resolve().parents[1] / "data" / "IV_panel.csv"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "panel_fixed.csv"
DIAG_PATH = Path(__file__).resolve().parents[1] / "results" / "district_repair_diagnostics.csv"

Q_ORDER = ['2021Q1','2021Q2','2021Q3','2021Q4','2022Q1','2022Q2','2022Q3','2022Q4',
           '2023Q1','2023Q2','2023Q3','2023Q4','2024Q1','2024Q2','2024Q3','2024Q4',
           '2025Q1','2025Q2']
TOURIST_CORE = {'Yau Tsim Mong', 'Wan Chai', 'Central & Western'}


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_PATH)
    df['q_idx'] = df['period_qtr'].map({q: i for i, q in enumerate(Q_ORDER)})
    return df.sort_values(['listing_id', 'q_idx']).reset_index(drop=True)


def diagnose(df: pd.DataFrame) -> dict:
    n_null = df['neighbourhood_cleansed'].isna().sum()
    n_districts = df['neighbourhood_cleansed'].nunique()
    per_listing_nonnull = df.groupby('listing_id')['neighbourhood_cleansed'].apply(lambda s: s.notna().sum())
    per_listing_total = df.groupby('listing_id')['neighbourhood_cleansed'].size()
    mixed = ((per_listing_nonnull > 0) & (per_listing_nonnull < per_listing_total)).sum()
    return {
        'stage': 'before_fix',
        'n_rows': len(df),
        'n_listings': df['listing_id'].nunique(),
        'n_district_null_rows': int(n_null),
        'pct_district_null': round(100 * n_null / len(df), 1),
        'n_distinct_districts_observed': int(n_districts),
        'n_listings_with_inconsistent_district_across_quarters': int(mixed),
        'n_quarters_in_panel': df['period_qtr'].nunique(),
    }


def repair(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ['neighbourhood_cleansed', 'latitude', 'longitude']:
        df[col] = df.groupby('listing_id')[col].transform(lambda s: s.ffill().bfill())
    n_before = len(df)
    df = df[df['neighbourhood_cleansed'].notna()].copy()
    n_dropped = n_before - len(df)
    if n_dropped:
        print(f"  dropped {n_dropped} rows: listing never has a recoverable district in any quarter")
    return df


def add_platform_activity(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    grp_total = df.groupby(['neighbourhood_cleansed', 'period_qtr'])['n_reviews_qtr'].transform('sum')
    df['platform_activity_loo'] = np.log1p(grp_total - df['n_reviews_qtr'].fillna(0))
    df['is_tourist'] = df['neighbourhood_cleansed'].isin(TOURIST_CORE).astype(int)
    return df


def main():
    df = load_raw()
    before = diagnose(df)

    fixed = repair(df)
    fixed = add_platform_activity(fixed)

    after = {
        'stage': 'after_fix',
        'n_rows': len(fixed),
        'n_listings': fixed['listing_id'].nunique(),
        'n_district_null_rows': int(fixed['neighbourhood_cleansed'].isna().sum()),
        'pct_district_null': 0.0,
        'n_distinct_districts_observed': int(fixed['neighbourhood_cleansed'].nunique()),
        'n_listings_with_inconsistent_district_across_quarters': 0,
        'n_quarters_in_panel': fixed['period_qtr'].nunique(),
    }

    diag = pd.DataFrame([before, after])
    DIAG_PATH.parent.mkdir(parents=True, exist_ok=True)
    diag.to_csv(DIAG_PATH, index=False)
    print(diag.to_string(index=False))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fixed.to_csv(OUT_PATH, index=False)
    print(f"\nWrote repaired panel -> {OUT_PATH}  ({len(fixed)} rows, {fixed['neighbourhood_cleansed'].nunique()} districts)")

    # district-level coverage table used by 05_make_figures.py
    cov = df.groupby('neighbourhood_cleansed', dropna=False).size().rename('n_rows_raw')
    cov.index = cov.index.fillna('(missing / unmerged)')
    cov_fixed = fixed.groupby('neighbourhood_cleansed').size().rename('n_rows_fixed')
    cov_table = pd.concat([cov, cov_fixed], axis=1).fillna(0).astype(int).sort_values('n_rows_fixed', ascending=False)
    cov_table.to_csv(Path(__file__).resolve().parents[1] / "results" / "district_coverage_before_after.csv")


if __name__ == "__main__":
    main()
