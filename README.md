# A/C and Lighting Load Disaggregation (TEB3123 Machine Learning, Group 8)

Estimates a building's air-conditioning and lighting power from its main meter alone, using the public
[CLEMD dataset](https://doi.org/10.1038/s41597-024-03433-7), then turns the estimates into peak-demand,
solar-timing and tCO₂e scenarios for UTP (Energy Security, SDG 7).

## Setup

```bash
uv venv .venv && uv pip install -r requirements.txt     # or: python -m venv .venv && pip install -r requirements.txt
```

The data is not in git (≈7 GB). Put it in `data/` (or symlink `data -> ../data`):

```
data/clemd/<six weekly folders from figshare>/*.csv    https://doi.org/10.6084/m9.figshare.c.6946581
data/external/nasa_power_utp_oct2023_utc.csv           NASA POWER hourly, UTP (4.385 N, 100.979 E), Oct 2023
```

## Pipeline

| Step | Script | Output |
|---|---|---|
| 1. Clean + resample 1 s → 1 min (weeks 2–6) | `prepare_data.py` | `data/processed/clemd_1min.parquet` |
| 2. Feature dictionary + redundancy check | `features.py` | `results/feature_dictionary.csv`, `results/redundant_feature_pairs.csv` |
| 3. Baselines + RF/XGBoost/LightGBM, time-series CV, **model freeze** | `train.py` | `results/cv_results.csv`, `results/freeze.json` |
| Proposal figures | `make_figures.py` | `figures/proposal/` |

Run each with `.venv/bin/python <script>`. Every script reads the parquet, so step 1 runs once (~40 s).

## Rules we follow

- **Week 6 is the sealed test week.** Nothing before the freeze loads it (`features.load()` drops it by default).
- Train A/C on weeks 4–5, lighting on weeks 2–5. Chronological split only; lags never cross a data gap.
- After `freeze.json` is committed, the model, features and search space don't change.
