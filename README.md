<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="5_scenarios_dashboard/figures/readme/hero-dark.png">
  <img src="5_scenarios_dashboard/figures/readme/hero-light.png" alt="Who sets the peak? The presentation walkthrough, opening on one week of building demand" width="900">
</picture>

# Who sets the peak?

**A building's air-conditioning and lighting load, estimated from its main meter alone.**

Then turned into peak-demand, cost and carbon decisions for Universiti Teknologi PETRONAS.

![Course](https://img.shields.io/badge/course-TEB3123%20Machine%20Learning-0b1420?style=flat-square)
![Group](https://img.shields.io/badge/group-8%20%C2%B7%20Lecture%20Group%202-1f6fd1?style=flat-square)
![SDG](https://img.shields.io/badge/UTP%20Grand%20Challenge-Energy%20Security%20%C2%B7%20SDG%207-f5a700?style=flat-square)
![Test MAE](https://img.shields.io/badge/sealed--week%20A%2FC%20MAE-1.24%20kW-179c6c?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-8590a0?style=flat-square)

**built with**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-3.1-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-2.4-013243?style=flat-square&logo=numpy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![LightGBM](https://img.shields.io/badge/LightGBM-4.7-02569B?style=flat-square)
![XGBoost](https://img.shields.io/badge/XGBoost-3.2-189fdd?style=flat-square)
![SHAP](https://img.shields.io/badge/SHAP-0.51-ff0d57?style=flat-square)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.11-11557c?style=flat-square)

[Results](#headline-results) · [Quick start](#quick-start) · [Pipeline](#pipeline) · [Team](#team)

</div>

---

## The problem in one picture

Every UTP building has a main meter, but it only shows the **total**. The monthly TNB demand charge (about RM 89–97 per kW) is set by the single worst 15 minutes, and nobody can see which load caused it. In the CLEMD building, A/C is **30% of the energy but 43% of the peak**, and every peak falls in weekday office hours.

```mermaid
flowchart LR
    M["🔌 Main meter<br/>(already on UTP's i-BMS)"] --> F["98 features<br/>power · harmonics · PQ · lags · calendar"]
    F --> ML["LightGBM<br/>estimates A/C kW every minute"]
    ML --> S{"Who sets<br/>the peak?"}
    S -->|"A/C ≈ 44% of peak load"| T["Demand-triggered A/C trim<br/>at ≥ 53 kW"]
    S -->|"after-hours load"| A["After-hours schedules"]
    T --> KW["−5.8 kW maximum demand<br/>≈ RM 6.2k–6.7k / year"]
    A --> C["≈ 9 MWh · 6.8 tCO₂e / year"]
    KW --> SDG["⚡ SDG 7 · Energy Security"]
    C --> SDG
```

> All RM, kWh and tCO₂e figures are **scenarios for one CLEMD-sized building**, not UTP measurements. The numbers come from `5_scenarios_dashboard/results/scenarios.json`; the full method is in Chapter 7 of the final report.

## Headline results

<table>
<tr>
<td width="50%" valign="top">

**Who sets the peak?** Top-5% demand windows of the sealed test week, measured by sub-meters:

```mermaid
pie showData
    title Share of building load at the peak (%)
    "A/C" : 45.4
    "Lighting & sockets" : 9.6
    "Everything else" : 45.0
```

From the main meter alone, the model estimates A/C at **44.0%** (measured: 45.4%).

</td>
<td width="50%" valign="top">

**How accurate?** A/C error on the sealed test week (lower is better):

```mermaid
xychart-beta
    title "Test-week A/C error, MAE (kW)"
    x-axis ["Time of day", "Ridge", "Random forest", "XGBoost", "LightGBM"]
    y-axis "MAE (kW)" 0 --> 2.5
    bar [2.26, 1.56, 1.25, 1.33, 1.24]
```

LightGBM (frozen): **1.24 kW** on a 6.5 kW load, 45% below the timetable baseline.

</td>
</tr>
</table>

| | Result | Evidence |
|---|---|---|
| 🎯 **A/C estimate** | MAE **1.24 kW** (95% CI 0.56–1.87), peak-window MAE **1.52 kW** | `3_tree_models/results/test_metrics.csv` |
| 🔍 **Why it works** | Phase-2 power and the 5th/7th/11th harmonics of inverter compressors | `4_explainability_clustering/results/shap_groups_ac.csv` |
| 🧪 **Ablation** | Without harmonics: +21% error. kW-only meter: 2× error, still beats the timetable | `3_tree_models/results/ablation_cv.csv` |
| 📅 **Operating modes** | The main meter alone finds the Maulidur Rasul public holiday | `4_explainability_clustering/results/cluster_days.csv` |
| ❌ **Pre-cooling** | Our proposal's idea **raises** the peak by 5.2 kW, so we dropped it | `5_scenarios_dashboard/results/scenarios.json` |
| ⚠️ **Lighting** | Not reliably estimable from the main meter (reported as a negative result) | `3_tree_models/results/test_metrics.csv` |

<p align="center">
  <img src="3_tree_models/figures/test_week_timeseries.png" alt="Estimated versus measured A/C over the sealed test week" width="49%">
  <img src="5_scenarios_dashboard/figures/report/fig_model_comparison.png" alt="Test-week MAE for every model with 95% bootstrap intervals" width="49%">
</p>
<p align="center">
  <img src="4_explainability_clustering/figures/importance_by_group.png" alt="SHAP and permutation importance by feature group" width="49%">
  <img src="5_scenarios_dashboard/figures/report/fig_scenarios.png" alt="Peak-shaving and after-hours scenario results" width="49%">
</p>

## Quick start

```bash
# 1. environment (Python 3.11; versions pinned)
uv venv .venv && uv pip install -r requirements.txt   # or: python -m venv .venv && .venv/bin/pip install -r requirements.txt

# 2. run everything and open the dashboard (~13 min)
./run_all.sh

# just open the dashboard, or run only some steps
./run_all.sh ui
./run_all.sh ablation build_dashboard
```

### Data

| File | Size | Where it comes from |
|---|---|---|
| `data/clemd/<six weekly folders>/*.csv` | ≈ 5.9 GB | CLEMD on figshare: [doi.org/10.6084/m9.figshare.c.6946581](https://doi.org/10.6084/m9.figshare.c.6946581). Open the link, download each weekly dataset, extract into `data/clemd/` |
| `data/processed/clemd_1min.parquet` | 15 MB | Made by `prepare_data.py`. With this file you can run every step except 1 and 10 without the raw data |
| `data/external/nasa_power_utp_oct2023_utc.csv` | 16 KB | NASA POWER hourly irradiance, UTP (4.385 N, 100.979 E), Oct 2023 |

Without the raw CLEMD folders, run the steps that only need the parquet:

```bash
./run_all.sh features train ablation evaluate explain cluster scenarios make_figures report_figures
```

## Pipeline

```mermaid
flowchart TD
    R[("Raw CLEMD<br/>42 CSVs · 1-second rows")] --> P["1 · prepare_data.py<br/>clean, fix dates, drop outage, 1 s → 1 min"]
    P --> PQ[("clemd_1min.parquet<br/>41,680 minutes")]
    PQ --> FE["2 · features.py<br/>98 main-meter features + redundancy check"]
    FE --> TR["3 · train.py<br/>baselines + RF / XGBoost / LightGBM<br/>time-series CV"]
    TR --> FZ{{"🔒 freeze.json<br/>committed before week 6 is loaded"}}
    TR --> AB["3b · ablation.py<br/>feature-group ablation"]
    FZ --> EV["4 · evaluate.py<br/>one-time test on week 6, bootstrap CIs"]
    EV --> EX["5 · explain.py<br/>SHAP + permutation importance"]
    EV --> CL["6 · cluster.py<br/>k-means operating modes"]
    EV --> SC["7 · scenarios.py<br/>kW · RM · solar · tCO₂e"]
    EX & CL & SC & AB --> FG["8–9 · make_figures.py · report_figures.py"]
    FG --> DB["10 · build_dashboard.py<br/>5_scenarios_dashboard/dashboard/index.html"]
```

Each team member's code sits in its own folder, with the results and figures it makes next to it:

```
1_data_acquisition/          prepare_data.py                                    (Izzatul)
2_feature_engineering/       features.py + results/                             (Izzati)
3_tree_models/               train.py, ablation.py, evaluate.py + results/, figures/   (Daphne)
4_explainability_clustering/ explain.py, cluster.py + results/, figures/        (Masyitah)
5_scenarios_dashboard/       scenarios.py, make_figures.py, report_figures.py,
                             build_dashboard.py + results/, figures/, dashboard/, public/   (Sharvin)
data/                        CLEMD data (not in git)
```

`run_all.sh` puts all five folders on `PYTHONPATH`, since the scripts import from each other. To run one script on its own: `PYTHONPATH=1_data_acquisition:2_feature_engineering:3_tree_models:4_explainability_clustering:5_scenarios_dashboard .venv/bin/python 3_tree_models/train.py`, or just `./run_all.sh train`.

| Step | Script | Output |
|---|---|---|
| 1. Clean + resample 1 s → 1 min (weeks 2–6) | `1_data_acquisition/prepare_data.py` | `data/processed/clemd_1min.parquet` |
| 2. Feature dictionary + redundancy check | `2_feature_engineering/features.py` | `2_feature_engineering/results/feature_dictionary.csv`, `2_feature_engineering/results/redundant_feature_pairs.csv` |
| 3. Baselines + RF/XGBoost/LightGBM, time-series CV, **model freeze** | `3_tree_models/train.py` | `3_tree_models/results/cv_results.csv`, `3_tree_models/results/freeze.json` |
| 3b. Feature-group ablation (dev weeks only, frozen settings) | `3_tree_models/ablation.py` | `3_tree_models/results/ablation_cv.csv` |
| 4. One-time test on week 6, bootstrap CIs, robustness, error analysis | `3_tree_models/evaluate.py` | `3_tree_models/results/test_metrics.csv`, `3_tree_models/results/predictions.csv`, … |
| 5. SHAP + permutation importance | `4_explainability_clustering/explain.py` | `4_explainability_clustering/results/shap_*.csv`, `4_explainability_clustering/results/permutation_importance_groups.csv` |
| 6. k-means operating modes, after-hours energy | `4_explainability_clustering/cluster.py` | `4_explainability_clustering/results/cluster_*.csv` |
| 7. UTP scenarios (kW, RM, solar, tCO₂e) | `5_scenarios_dashboard/scenarios.py` | `5_scenarios_dashboard/results/scenarios.json` |
| 8. Problem/data figures (EDA, workflow, split) + headline stats | `5_scenarios_dashboard/make_figures.py` | `5_scenarios_dashboard/figures/proposal/` |
| 9. Extra report figures (distributions, residuals, model comparison, scenarios) | `5_scenarios_dashboard/report_figures.py` | `5_scenarios_dashboard/figures/report/` |
| 10. Presentation walkthrough + stakeholder dashboard | `5_scenarios_dashboard/build_dashboard.py` | `5_scenarios_dashboard/dashboard/index.html` |

Steps run in this order; each reads the previous step's output. Every script ends with `assert` self-checks, so a clean run with no traceback means the outputs are consistent. All randomness is seeded (`random_state=0`, `default_rng(0)`), so a rerun regenerates the same results.

### How the data is split

```mermaid
gantt
    title CLEMD weeks used for training and testing (2023)
    dateFormat YYYY-MM-DD
    axisFormat %d %b
    section Dropped
    Week 1 · no main meter            :crit, 2023-09-16, 6d
    section Lighting model
    Train · weeks 2–5                 :active, 2023-09-21, 27d
    section A/C model
    Train · weeks 4–5                 :active, 2023-10-04, 14d
    section Sealed test
    Week 6 · loaded once, after the freeze :done, 2023-10-18, 7d
```

## Rules we follow

- 🔒 **Week 6 is the sealed test week.** Nothing before the freeze loads it (`features.load()` drops it by default).
- ⏱️ **Chronological splits only.** A/C trains on weeks 4–5, lighting on weeks 2–5; lags never cross a data gap; CV leaves a 60-minute gap between train and validation.
- 📝 **The freeze rule was written down first.** A tree model is chosen only if it beats Ridge's CV error by at least 5%. After `freeze.json` is committed, the model, features and search space don't change; rerunning `train.py` writes `freeze_rerun.json` and checks the choice is reproduced.
- 🏷️ **Scenarios are labelled as scenarios.** No accuracy gain is ever turned into a claimed energy saving.

## Dashboard

<p align="center">
  <img src="5_scenarios_dashboard/figures/readme/dashboard.png" alt="Stakeholder dashboard: A/C share of peak, peak cut, demand-charge saving and after-hours savings" width="900">
</p>

`5_scenarios_dashboard/dashboard/index.html` is one offline file: an 11-step walkthrough of the project plus a stakeholder dashboard and a team page. Every chart has hover tooltips.

| Key | Action |
|---|---|
| `←` `→` | Previous / next step |
| `0`–`9` | Jump to a step |
| `D` | Stakeholder dashboard |
| `T` | Light / dark theme |

It is generated from `5_scenarios_dashboard/dashboard/template.html` and the files above; rerun `build_dashboard.py` after any result changes. Rebuilding needs the raw CLEMD folders (the data step reads a raw sample); the shipped `index.html` is already built. Team phone numbers are read from an optional `5_scenarios_dashboard/public/phones.json`, which is not included.

<p align="center">
  <img src="5_scenarios_dashboard/figures/readme/limits-loop.png" alt="Limits step with the CRISP-ML(Q) cycle: four phases done, deployment and monitoring proposed next" width="900">
</p>

## Limitations

One building, about three weeks of A/C ground truth and one season, so confidence intervals are wide. The CLEMD building uses rooftop VRF units while much of UTP is on district cooling: the **method** transfers, this trained model does not. The adoption plan has not yet been reviewed with UTP stakeholders. Full list: Section 8.1 of the final report.

## License

[MIT](LICENSE) © 2026 Sharvin A/L Kanesan and Group 8. The CLEMD dataset is CC BY 4.0 (Al-Khadher et al., *Scientific Data* 2024, [doi:10.1038/s41597-024-03433-7](https://doi.org/10.1038/s41597-024-03433-7)). Solar data from the NASA Langley Research Center POWER Project.

## Team

**Group 8 · TEB3123 Machine Learning · Lecture Group 2**

<table>
<tr>
<td align="center" width="20%"><img src="5_scenarios_dashboard/public/Izzatul.png" width="140" alt="Izzatul Najwa Binti Che Zaki"><br><b>Izzatul Najwa Binti Che Zaki</b><br><sub>22007298</sub><br><sub>Data acquisition, cleaning and quality log</sub><br><sub><a href="1_data_acquisition/"><code>1_data_acquisition/</code></a></sub></td>
<td align="center" width="20%"><img src="5_scenarios_dashboard/public/Izzati.png" width="140" alt="Nurul Izzati Binti Razali"><br><b>Nurul Izzati Binti Razali</b><br><sub>22007868</sub><br><sub>Feature engineering and baselines</sub><br><sub><a href="2_feature_engineering/"><code>2_feature_engineering/</code></a></sub></td>
<td align="center" width="20%"><img src="5_scenarios_dashboard/public/Daphne.png" width="140" alt="Daphne Binti Douglas"><br><b>Daphne Binti Douglas</b><br><sub>22006239</sub><br><sub>Tree models, tuning, freeze and test</sub><br><sub><a href="3_tree_models/"><code>3_tree_models/</code></a></sub></td>
<td align="center" width="20%"><img src="5_scenarios_dashboard/public/Masyitah.png" width="140" alt="Siti Nurmasyitah Binti Ab Aziz"><br><b>Siti Nurmasyitah Binti Ab Aziz</b><br><sub>22007601</sub><br><sub>Explainability, error analysis and clustering</sub><br><sub><a href="4_explainability_clustering/"><code>4_explainability_clustering/</code></a></sub></td>
<td align="center" width="20%"><img src="5_scenarios_dashboard/public/Sharvin.png" width="140" alt="Sharvin A/L Kanesan"><br><b>Sharvin A/L Kanesan</b><br><sub>22006930</sub><br><sub>Scenarios, figures, integration and dashboard</sub><br><sub><a href="5_scenarios_dashboard/"><code>5_scenarios_dashboard/</code></a></sub></td>
</tr>
</table>

<div align="center"><sub>Universiti Teknologi PETRONAS · September 2026</sub></div>
