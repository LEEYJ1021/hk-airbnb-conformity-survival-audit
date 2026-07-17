"""
03_h2_momentum_logit.py

H2a/H2b: cumulative representational momentum (convergence = "recovery",
divergence = "deterioration") and quarterly exit risk, estimated via
discrete-time logit on each listing's first observation spell.

Because rolling-window momentum requires W consecutive non-missing
quarters and `sem_distance` itself has genuine (pre-existing, not
district-bug-related) missingness, effective sample size shrinks
sharply as the window widens. This script estimates the model at
W = 2, 3, 4, 5, 6, 8 quarters and writes the full sensitivity table to
results/h2_momentum_by_window.csv -- a single window is not privileged
a priori.

Standard errors are cluster-robust at the listing level. A linear
quarter-index trend (q_idx) is used in place of full quarter fixed
effects: with full quarter dummies, W=6 and W=8 fail to converge
(quasi-separation) given the small number of events remaining at
those windows. This is disclosed rather than silently worked around.
"""
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = ROOT / "data" / "panel_fixed.csv"
OUT_PATH = ROOT / "results" / "h2_momentum_by_window.csv"

Q_ORDER = ['2021Q1','2021Q2','2021Q3','2021Q4','2022Q1','2022Q2','2022Q3','2022Q4',
           '2023Q1','2023Q2','2023Q3','2023Q4','2024Q1','2024Q2','2024Q3','2024Q4',
           '2025Q1','2025Q2']
TERMINAL_Q_IDX = len(Q_ORDER) - 1
WINDOWS = [2, 3, 4, 5, 6, 8]


def assign_first_spell(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(['listing_id', 'q_idx']).reset_index(drop=True)
    same_listing = df['listing_id'] == df['listing_id'].shift(1)
    gap = df['q_idx'] - df['q_idx'].shift(1)
    new_spell = ~(same_listing & (gap == 1))
    df['spell_id'] = new_spell.cumsum()
    first_spell_id = df.groupby('listing_id')['spell_id'].transform('min')
    df['is_first_spell'] = df['spell_id'] == first_spell_id
    fs = df[df['is_first_spell']].copy()
    return fs


def build_exit_panel(fs: pd.DataFrame) -> pd.DataFrame:
    fs = fs.sort_values(['listing_id', 'q_idx']).copy()
    fs['delta_sem'] = fs.groupby('listing_id')['sem_distance'].diff()
    fs['pos_step'] = (-fs['delta_sem']).clip(lower=0)   # convergence
    fs['neg_step'] = (fs['delta_sem']).clip(lower=0)    # divergence

    is_last = fs.groupby('listing_id')['q_idx'].transform('max') == fs['q_idx']
    max_q_overall = fs.groupby('listing_id')['q_idx'].transform('max')
    censored = (max_q_overall == TERMINAL_Q_IDX).astype(int)
    fs['exit_next'] = np.where(is_last & (censored == 0), 1, 0)

    # exclude terminal-quarter rows: exit cannot be observed (right-censored by construction)
    panel = fs[fs['q_idx'] < TERMINAL_Q_IDX].copy()
    return panel


def run_window(panel: pd.DataFrame, W: int) -> dict:
    p = panel.sort_values(['listing_id', 'q_idx']).copy()
    p['pos_mom_raw'] = p.groupby('listing_id')['pos_step'].transform(
        lambda s: s.rolling(W, min_periods=W).sum())
    p['neg_mom_raw'] = p.groupby('listing_id')['neg_step'].transform(
        lambda s: s.rolling(W, min_periods=W).sum())
    p['pos_mom_lag'] = p.groupby('listing_id')['pos_mom_raw'].shift(1)
    p['neg_mom_lag'] = p.groupby('listing_id')['neg_mom_raw'].shift(1)

    v = p.dropna(subset=['pos_mom_lag', 'neg_mom_lag', 'platform_activity_loo',
                          'n_reviews_qtr', 'sentiment_mean_qtr']).copy()
    if len(v) < 30 or v['exit_next'].sum() < 5:
        return {'window_q': W, 'N': len(v), 'events': int(v['exit_next'].sum()), 'status': 'insufficient_events'}

    v['pos_z'] = (v['pos_mom_lag'] - v['pos_mom_lag'].mean()) / v['pos_mom_lag'].std()
    v['neg_z'] = (v['neg_mom_lag'] - v['neg_mom_lag'].mean()) / v['neg_mom_lag'].std()

    formula = "exit_next ~ pos_z + neg_z + platform_activity_loo + n_reviews_qtr + sentiment_mean_qtr + q_idx"
    try:
        m = smf.logit(formula, data=v).fit(disp=0, cov_type='cluster',
                                            cov_kwds={'groups': v['listing_id']})
        return {
            'window_q': W, 'N': len(v), 'events': int(v['exit_next'].sum()),
            'status': 'ok',
            'pos_beta': m.params['pos_z'], 'pos_se': m.bse['pos_z'], 'pos_p': m.pvalues['pos_z'],
            'pos_OR': np.exp(m.params['pos_z']),
            'pos_OR_lo': np.exp(m.params['pos_z'] - 1.96 * m.bse['pos_z']),
            'pos_OR_hi': np.exp(m.params['pos_z'] + 1.96 * m.bse['pos_z']),
            'neg_beta': m.params['neg_z'], 'neg_se': m.bse['neg_z'], 'neg_p': m.pvalues['neg_z'],
            'neg_OR': np.exp(m.params['neg_z']),
            'neg_OR_lo': np.exp(m.params['neg_z'] - 1.96 * m.bse['neg_z']),
            'neg_OR_hi': np.exp(m.params['neg_z'] + 1.96 * m.bse['neg_z']),
        }
    except Exception as e:
        return {'window_q': W, 'N': len(v), 'events': int(v['exit_next'].sum()),
                'status': f'failed: {e}'}


def main():
    df = pd.read_csv(PANEL_PATH)
    df['q_idx'] = df['period_qtr'].map({q: i for i, q in enumerate(Q_ORDER)})

    fs = assign_first_spell(df)
    panel = build_exit_panel(fs)

    rows = [run_window(panel, W) for W in WINDOWS]
    results = pd.DataFrame(rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_PATH, index=False)

    print(results.to_string(index=False))
    print(f"\nWrote -> {OUT_PATH}")


if __name__ == "__main__":
    main()
