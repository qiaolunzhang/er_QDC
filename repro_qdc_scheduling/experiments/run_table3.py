"""Table III: average ebits per QCirc type, M=28, PH distributor.
Columns: PH (=Pytket-PH), Single+PH, Batch+PH; each split by Sc.1/Sc.2/Sc.3.

Run:  python -m experiments.run_table3
"""

import glob
import os
import pickle
from collections import defaultdict

import numpy as np

RESULTS = os.path.join(os.path.dirname(__file__), "..", "results", "pytket")
TYPES = ["QFT", "DJ", "WState", "GHZ"]
SCHEMES = [("Pytket-PH", "PH"), ("Single+PH", "Single+PH"),
           ("Batch+PH", "Batch+PH")]

# paper Table III (M=28, PH):  scheme -> {type: [Sc1, Sc2, Sc3]}
PAPER = {
    "PH": {"QFT": [1.375, 6.01, 17.2], "DJ": [0.96, 1.93, 2.82],
           "WState": [3.39, 5.15, 5.4], "GHZ": [1.67, 2.7, 2.75]},
    "Single+PH": {"QFT": [1.04, 4.48, 13.35], "DJ": [0.47, 0.88, 1.15],
                  "WState": [1.68, 2.25, 2.39], "GHZ": [0.77, 1.15, 1.19]},
    "Batch+PH": {"QFT": [0, 2.23, 10.53], "DJ": [0.26, 0.67, 1.01],
                 "WState": [1.52, 2.1, 2.67], "GHZ": [0.82, 1.09, 1.27]},
}


def main():
    acc = defaultdict(list)
    for path in glob.glob(os.path.join(RESULTS, "*.pkl")):
        with open(path, "rb") as f:
            s = pickle.load(f)
        c = s["config"]
        if c["M"] == 28:
            acc[(c["scenario"], c["scheme"])].append(s)

    print(f"{'type':>7} {'scheme':>10} | {'Sc1 (p/r)':>14} {'Sc2 (p/r)':>14} "
          f"{'Sc3 (p/r)':>14}")
    print("-" * 70)
    for ctype in TYPES:
        for key, plabel in SCHEMES:
            row = []
            for scen in ("Sc1", "Sc2", "Sc3"):
                runs = acc.get((scen, key), [])
                ours = (np.mean([r["ebits_by_type"].get(ctype, np.nan)
                                 for r in runs]) if runs else np.nan)
                paper = PAPER[plabel][ctype][["Sc1", "Sc2", "Sc3"].index(scen)]
                row.append(f"{paper:.2f}/{ours:.2f}")
            print(f"{ctype:>7} {plabel:>10} | " + " ".join(f"{c:>14}" for c in row))


if __name__ == "__main__":
    main()
