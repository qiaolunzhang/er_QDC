"""Reproduce Table II: linear regression results for nu_mk estimation.

Train: 4 circuit types x w in [10,30] (84 circuits). Test: w in [31,40] (40).
Output: results/table2_regression.csv + console comparison against paper values.

Run from repo root:  python -m experiments.run_table2_regression
"""

import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from qdc_scheduler.regression import fit_all

PAPER = {  # k: (chi0, chi1, chi2, chi3, R2_test, RMSE_test)
    2: (0.0272, 0.4345, 0.0163, 0.0434, 0.995, 0.0175),
    3: (0.1185, 0.4808, 0.0534, 0.0802, 0.986, 0.0369),
    4: (0.1887, 0.4585, 0.081, 0.1235, 0.973, 0.055),
    5: (0.2842, 0.3836, 0.119, 0.162, 0.953, 0.075),
    6: (0.368, 0.3, 0.152, 0.0203, 0.925, 0.096),
}


def main():
    models = fit_all()
    os.makedirs("results", exist_ok=True)
    rows = []
    hdr = f"{'k':>2} | {'chi0':>8} {'chi1':>8} {'chi2':>8} {'chi3':>8} {'R2':>7} {'RMSE':>7}"
    print(hdr + "   (first line: ours, second: paper)")
    print("-" * len(hdr))
    for k, m in models.items():
        ours = (m.chi[0], m.chi[1], m.chi[2], m.chi3, m.r2_test, m.rmse_test)
        rows.append([k, *[f"{v:.4f}" for v in ours]])
        print(f"{k:>2} | " + " ".join(f"{v:8.4f}" for v in ours[:4])
              + f" {ours[4]:7.3f} {ours[5]:7.4f}")
        p = PAPER[k]
        print(f"   | " + " ".join(f"{v:8.4f}" for v in p[:4])
              + f" {p[4]:7.3f} {p[5]:7.4f}")
    with open("results/table2_regression.csv", "w", newline="") as f:
        wcsv = csv.writer(f)
        wcsv.writerow(["k", "chi0", "chi1", "chi2", "chi3", "R2_test", "RMSE_test"])
        wcsv.writerows(rows)
    print("\nSaved results/table2_regression.csv")


if __name__ == "__main__":
    main()
