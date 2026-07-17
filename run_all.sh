#!/usr/bin/env bash
# run_all.sh
#
# Runs the full re-audit pipeline end-to-end, in order. Each step reads
# only from data/ and results/ (no hidden state, no manual editing of
# outputs). Re-running this script after any change to src/*.py will
# regenerate every file under results/ and figures/ from scratch.
#
# Usage:
#   bash run_all.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

mkdir -p results figures

echo "============================================================"
echo "[1/5] Diagnosing and repairing the district merge defect..."
echo "============================================================"
python src/01_fix_district.py

echo
echo "============================================================"
echo "[2/5] H1: representational fit/variability -> lifetime (OLS)"
echo "============================================================"
python src/02_h1_lifetime_ols.py

echo
echo "============================================================"
echo "[3/5] H2: momentum -> exit risk, 2-8Q window sweep (logit)"
echo "============================================================"
python src/03_h2_momentum_logit.py

echo
echo "============================================================"
echo "[4/5] H3: spatial subgroup extension + split sensitivity"
echo "============================================================"
python src/04_h3_spatial_subgroup.py

echo
echo "============================================================"
echo "[5/5] Generating figures..."
echo "============================================================"
python src/05_make_figures.py

echo
echo "============================================================"
echo "Done. Outputs:"
echo "  results/  -- all CSV output (7 files)"
echo "  figures/  -- 4 grayscale PNGs, 300 dpi"
echo "============================================================"