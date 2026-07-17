"""
04_h3_spatial_subgroup.py

H3a/H3b: re-estimates the H1 OLS specification separately for
tourist-core districts (Yau Tsim Mong, Wan Chai, Central & Western)
and the remaining ("stable-market") districts, using the CORRECTED
district assignment from 01_fix_district.py.

Also reconstructs, for comparison, what the tourist/non-tourist split
looks like under two alternative (uncorrected) district-assignment
rules, to show that the subgroup composition -- and the significance
of the subgroup results -- is highly sensitive to how the district
merge defect is handled. Writes results/h3_subgroup_results.csv and
results/h3_split_comparison.csv.
"""
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
H1_SAMPLE_PATH = ROOT / "results" / "h1_analysis_sample.csv"
RAW_PANEL_PATH = ROOT / "data" / "IV_panel.csv"
OUT_RESULTS = ROOT / "results" / "h3_subgroup_results.csv"
OUT_SPLIT = ROOT / "results" / "h3_split_comparison.csv"

Q_ORDER = ['2021Q1','2021Q2','2021Q3','2021Q4','2022Q1','2022Q2','2022Q3','2022Q4',
           '2023Q1','2023Q2','2023Q3','2023Q4','2024Q1','2024Q2','2024Q3','2024Q4',
           '2025Q1','2025Q2']
TOURIST_CORE = {'Yau Tsim Mong', 'Wan Chai', 'Central & Western'}
CONTROLS = "activity_init + reviews_pq + price_log + superhost + amenity_count + sentiment"


def run_subgroup(sub: pd.DataFrame, label: str) -> list:
    rows = []
    formula = f"lifetime ~ fit_init + variability_init + {CONTROLS} + C(entry_q)"
    try:
        m = smf.ols(formula, data=sub).fit(cov_type='HC1')
        for var in ['fit_init', 'variability_init']:
            rows.append({
                'subgroup': label, 'term': var,
                'beta': m.params[var], 'se': m.bse[var], 'p': m.pvalues[var],
                'N': int(m.nobs), 'R2': m.rsquared,
            })
    except Exception as e:
        rows.append({'subgroup': label, 'term': 'FAILED', 'beta': np.nan, 'se': np.nan,
                      'p': np.nan, 'N': len(sub), 'R2': np.nan})
    return rows


def main():
    h1 = pd.read_csv(H1_SAMPLE_PATH)

    # --- main H3 subgroup results using corrected district ---
    all_rows = []
    all_rows += run_subgroup(h1[h1.is_tourist == 1], "tourist_core (corrected)")
    all_rows += run_subgroup(h1[h1.is_tourist == 0], "non_tourist (corrected)")

    h1c = h1.copy()
    h1c['fit_x_tourist'] = h1c['fit_init'] * h1c['is_tourist']
    h1c['var_x_tourist'] = h1c['variability_init'] * h1c['is_tourist']
    formula_int = (f"lifetime ~ fit_init + variability_init + fit_x_tourist + var_x_tourist "
                   f"+ is_tourist + {CONTROLS} + C(entry_q)")
    m = smf.ols(formula_int, data=h1c).fit(cov_type='HC1')
    for var in ['fit_init', 'variability_init', 'fit_x_tourist', 'var_x_tourist']:
        all_rows.append({'subgroup': 'full_sample_interaction (corrected)', 'term': var,
                          'beta': m.params[var], 'se': m.bse[var], 'p': m.pvalues[var],
                          'N': int(m.nobs), 'R2': m.rsquared})

    results = pd.DataFrame(all_rows)
    results.to_csv(OUT_RESULTS, index=False)
    print("=== H3 subgroup results (corrected district) ===")
    print(results.to_string(index=False))

    # --- diagnostic: how sensitive is the tourist/non-tourist split to district-fix method? ---
    raw = pd.read_csv(RAW_PANEL_PATH)
    raw['q_idx'] = raw['period_qtr'].map({q: i for i, q in enumerate(Q_ORDER)})
    raw = raw.sort_values(['listing_id', 'q_idx'])
    raw_valid = raw[raw['neighbourhood_cleansed'].notna()].copy()
    raw_valid['rnk'] = raw_valid.groupby('listing_id').cumcount()
    early_raw = raw_valid[raw_valid['rnk'] < 4]
    split_raw = early_raw.groupby('listing_id')['neighbourhood_cleansed'].agg(
        lambda s: 1 if s.mode().iloc[0] in TOURIST_CORE else 0)

    split_comparison = pd.DataFrame([
        {'method': 'as reported in paper (unverifiable)', 'tourist_core_n': 188, 'non_tourist_n': 129},
        {'method': 'raw district, no repair (early window, non-null only)',
         'tourist_core_n': int((split_raw == 1).sum()), 'non_tourist_n': int((split_raw == 0).sum())},
        {'method': 'repaired district (this pipeline, full H1 covariate sample)',
         'tourist_core_n': int((h1.is_tourist == 1).sum()), 'non_tourist_n': int((h1.is_tourist == 0).sum())},
    ])
    split_comparison.to_csv(OUT_SPLIT, index=False)
    print("\n=== Tourist/non-tourist split under different district-handling methods ===")
    print(split_comparison.to_string(index=False))
    print(f"\nWrote -> {OUT_RESULTS}\nWrote -> {OUT_SPLIT}")


if __name__ == "__main__":
    main()
