# Results

All numbers below are produced by the scripts in this repo (`./run_all.sh`) and stored in `results/`.
Figures are in `figures/results/` (model results) and `figures/proposal/` (problem and data figures).
Figure titles carry no numbers; number them in the report captions.

**Integrity of the test.** The model choice, features and search space were frozen and committed
(commit `9e5fc5e`, record in `results/freeze.json`) before week 6 was ever loaded. Week 6 was then
evaluated once. Choices were not revisited after seeing the test results.

## 1. Accuracy on the sealed test week (RQ1, RQ2)

Train A/C on CLEMD weeks 4–5 and lighting on weeks 2–5, test on week 6 (19–24 Oct 2023, 8,591 minutes).
95% CIs use a block bootstrap that resamples whole days (6 days, 2,000 resamples).
Peak windows = top 5% of 15-min building demand in the test week (29 windows, ≥ 61.9 kW).

**A/C (primary target, average 6.5 kW)** — `results/test_metrics.csv`

| Model | MAE kW [95% CI] | RMSE | R² | Peak-window MAE kW [95% CI] | Energy-share error (pp) |
|---|---|---|---|---|---|
| Time-of-day average | 2.26 [1.29, 3.25] | 4.28 | 0.80 | 6.54 [3.41, 7.92] | −2.6 |
| Ridge | 1.56 [1.19, 1.91] | 2.35 | 0.94 | 1.95 [0.93, 2.15] | +2.3 |
| Random Forest | 1.25 [0.61, 1.88] | 2.47 | 0.93 | 2.11 [1.72, 4.73] | −1.1 |
| XGBoost | 1.33 [0.61, 2.01] | 2.55 | 0.93 | 1.92 [1.26, 5.21] | −0.3 |
| **LightGBM (frozen)** | **1.24 [0.57, 1.88]** | 2.57 | 0.93 | **1.52 [1.11, 5.13]** | −0.9 |

- The frozen LightGBM model has the lowest MAE and peak-window MAE, cutting typical error by 45% against
  the timetable baseline and 21% against Ridge, and getting the A/C share of energy within 1 percentage point.
- It does **not** dominate Ridge everywhere: Ridge has a lower RMSE (fewer large misses) and tighter
  CIs, and the CIs overlap. With 6 test days the honest claim is "tree models are better on typical error
  and at the peak point estimate, Ridge is competitive"; the gap is not statistically decisive.
- Where it errs (`results/error_breakdown_ac.csv`, `figures/results/test_error_by_hour.png`):
  weekends 0.15 kW vs weekdays 1.78 kW; error rises at 08:00–14:00 when A/C ramps; minutes with a
  > 5 kW step change have 3.5 kW error vs 1.2 kW otherwise (switching, logger misalignment);
  error is worst at 30–60 kW building load (4.3–4.7 kW), exactly the ambiguous band shown in proposal Figure 8.
- **Robustness (train week 4 → test week 5)** — `results/robustness_w4_to_w5.csv`: tree models hold up
  (MAE 1.16–1.18 kW, LightGBM peak-window MAE 1.04 kW) while Ridge degrades to 2.81 kW. Trained on
  less data, linear models drift more.

**Lighting & sockets (secondary target, average 3.1 kW)**

| Model | MAE kW | Peak-window MAE kW | Energy-share error (pp) |
|---|---|---|---|
| Time-of-day average | 0.51 | 1.78 | −1.9 |
| **Ridge (frozen)** | 0.64 | 1.05 | −3.0 |
| Random Forest | **0.42** | 1.28 | −1.7 |

- **Negative finding, reported as is:** Ridge won cross-validation (MAE 0.36) but is the *worst* model on
  typical error in the test week, under-estimating lighting by 3 pp of building energy. It is still the best at
  peak windows. Lighting is a small, flat load (~15% of energy) that the main meter barely "sees"; its
  signal drifts between September and October weeks. The frozen choice is kept; the report should say
  lighting disaggregation from the main meter alone is not reliable with this data.

## 2. What the A/C model relies on (RQ3) — `explain.py`

| Feature group | Mean \|SHAP\| (kW) | Permutation: MAE rise when shuffled (kW) |
|---|---|---|
| Power (real/reactive/apparent, per phase) | 4.97 | 3.93 |
| Harmonics (odd harmonics + ratios to fundamental) | 1.20 | 2.11 |
| Power quality (PF, THD, voltage, current) | 0.60 | 0.42 |
| Calendar | 0.44 | 0.19 |
| Temporal (lags, rolling) | 0.26 | 0.42 |

- The single strongest feature is **phase-2 real power** (mean |SHAP| 3.98 kW). Phase 2 carries the least
  non-A/C load (5.6 kW mean vs 8.5 / 6.3 kW on phases 1 / 3), so its swings are mostly A/C; it also has the
  highest correlation with A/C (r = 0.946).
- The next features are the **5th, 7th and 11th current harmonics** and THD. Inverter-driven VRF
  compressors draw distorted current with exactly these harmonics, so the model is using a physically
  meaningful A/C signature, not just "the building is busy". SHAP and permutation importance agree on the
  ranking of the top two groups.
- Calendar features matter little: the model reads A/C from electrical signals, not from the timetable,
  which is why it handles light weekdays the time-of-day baseline gets wrong.
- Local explanation of the week's peak (Thu 19 Oct 16:00, building 71.4 kW): estimated A/C 28.9 kW vs
  measured 30.4 kW; phase-2 power contributes +12.4 kW above the 5.9 kW baseline, 5th harmonics and THD add
  ~+3 kW (`figures/results/shap_local_peak.png`).

## 2b. Feature-group ablation (dev weeks only) — `ablation.py`, `results/ablation_cv.csv`

Frozen LightGBM settings, same 4 CV folds on weeks 4–5, only the inputs change. Test week not used.

| Feature set | n | CV MAE kW | vs all | CV peak MAE kW |
|---|---|---|---|---|
| All (frozen) | 98 | 0.99 | — | 2.59 |
| Without harmonics | 45 | 1.20 | +21% | 2.30 |
| Without power quality | 82 | 0.99 | +0.3% | 2.82 |
| Without temporal | 89 | 0.98 | −1.2% | 2.85 |
| Without calendar | 93 | 1.05 | +6.5% | 4.35 |
| Duplicates removed | 73 | 1.01 | +2.4% | 3.15 |
| Power meter, no harmonics/PQ | 29 | 1.69 | +71% | 4.11 |
| kW-only meter | 18 | 2.01 | +104% | 4.93 |
| Calendar only | 5 | 3.05 | +209% | 6.55 |

Harmonics carry the most unique information; duplicates can go at no cost; a kW-only meter doubles the error
but still beats the timetable baseline (CV 2.99) by 33%.

## 3. Operating modes and after-hours use (RQ4) — `cluster.py`

k-means on normalised 24-h building profiles (main meter only, 28 full days, weeks 2–6).
Silhouette picks **k = 2** (0.74; k = 3: 0.61).

| Mode | Days | Weekdays | Building kWh/day | A/C after-hours kWh/day (measured / estimated) | Lighting after-hours kWh/day |
|---|---|---|---|---|---|
| 0: working day | 16 | 16 | 561 | 26.4 / 32.6 | 33.4 |
| 1: non-working day | 12 | 2 | 268 | 31.7 / 40.2 | 46.1 |

- The two "weekdays" in the non-working mode are Fri 22 Sep and **Thu 28 Sep 2023, which appears to be the
  Maulidur Rasul public holiday** (cite the official 2023 holiday list in the report). The main meter alone identifies non-working days.
- Sensitivity, k = 3: a third "light day" mode (375 kWh/day) contains Fri 22 Sep, Mon 25 Sep and Fri 29 Sep,
  the days around that holiday, matching the proposal's expectation of light days.
- Non-working days still use ~32 kWh of A/C and ~46 kWh of lighting/sockets per day. Overnight (00–06) A/C
  averages ~1.3 kW measured. This is the after-hours target.
- The model over-estimates after-hours A/C by 10–27% (week 6: 30.6 vs 27.7 kWh/day; per mode above),
  so the after-hours savings below are somewhat optimistic.

## 4. UTP scenarios (RQ5) — `scenarios.py`, `results/scenarios.json`

**Scenarios for one CLEMD-sized building, built only from main-meter A/C estimates on unseen weeks
(2, 3, 6; 20 days). Not UTP measurements.** Week 6 is checked against the sub-meter.

**Peak drivers.** In the test week's top-5% windows the model estimates A/C at **44.0%** of building
load vs **45.4% measured**; lighting 8.3% vs 9.6%. All peak windows are weekday 08:00–17:00.
The main meter alone is enough to tell facilities that A/C sets the peak.

**Peak shaving (demand-triggered A/C trim, peak recomputed after shaving).** When building demand
≥ 53.1 kW, trim A/C by x%:

| Trim | Max-demand cut (kW) | Week 6: estimated / measured A/C | RM per month (RM 89.27–97.06/kW) | RM per year |
|---|---|---|---|---|
| 10% | 2.9 | 2.9 / 3.0 | 258–280 | 3,100–3,400 |
| 20% | 5.8 | 5.8 / 6.1 | 516–561 | 6,200–6,700 |
| 30% | 8.7 | 8.7 / 8.1 | 774–841 | 9,300–10,100 |

The model-based cut matches the cut computed from the real sub-meter within 0.6 kW.

**Solar timing and pre-cooling: the proposal's idea does not hold.**
- 77% of estimated A/C energy falls in UTP's PV hours (08:00–18:00). A/C is already a daytime load.
- Solar at 14:00–16:00 is still 89% of its 11:00–13:00 level, so the afternoon A/C peak is *not*
  happening while solar is "falling away", as the proposal assumed.
- Moving 20% of 14:00–16:00 A/C into 11:00–13:00 **raises** the maximum by 5.2 kW (measured A/C: 5.4 kW),
  because the building is already near peak at midday and daily peaks fall anywhere from 11:00 to 16:59.
  The best window (08:00–10:00, only 35% of peak sun) gives 0 kW cut on the period maximum
  (1.2 kW if the late window is widened to 14:00–17:00).
- **Recommendation changes:** use a demand-triggered A/C trim (above), not fixed-time pre-cooling.
  Rooftop PV already overlaps A/C well; the gain is in limiting the peak, not shifting it.

**After-hours savings → carbon.** Cut after-hours A/C by 50% and lighting by 30%:

| Office hours | A/C after-hours kWh/day (est.) | Lighting after-hours kWh/day | Saved kWh/yr | tCO₂e/yr (0.740 t/MWh) | % of UTP Scope 2 |
|---|---|---|---|---|---|
| 08–17 | 30.8 | 33.1 | 9,243 | 6.8 | 0.034% |
| 08–18 | 27.9 | 31.3 | 8,528 | 6.3 | 0.031% |
| 07–19 | 25.0 | 28.4 | 7,675 | 5.7 | 0.028% |

Per building the carbon effect is small (≈ 6 tCO₂e/yr); the value is that it needs no new hardware and
repeats across every metered building. Annualising 20 days of Sep–Oct data is indicative only.

## 5. Limitations to state in the report

- One building, ~3 weeks of A/C ground truth, one season; 6 test days means wide CIs.
- The CLEMD building has rooftop VRF units; UTP is largely on district cooling, so the trained model does
  not transfer. The method does.
- Lighting estimation from the main meter is unreliable (Section 1).
- Scenario inputs: TNB rates from secondary sources, provisional emission factor, assumed PV performance
  ratio (0.75–0.80 → 4.2–4.5 MW mean peak), office-hours definition (sensitivity shown).
- Not done (proposal stretch goals): the 1-D CNN and the 15-minute-ahead forecasting extension, and the
  optional NASA temperature feature. These were marked optional and dropped first.

## Figure index (`figures/results/`)

| File | Shows |
|---|---|
| `test_week_timeseries.png` | Estimated vs measured A/C over the test week |
| `test_pred_vs_actual.png` | Scatter, peak windows highlighted |
| `test_error_by_hour.png` | Error by hour, weekday vs weekend |
| `shap_global_top15.png`, `shap_beeswarm.png` | Global SHAP |
| `importance_by_group.png` | SHAP and permutation importance by feature group |
| `shap_local_peak.png` | Why the model estimates A/C at the week's peak |
| `cluster_profiles.png` | Daily operating modes and the mode of each day |
| `scenario_peak_drivers.png` | A/C share of peak: estimated vs measured |
| `scenario_precooling.png` | Pre-cooling scenario on the peak weekday |
