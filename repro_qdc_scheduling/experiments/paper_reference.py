"""Paper reference values, read bar-by-bar from 300 dpi crops of the original
figures (arXiv:2409.12675v5). Reading precision ~ +-3% of axis range.

Index convention: {metric: {(scenario, M, scheme): value}}; schemes use our
tags (RB, CAB, Single, Batch_a0.55, ...). Batch values given for alpha=0.55;
0.65/0.75 within reading error unless noted.
"""

M_VALUES = [12, 20, 28, 36]


def _expand(scen, scheme, vals):
    return {(scen, m, scheme): v for m, v in zip(M_VALUES, vals)}


EBITS = {}  # Fig. 7(a)(c)
EBITS.update(_expand("Sc1", "RB", [11.6, 9.9, 7.8, 6.6]))
EBITS.update(_expand("Sc1", "CAB", [3.35, 3.45, 2.7, 2.45]))
EBITS.update(_expand("Sc1", "Single", [2.85, 3.3, 2.3, 2.15]))
EBITS.update(_expand("Sc1", "Batch_a0.55", [0.8, 1.0, 0.9, 0.95]))
EBITS.update(_expand("Sc2", "RB", [21.1, 20.8, 17.6, 16.5]))
EBITS.update(_expand("Sc2", "CAB", [13.5, 12.4, 10.7, 9.4]))
EBITS.update(_expand("Sc2", "Single", [11.2, 10.2, 9.0, 8.1]))
EBITS.update(_expand("Sc2", "Batch_a0.55", [6.4, 7.1, 6.8, 6.0]))

PARTITIONS = {}  # Fig. 7(b)(d)
PARTITIONS.update(_expand("Sc1", "RB", [2.5, 2.3, 2.1, 2.0]))
PARTITIONS.update(_expand("Sc1", "CAB", [1.6, 1.6, 1.55, 1.55]))
PARTITIONS.update(_expand("Sc1", "Single", [1.6, 1.6, 1.55, 1.5]))
PARTITIONS.update(_expand("Sc1", "Batch_a0.55", [1.4, 1.6, 1.55, 1.45]))
PARTITIONS.update(_expand("Sc2", "RB", [2.8, 2.65, 2.5, 2.4]))
PARTITIONS.update(_expand("Sc2", "CAB", [2.0, 1.95, 1.85, 1.8]))
PARTITIONS.update(_expand("Sc2", "Single", [1.95, 1.95, 1.85, 1.8]))
PARTITIONS.update(_expand("Sc2", "Batch_a0.55", [1.7, 1.75, 1.7, 1.75]))

MAKESPAN = {}  # Fig. 9(a)(c)
MAKESPAN.update(_expand("Sc1", "CAB", [0.195, 0.302, 0.284, 0.348]))
MAKESPAN.update(_expand("Sc1", "Single", [0.18, 0.307, 0.235, 0.265]))
MAKESPAN.update(_expand("Sc1", "Batch_a0.55", [0.048, 0.073, 0.088, 0.112]))
MAKESPAN.update(_expand("Sc1", "Batch_a0.65", [0.062, 0.074, 0.093, 0.110]))
MAKESPAN.update(_expand("Sc1", "Batch_a0.75", [0.058, 0.080, 0.100, 0.120]))
MAKESPAN.update(_expand("Sc2", "CAB", [0.625, 0.73, 0.91, 0.93]))
MAKESPAN.update(_expand("Sc2", "Single", [0.55, 0.59, 0.70, 0.69]))
MAKESPAN.update(_expand("Sc2", "Batch_a0.55", [0.335, 0.49, 0.58, 0.59]))
MAKESPAN.update(_expand("Sc2", "Batch_a0.65", [0.34, 0.53, 0.58, 0.60]))
MAKESPAN.update(_expand("Sc2", "Batch_a0.75", [0.36, 0.54, 0.60, 0.63]))

JET_QFT = {}  # Fig. 8(a)(e)
JET_QFT.update(_expand("Sc1", "CAB", [0.070, 0.074, 0.058, 0.052]))
JET_QFT.update(_expand("Sc1", "Single", [0.061, 0.070, 0.045, 0.043]))
JET_QFT.update(_expand("Sc1", "Batch_a0.55", [0.018, 0.015, 0.015, 0.015]))
JET_QFT.update(_expand("Sc2", "CAB", [0.36, 0.33, 0.285, 0.24]))
JET_QFT.update(_expand("Sc2", "Single", [0.24, 0.215, 0.196, 0.17]))
JET_QFT.update(_expand("Sc2", "Batch_a0.55", [0.117, 0.13, 0.127, 0.11]))

# Fig. 10 relative improvements quoted in the text (M=36):
# Batch vs Single makespan reduction: 14.7% @0.5dB, 28.3% @1dB, 43.8% @2dB

TABLE4 = {("Single", "Sc1"): 0.0062, ("Single", "Sc2"): 0.0061,
          ("Single", "Sc3"): 0.0065, ("Batch_a0.55", "Sc1"): 3.41,
          ("Batch_a0.55", "Sc2"): 2.93, ("Batch_a0.55", "Sc3"): 4.14}
