# repro_qdc_scheduling

Reproduction of **arXiv:2409.12675v5** — *Resource Management and Circuit Scheduling for
Distributed Quantum Computing Interconnect Networks* (Bahrani, Oliveira, Parra-Ullauri,
Wang, Simeonidou — IEEE JSAC).

See `CLAUDE.md` for the quick guide and `AI_GUIDE/REPRODUCTION_TODO.md` for the full
step-by-step reproduction plan (Table II–IV, Fig. 7–11).

## Quick start

```bash
pip install -r requirements.txt
python -m pytest tests/ -q                      # unit tests
python -m experiments.run_table2_regression     # Table II
python -m experiments.run_kl_experiments        # Fig 7-9 data (long)
python plot_scripts/plot_fig7.py                # figures
```
