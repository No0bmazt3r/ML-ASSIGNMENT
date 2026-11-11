# TEB3123 MACHINE LEARNING
## FINAL PROJECT REPORT

**September 2026 semester**

| | |
|---|---|
| **Project Title** | ML-Based Air-Conditioning and Lighting Load Disaggregation in Malaysian Institutional Buildings for Peak-Demand Reduction Towards UTP's Net-Zero Carbon Campus Goal |
| **Course** | TEB3123 Machine Learning, Universiti Teknologi PETRONAS |
| **Lecturer** | **[TODO: lecturer name]** |
| **Lecture Session Group** | **[TODO: Group 1 / Group 2]** |
| **Project Group No.** | 8 |
| **UTP Grand Challenge** | Energy Security |
| **Relevant SDG** | SDG 7: Affordable and Clean Energy (primary); SDG 13: Climate Action (secondary) |
| **Dataset Name / Source** | CLEMD: Circuit-Level Electrical Measurements Dataset, Al-Khadher et al., figshare, https://doi.org/10.6084/m9.figshare.c.6946581 [1] |
| **Submission Date** | 13 November 2026 |

### Group Members

| No. | Student Name | Student ID |
|---|---|---|
| 1 | IZZATUL NAJWA BINTI CHE ZAKI | 22007298 |
| 2 | NURUL IZZATI BINTI RAZALI | 22007868 |
| 3 | DAPHNE BINTI DOUGLAS | 22006239 |
| 4 | SITI NURMASYITAH BINTI AB AZIZ | 22007601 |
| 5 | SHARVIN A/L KANESAN | 22006930 |

---

## Executive Summary

Purchased electricity makes up 99.7% of UTP's Scope 1 and 2 emissions [2], and large customers pay about RM 89–97 per kW per month for their highest 15-minute demand [3], [4]. Every UTP building has a main meter on the i-BMS [5], but it cannot show which loads set the peak. This project, aligned with the **Energy Security** Grand Challenge (**SDG 7**), tests whether machine learning can estimate a building's air-conditioning (A/C) and lighting load from its main meter alone, so that UTP Property Management can target peak and after-hours measures without sub-metering.

We used CLEMD, a public 1-second dataset from a Kuala Lumpur university building (16 September–25 October 2023) whose circuit sub-meters give ground truth [6]. From 41,680 cleaned one-minute records we built 98 main-meter features, compared a time-of-day baseline, Ridge, Random Forest, XGBoost and LightGBM with time-series cross-validation, froze the choice, and tested once on a sealed week (19–24 October).

The frozen LightGBM model estimated A/C power with a mean absolute error (MAE) of **1.24 kW** (95% CI 0.57–1.88) against an average A/C load of 6.5 kW. That is 45% lower than the timetable baseline and 21% lower than Ridge, and 1.52 kW in the 29 peak windows. From the main meter alone it put A/C at **44.0%** of peak load (measured 45.4%), relying on phase-2 power and the harmonic signature of inverter compressors. Lighting could not be estimated reliably.

**Recommendation.** Trimming A/C by 20% whenever demand exceeds 53 kW would cut this building's maximum demand by about 5.8 kW, or roughly RM 6,200–6,700 a year (scenario). Pre-cooling during the solar peak, which our proposal suggested, would instead *raise* the peak by 5.2 kW, so it should not be adopted. Cutting after-hours A/C by half and lighting by 30% would save about 9 MWh, or 6.8 tCO₂e, a year per building.

**Main limitation.** The model was trained on one VRF-cooled building, with three weeks of A/C ground truth from a single season. UTP's district-cooled buildings would need a short sub-metered pilot before the model could be used there.

---

## Project Infographic

> **[TODO: insert the one-page infographic image here, e.g. `![Project infographic](figures/infographic.png)`. It must be a single page placed immediately after the executive summary and embedded in this report. A separate file does not count.]**
>
> Content to place on it. Every number below matches the main chapters:
>
> | Block | Content |
> |---|---|
> | Identity & problem | Project title; Group 8; "Building meters show the total, not which load sets the costly peak"; stakeholder: UTP Property Management |
> | Alignment | Energy Security · SDG 7 (Target 7.3 energy efficiency); secondary SDG 13 via avoided tCO₂e |
> | Dataset | CLEMD (UPNM, Kuala Lumpur), 1-s data → 41,680 one-minute records, 16 Sep–25 Oct 2023; input = main meter; targets = A/C panel, lighting boards |
> | ML workflow | Clean & resample → 98 main-meter features → baseline, Ridge, RF, XGBoost, LightGBM → time-series CV → freeze → one-time test on sealed week 6 → SHAP, k-means, scenarios |
> | Key results | A/C MAE 1.24 kW (avg. load 6.5 kW), 45% better than timetable baseline; peak A/C share 44.0% estimated vs 45.4% measured (bar chart: Figure 24) |
> | Recommendation & limitation | Demand-triggered 20% A/C trim → ≈ 5.8 kW, RM 6.2–6.7k/yr per building (**estimate**); don't pre-cool at the solar peak (+5.2 kW); limitation: one VRF building, one season |

---

## Table of Contents

> [TODO: when exporting to PDF, generate a table of contents with page numbers (e.g. `pandoc --toc`) and add lists of figures and tables.]

- Executive Summary
- Project Infographic
- Chapter 1 Introduction and Problem Definition
- Chapter 2 Data Understanding and Exploratory Analysis
- Chapter 3 Data Preprocessing
- Chapter 4 Feature Engineering and Selection
- Chapter 5 Machine Learning Methodology
- Chapter 6 Evaluation Measures, Results and Discussion
- Chapter 7 Sustainability Insights and Recommendations
- Chapter 8 Limitations, Conclusion and Future Work
- References
- Appendix A Data Dictionary and Quality Checks
- Appendix B Model Settings, Tuning Ranges and Supplementary Results
- Appendix C Additional Results
- Appendix D Implementation Instructions
- Appendix E Team Contribution Record

---

## Chapter 1 Introduction and Problem Definition

### 1.1 Background and context

Most of a university's electricity is used in its buildings, and in Malaysia's hot, humid climate cooling is the largest single use. An energy audit of an institutional building at Universiti Malaya found that air-conditioning used 34% of its electricity and lighting 18% [7]. Government guidance for typical Malaysian office buildings puts air-conditioning and mechanical ventilation at about 49% [8], and audits of air-conditioned offices found air conditioners using 57%, with lighting at 19% [9]. Exact shares vary between buildings, but A/C is consistently the largest load and lighting usually the second.

Cooling matters even more at the peak than across the day. Large Malaysian electricity customers pay a maximum-demand charge set by their highest 15-minute window each month [10]. Under the tariff schedule that took effect on 1 July 2025 [11], this charge is split into capacity and network charges. Both are still billed per kW of maximum demand, and together they come to about RM 89.27 per kW per month for medium-voltage customers on the standard tariff, or RM 97.06 per kW on the time-of-use tariff [3], [4]. TNB has said the reform is meant to encourage "load smoothing" [12].

UTP has already acted on both energy cost and peak demand. It changed how its District Cooling Plant (DCP) runs "to minimise the impact of Maximum Demand (MD) charges", which saves RM 1.0 million a year [13]. DCP optimisation, LED retrofits and rescheduled operations together cut its projected annual electricity bill from RM 22.80 million to RM 21.21 million [5]. A 7.4 MWp rooftop solar system meets more than a quarter of the campus demand [14], and a second phase brought rooftop capacity to 7.7 MW [15]. Every building now has an energy meter linked to the cloud-based Integrated Building Management System (i-BMS) [5], and UTP has committed to a net-zero carbon campus by 2050 [16]. Purchased electricity accounts for 20.27 of UTP's 20.33 million kgCO₂e of Scope 1 and 2 emissions a year [2], so almost every tonne of CO₂ the campus emits comes from the grid.

What UTP's meters cannot show is what makes up each building's load. Installing a sub-meter on every A/C and lighting circuit would solve this, but it is expensive and disruptive. Non-intrusive load monitoring (NILM), introduced by Hart [17], instead estimates individual loads from the signals at a single main meter. These signals include real and reactive power, power factor, harmonic distortion and how they change over time [18]. NILM is harder in commercial buildings than in homes, because large HVAC systems with variable-speed drives change their power draw continuously instead of switching cleanly on and off [19].

The people affected are UTP Property Management, who pay for and manage the peak; the sustainability office, which must cut Scope 2 emissions; university management; building occupants, whose comfort depends on the A/C; and the registered energy managers that Malaysia's Energy Efficiency and Conservation Act 2024 (Act 861) now requires large energy users to appoint [20]. The study uses one university building in Kuala Lumpur, recorded from 16 September to 25 October 2023, as a stand-in for a UTP campus building. Section 1.4 sets out the scope.

### 1.2 Problem statement

> **Campus electricity drives UTP's carbon footprint and energy bill, but its building meters cannot show which loads cause the costly demand peaks. As a result, peak-reduction and efficiency measures cannot be targeted or verified building by building.**

**The knowledge gap.** When a demand peak appears, facilities staff cannot tell from the main meter whether it was caused by cooling (which could be trimmed briefly), by lighting (which could be switched off or dimmed), or by loads that cannot be changed. They also cannot tell how much A/C and lighting energy is used outside office hours. The consequence is that UTP pays demand charges set by peaks whose cause is unknown, and measures such as set-point changes or after-hours shut-off are applied blindly, with no way to check their effect.

**Evidence from the data that A/C drives the peak.** Figure 1 compares A/C's share of the building's energy with its share during the building's highest-demand windows. Across all 15-minute windows in weeks 4–6, A/C uses 30.1% of the energy. In the top 5% of demand windows, its share rises to 42.5%, while the lighting and socket share falls from 14.4% to 8.8%. Every one of those peak windows fell on a weekday between 08:00 and 17:00.

![Figure 1. A/C share of energy versus share of peak demand](figures/proposal/fig02_energy_vs_peak_share.png)

*Figure 1. Share of building energy versus share of the top-5% 15-minute demand windows, by circuit (CLEMD weeks 4–6, measured sub-meters).*

**Why machine learning is appropriate.** A simple rule cannot recover A/C from the total. During weekday office hours, a building total of 40–60 kW can correspond to anywhere from about 4 kW to 35 kW of A/C (Figure 9, Section 2.5). Separating these cases means combining power with harmonic, power-factor and time signals in a non-linear way. A supervised model can learn that combination where sub-metered ground truth exists, and then be applied where only the main meter exists. A fixed rule such as "A/C is 30% of the total" cannot. CLEMD's authors describe it as the first Malaysian public dataset of circuit-level electricity use. They suggest disaggregation as one of its uses but publish no ML results [6], and we found no published ML disaggregation results on it.

### 1.3 Aim and measurable objectives

**Aim:** to develop and evaluate machine-learning models that estimate a building's A/C and lighting load from its main incoming meter, and to turn those estimates into peak-demand, solar-timing and emissions insights that UTP's facilities and sustainability teams can act on.

*Table 1. Objectives and where each is evidenced.*

| # | Objective | Evidence of completion |
|---|---|---|
| O1 | Build a clean, time-aligned 1-minute modelling dataset from the CLEMD main supply and A/C, lighting and socket circuits, documenting every data-quality issue found. | Chapter 3; 41,680 records in `data/processed/clemd_1min.parquet`; Tables 5 and 8 |
| O2 | Develop regression models that estimate A/C power (primary) and lighting-and-socket power (secondary) from main-meter features only, and show whether they beat simple baselines on a sealed test week, overall and in the highest-demand 15-minute windows. | Chapters 5–6; Tables 12–14; Figures 12–18 |
| O3 | Explain which electrical and temporal signals the A/C model relies on, and check whether they make physical sense. | Section 6.8; Figures 19–22; Table 16 |
| O4 | Cluster daily load profiles into operating modes and measure A/C and lighting energy used outside office hours. | Section 6.8; Figure 23; Table 17 |
| O5 | Turn the model's estimates into clearly labelled UTP scenarios (peak-demand kW and RM, A/C timing against rooftop solar, avoided tCO₂e) and recommendations. | Chapter 7; Tables 18–20; Figures 24–27 |

### 1.4 Sustainability alignment and scope

**Primary alignment: Energy Security, SDG 7 (Affordable and Clean Energy), Target 7.3** (double the global rate of improvement in energy efficiency) [21]. The project works through three mechanisms. (1) It turns meters UTP already owns into a diagnostic tool that shows which load sets each peak, so peak-reduction measures can be aimed at the right equipment. (2) Lower peaks reduce demand charges and the stress the campus's afternoon peak puts on the grid, which makes campus energy more affordable and secure. (3) Matching A/C timing with on-site rooftop solar tests whether more clean, self-generated energy can be used.

**Secondary alignment: Regenerative Futures, SDG 13.** Every kWh saved avoids Scope 2 emissions at the grid emission factor [22], which supports UTP's 2050 net-zero commitment [16] and Malaysia's national target [23]. We treat this as secondary because the carbon effect for one building is small (Section 7.3). The main value lies in energy efficiency and demand.

**In scope:** supervised regression of A/C and lighting power at 1-minute resolution, k-means clustering of daily load profiles, and scenario analysis combining model estimates with published UTP, TNB, Energy Commission and NASA figures. **Out of scope:** real-time control, deployment on UTP's i-BMS, other seasons or buildings, and forecasting. The optional 15-minute-ahead forecasting extension and the 1-D CNN stretch goal from the proposal were not attempted (Section 1.5).

### 1.5 Expected and achieved outcomes

*Table 2. Proposed outcomes versus what was achieved.*

| Proposed outcome (proposal §1.3) | Status | Notes |
|---|---|---|
| Working A/C disaggregation model in reproducible code | **Completed** | LightGBM, frozen before testing; full pipeline reruns from raw data with one command (Appendix D) |
| Peak-driver profile from model estimates | **Completed** | 44.0% estimated vs 45.4% measured A/C share of peak (Section 7.1) |
| SHAP evidence of the electrical signature | **Completed** | Phase-2 power and 5th/7th/11th harmonics (Section 6.8) |
| Load-profile clusters and after-hours estimate | **Completed** | k = 2 modes; a public holiday found from the main meter alone |
| UTP scenarios (kW, RM, solar, tCO₂e) | **Completed, with one finding reversed** | Pre-cooling into the solar peak was proposed but turns out to *raise* the peak; we now recommend a demand-triggered trim instead |
| Lighting model | **Completed, negative result** | Not reliable from the main meter with this data (Section 6.5) |
| Forecasting extension, 1-D CNN, NASA temperature feature | **Not attempted** | All three were optional and were dropped first, as the proposal's contingency plan specified |
| Benefits for UTP (RM saved, tCO₂e avoided) | **Hoped-for, not measured** | Need deployment on a UTP building; reported as scenarios only |

Changes since the proposal. Clustering now uses the main-meter profile only, rather than A/C and lighting profiles, so it works in buildings without sub-meters. Lighting training was extended to weeks 2–3, as the proposal planned. The work plan's internal target date of 15 November moved forward to the official deadline of 13 November.

Figure 2 summarises how the project connects Problem → Data → Features → Machine Learning → Evaluation → Interpretation → Sustainability.

![Figure 2. Project workflow](figures/proposal/fig01_workflow.png)

*Figure 2. Project workflow, from problem to sustainability scenarios, in the same order as the code.*

---

## Chapter 2 Data Understanding and Exploratory Analysis

### 2.1 Dataset provenance and suitability

CLEMD was recorded in the low-voltage switch room of the Faculty of Medicine and Defence Health building at Universiti Pertahanan Nasional Malaysia (UPNM), Kuala Lumpur. Power-quality loggers sampled each circuit at 200 kHz, and the published files summarise them as one row per second [6]. The data is suitable for this project for three reasons: it comes from a real Malaysian institutional building; it records the main incoming supply (our model input) at the same time as the outgoing circuits, including a dedicated A/C panel (our targets), which gives measured ground truth that very few public non-residential datasets provide; and its A/C and lighting energy shares (30.1% and 14.4%) are close to those of the Universiti Malaya institutional building (34% and 18%) [7].

*Table 3. Dataset provenance.*

| Attribute | Detail |
|---|---|
| Source and access | "CLEMD, a circuit-level electrical measurements dataset", Al-Khadher et al., *Scientific Data* 2024 [6]; data on figshare [1]; downloaded October 2026 |
| Coverage | One institutional building, UPNM, Kuala Lumpur; 16 Sep–25 Oct 2023 in six weekly folders; 1-second sampling |
| Observation unit | Raw: one second of one circuit. Modelling: one minute of the building (main meter + sub-meters joined on timestamp) |
| Original size | 42 CSV files, about 5.9 GB extracted, 0.35–0.52 million rows and 59 columns per file |
| Task and outcome | Supervised regression: A/C real power (kW), primary; lighting-and-socket real power (kW), secondary. Unsupervised clustering of daily profiles (no target) |
| Use constraints | CC BY 4.0 (free use with citation); building-level electrical data only, no personal data |

Each weekly folder contains one CSV per metered circuit. **Aggregate** is the building's main incoming supply and the source of every model input. **CP AC** is the A/C control panel feeding six 10 hp variable-refrigerant-flow (VRF) rooftop units, and is the primary target. **DB TG**, **DB T1** and **DB ML 1** are distribution boards serving mainly lighting plus sockets; their sum is the secondary target. **DB ML 2**, **EMSB 1** (emergency main switchboard) and **SSB MF** (a sub-switchboard) are used only for context. Some circuits in the building (FP 1, PUMP CP, DB RA) were never metered [6], so the main supply always reads more than the sum of the sub-meters.

We also used hourly irradiance for the UTP campus (4.385° N, 100.979° E, October 2023) from NASA POWER [24] for the solar-timing scenario. *These data were obtained from the NASA Langley Research Center (LaRC) POWER Project funded through the NASA Earth Science/Applied Science Program.*

### 2.2 Data dictionary

All model inputs come from the Aggregate (main-meter) file. Table 4 lists the key variables; Appendix A lists all 98 engineered features.

*Table 4. Key variables.*

| Variable | Meaning and unit | Type | Role |
|---|---|---|---|
| `Date`, `Time` | Timestamp of each 1-s record (12-hour clock; mixed D/M/Y and M/D/Y) | Datetime | Index; source of calendar features |
| `Voltage1–3`, `VoltageN` | Phase and neutral voltage (V) | Continuous | Input; also used to detect the outage |
| `Current1–3`, `CurrentN` | Phase and neutral current (A) | Continuous | Input |
| `Frequency` | Supply frequency (Hz) | Continuous | Input |
| `Real Power1–3` | Active power per phase (W) | Continuous | Input; summed to total kW |
| `Apparent Power1–3` | Apparent power per phase (VA) | Continuous | Input |
| `Reactive Power1–3` | Reactive power per phase (VAR); separates motor and inverter loads from resistive ones | Continuous | Input |
| `PF1–3` | Power factor per phase (0–1) | Continuous | Input |
| `THD1–3`, `THDN` | Total harmonic distortion of current (%) | Continuous | Input |
| `Current{1,2,3,N}H{1,3,…,15}` | Odd current harmonics, **% of the fundamental** (H1 is fixed at 100) | Continuous | Input (32 columns) |
| **`ac_kw`** | CP AC Real Power 1+2+3, 1-minute mean (kW) | Continuous | **Primary target** |
| **`light_kw`** | DB TG + DB T1 + DB ML 1 real power, 1-minute mean (kW) | Continuous | **Secondary target** |
| `week` | CLEMD weekly folder number (2–6) | Integer | Splitting only, never a model input |

For clustering there is **no supervised target**. The input is each day's 24-hourly building load (main meter), normalised by that day's maximum.

### 2.3 Target definition and data availability

**Target definition.** Both targets are the real power of the sub-metered circuits, averaged over the same minute as the inputs: `ac_kw` is the sum of CP AC's three phases divided by 1,000, and `light_kw` is the sum of the three lighting boards. The task is *nowcasting*, not forecasting: the model estimates the A/C power in minute *t* from main-meter readings up to and including minute *t*, all of which a meter can supply in real time.

**Leakage exclusions.** No sub-meter signal, nothing recorded after minute *t*, and no identifier (such as `week`) is used as an input. The total building power does *contain* the A/C power, but this is not leakage: the main meter is exactly what UTP would have when using the model, and the task is to separate that total into its parts.

**Availability.** Not every circuit was recorded in every week (Figure 3). Week 1 has no Aggregate file, so it cannot be used. Weeks 2 and 3 have no CP AC file, so A/C ground truth exists only in **weeks 4–6 (4–25 October 2023)**. Lighting boards exist in weeks 2–6. Each weekly folder covers about six days, and the day on which one folder ends and the next begins (27 September and 4, 11 and 18 October) is not recorded.

![Figure 3. CLEMD file availability](figures/proposal/fig03_data_availability.png)

*Figure 3. CLEMD file availability by week and circuit. The outlined block is the A/C modelling set; "dup." marks the duplicated file described in Section 2.4.*

**Mismatch with the intended application.** The CLEMD building is cooled by rooftop VRF units whose compressors sit on the building's own supply. Much of UTP is served by a district cooling plant [13], where a building meter sees air-handling fans and pumps rather than compressors. The trained model therefore cannot be copied to UTP; what transfers is the method (Section 8.1).

### 2.4 Data quality profile

We measured every issue on the raw files before choosing a treatment.

*Table 5. Data quality profile (before cleaning).*

| Quality check | Evidence before cleaning | Response |
|---|---|---|
| Missing files | Week 1: no Aggregate. Weeks 2–3: no CP AC. DB ML 2 missing in weeks 2 and 5; EMSB 1 missing in week 5 | Week 1 excluded; A/C modelling restricted to weeks 4–6; DB ML 2 not used in the lighting target |
| Blank rows | About 33,000 empty rows at the end of several files | Dropped (rows with no `Date`) |
| Duplicate file | Week 1 `DB ML 2.csv` is byte-for-byte identical to `SSB MF.csv` | Excluded (week 1 is not used anyway) |
| Misnamed file | Week 4 main supply is spelt `Aggregtae.csv` | Mapped explicitly by the loader |
| Inconsistent date formats | Some files use M/D/Y and others D/M/Y, sometimes within the same folder; automatic parsing would silently shift files by a month | For each file, the loader picks the format that maps the first row to that folder's known start date |
| Invalid values (outage) | 5 Oct 2023, 14:49–17:03: every circuit reads ≈ 0 V and 0 kW for **135 minutes** | Removed as a supply outage, not zero demand (rule: phase-1 voltage < 100 V) |
| Time gaps | One unrecorded day between each pair of weekly folders, plus the outage | Lag and rolling features are never computed across a gap (Section 4.5) |
| Harmonic units | All `Current*H1` columns equal 100.0 in every row: harmonics are already reported as % of fundamental, not amperes as our proposal assumed | Documented. Ratio features therefore duplicate the raw harmonics (Section 4.2) |
| Unmetered loads | ≈ 55% of building energy comes from circuits outside both targets, some never metered | Kept. A real main meter sees the same mix |
| Duplicated timestamps / class coverage | No duplicate timestamps after joining. Regression task, so no class imbalance; peak windows are rare by design (≈ 5%) | Peak-window metric with day-block bootstrap CIs (Section 6.3) |

The paper is inconsistent about how many circuits were measured [6], so we relied on the files themselves.

### 2.5 Exploratory visualisations

The exploratory analysis below uses weeks 4–6, the weeks with A/C ground truth. Over those weeks the building drew an average of 20.3 kW, of which A/C averaged 6.1 kW. The highest 15-minute demand was 83.9 kW (31.7 kW of it A/C), and the highest single minute was 94.6 kW.

![Figure 4. Target distributions](figures/report/fig_target_distributions.png)

*Figure 4. Distribution of the two targets over their training weeks (1-minute means): A/C, weeks 4–5 (16,985 minutes); lighting and sockets, weeks 2–5 (32,725 minutes).*

Figure 4 shows that the two targets behave very differently. A/C is **strongly right-skewed** (skewness 1.88): 28.4% of training minutes are below 1 kW, mostly at weekends when the units are off, and a long tail runs up to 44 kW on weekday afternoons. Its median (1.6 kW) is far below its mean (5.9 kW). Lighting and sockets are also right-skewed (skewness 1.72) but over a narrow range, and they are **multi-modal**: a large peak near 2 kW (the always-on floor of sockets, servers and security lighting), and smaller peaks near 4 kW and 6 kW, which correspond to different working-hours lighting levels. **Why it matters:** with a skewed target, the average error is dominated by the few busy hours, so we report peak-window MAE separately and do not rely on R², which looks high mainly because of the large gap between near-zero nights and busy afternoons. The lighting target's narrow range means even a small absolute error is a large relative one.

![Figure 5. Building, A/C and lighting load over six days](figures/proposal/fig04_week6_timeseries.png)

*Figure 5. Building, A/C and lighting-and-socket load, 19–24 October 2023 (15-minute means, measured sub-meters).*

Figure 5 shows that building demand rises sharply on weekday mornings and falls in the late afternoon, and that A/C (blue) accounts for most of that swing. Lighting and sockets (orange) form a smaller, steadier load. The A/C peak on Tuesday 24 October was much lower than on the Monday before, so day-to-day variation is real and a model must capture it rather than repeat an average day.

![Figure 6. Average daily load profile](figures/proposal/fig05_daily_profile.png)

*Figure 6. Average daily load profile by circuit, weekdays and weekends (weeks 4–6).*

On weekdays (Figure 6), A/C ramps up from about 08:00, peaks around 14:00 and falls away after 17:00. At weekends the building runs at a nearly flat baseline of about 10 kW, most of it unmetered or "other" load. Overnight (00:00–06:00) the building still draws 10.6 kW on average, of which A/C is 1.3 kW. **Why it matters:** time of day explains a lot, so a time-of-day average is the natural baseline a model must beat.

![Figure 7. Hourly A/C load for each day](figures/proposal/fig06_ac_heatmap.png)

*Figure 7. Hourly mean A/C load (kW) for each day, weeks 4–6. The white block on 5 October is the supply outage.*

Figure 7 shows that some weekdays (Friday 6 October, Tuesday 10 October and Tuesday 24 October) are much lighter than others, which points to timetable and occupancy effects. **Why it matters:** there are distinct kinds of day, and these are what the clustering step is designed to find.

![Figure 8. Correlation of main-meter signals with A/C power](figures/proposal/fig07_feature_correlation.png)

*Figure 8. Pearson correlation of selected main-meter signals with measured A/C power (1-minute data, weeks 4–6).*

Total real power is the strongest single signal (r = 0.94). The 5th and 7th harmonics and THD on phase 1 follow closely (r = 0.85–0.86), as expected if the inverter-driven VRF compressors inject those harmonics. Power factor on phases 1 and 3 falls as A/C rises (r ≈ −0.65), but phase 2 behaves differently (r = 0.08), so the A/C load is not spread evenly across phases. **Why it matters:** harmonics carry A/C-specific information beyond total power, and the many strongly correlated inputs need regularisation (Ridge) or tree models. Correlation is not causation: these are associations in one building.

![Figure 9. Main-meter total versus A/C load](figures/proposal/fig08_agg_vs_ac.png)

*Figure 9. Total building power versus A/C power, 15-minute windows; office-hours windows highlighted.*

Outside office hours (grey), A/C and total load move together closely. During weekday office hours (blue), a total of 40–60 kW can hide anywhere from about 4 kW to 35 kW of A/C. **Why it matters:** this ambiguous band is exactly where peaks happen, and Chapter 6 shows it is where the model's error is largest.

### 2.6 Insights that shape the methodology

*Table 6. How each data observation changed the workflow.*

| Observation | Change to the workflow |
|---|---|
| Neighbouring minutes are almost identical (time series) | Chronological split with a sealed test week; expanding-window CV with a 60-minute gap; no random splits [25] |
| A/C is a larger share of the peak (42.5%) than of energy (30.1%) (Figure 1) | Peak-window MAE added as a key metric |
| Strong daily and weekly rhythm (Figures 6 and 7) | Calendar features; time-of-day average as Baseline 1 |
| The total is ambiguous in office hours (Figure 9) | Non-linear models plus harmonic and power-quality features, not total power alone |
| Many highly correlated electrical signals (Figure 8) | Ridge (L2) for the linear model; SHAP and permutation importance interpreted by *feature group* |
| Data gaps between weeks and at the outage | Lags and rolling windows computed within contiguous segments only |
| Only ≈ 29 peak windows in a test week | Day-block bootstrap confidence intervals |
| Distinct kinds of day (Figure 7) | k-means on normalised daily profiles |

**Note on the test week.** The descriptive figures in our proposal (Figures 1 and 5–9) were drawn from weeks 4–6, so they include week 6's *measured* loads. No model, feature or hyperparameter was ever fitted, tuned or selected on week 6. The feature-redundancy check (Section 4.2) and all cross-validation used weeks 2–5 only, and the model choice was frozen in writing before any model saw week 6 (Section 5.3). However, our general view of the data did include a look at the test week, and we state this openly.

---

## Chapter 3 Data Preprocessing

### 3.1 Preparation sequence

All steps are scripted in `prepare_data.py` and `features.py`. The raw CSVs are read once and saved to Parquet, so every later step starts from the same file.

1. **Read** each weekly folder's Aggregate file (all 59 columns) and the CP AC, DB TG, DB T1 and DB ML 1 files (date, time and real power only), resolving the misnamed file and each file's date format.
2. **Drop** trailing blank rows; convert all values to numbers.
3. **Resample** 1 second → 1 minute: the mean of every main-meter signal, plus the within-minute standard deviation, minimum and maximum of total real power.
4. **Join** main meter and sub-meters on the minute, keeping only minutes where the main meter and all three lighting boards are present.
5. **Remove** the outage (phase-1 voltage < 100 V).
6. **Derive** `light_kw` = DB TG + DB T1 + DB ML 1.
7. **Build features** (Chapter 4) within contiguous segments, then drop rows whose 60-minute lag window is incomplete.
8. **Partition** by CLEMD week (Section 5.3).

*Figure 2 (Section 1.5) shows the full workflow.* Observation counts at each step:

> 42 raw CSV files (1 s) → weeks 2–6 loaded (week 1 excluded: no main meter) → **41,815** joined minutes → outage removed (−135) → **41,680** clean minutes (69 columns) → features built, 365 minutes with incomplete lag windows dropped → **41,315** model-ready minutes → A/C train 16,985 (weeks 4–5) · lighting train 32,725 (weeks 2–5) · test 8,590 (week 6)

Each run of `prepare_data.py` and `features.py` ends with `assert` checks (dates fall in September–October 2023, timestamps are increasing with no duplicates, A/C is present only where CP AC exists, and lags never cross a gap), so the dataset can be regenerated and checked from raw data.

### 3.2 Cleaning and missing values

*Table 7. Cleaning rules and their effect.*

| Step | Rule and rationale | Effect on dataset |
|---|---|---|
| Blank rows | Drop rows with no date: they carry no data | ≈ 33,000 rows per affected raw file |
| Date parsing | Choose M/D/Y or D/M/Y per file so row 1 equals the folder's known start date. Automatic parsing would silently misplace files | All files land in 21 Sep–25 Oct 2023 (checked by `assert`) |
| Units | Sum three phases and divide by 1,000 to give kW, kVAR and kVA | Totals for building, A/C and lighting |
| Missing circuits | No imputation: a missing A/C file means *no ground truth*, and inventing a target would teach the model its own guesses | Weeks 2–3 have `ac_kw` empty (15,862 minutes); used only for lighting, clustering and out-of-sample scenario estimates |
| Missing minutes inside weeks | None in the A/C weeks after joining; 5 minutes had a single 1-s sample, so no within-minute std | Those 5 rows are dropped with the incomplete-lag rows |
| Gap days and outage | Left as gaps, not filled. Interpolating 135 minutes or a whole day would create fake load shapes | Features never span a gap (Section 4.5) |

**Risk of losing meaningful observations.** The only rows removed are the outage, blank rows and 365 minutes at segment starts whose lag history is incomplete (0.9% of clean minutes). No high-demand minute was removed.

### 3.3 Outliers and unusual cases

We checked extreme values against what the building could physically do rather than applying a statistical cut-off. The outage is an *invalid* reading (0 V on every circuit at once) and was removed. Short demand spikes up to 94.6 kW for the building and 44.1 kW for A/C occur on weekday afternoons and coincide with A/C ramps, so they are **real peaks**. In a peak-demand study they are the most important observations, so they were kept unchanged. No capping or transformation was applied to the inputs or targets. Averaging from 1 second to 1 minute reduces sensor noise and small clock misalignment between the separate loggers.

### 3.4 Encoding, scaling and imbalance

- **Encoding.** There are no text categories. Hour of day is encoded cyclically (sin and cos), so 23:00 and 00:00 are close. Day of week is an integer 0–6, which tree models can split on directly. Weekend and office-hours flags are binary. Unknown categories cannot occur.
- **Scaling.** Only Ridge needs scaling, because its penalty depends on feature scale. It uses a `StandardScaler` inside a scikit-learn pipeline, so the scaler is **fitted on each training fold only** and applied to the validation or test data. Tree models are scale-invariant and use raw values.
- **Imbalance.** This is regression, so there are no classes. The decision-relevant peak windows are rare by definition (top 5%). We did not resample, because that would change the time series. We report a separate peak-window metric with bootstrap intervals instead.

### 3.5 Final prepared dataset

![Figure 10. Data preparation sequence](figures/report/fig_prep_flow.png)

*Figure 10. Data preparation sequence, from raw CLEMD files to model-ready partitions, with record counts at each step (generated from the code, so the counts are those of the submitted pipeline).*

*Table 8. Final prepared dataset.*

| Item | Value |
|---|---|
| Clean 1-minute records | 41,680 (weeks 2–6, 21 Sep 23:55 – 25 Oct 00:05, 2023) |
| Model-ready records | 41,315 |
| Features | 98 (all from the main meter or the clock) |
| A/C target (training weeks 4–5) | mean 5.92 kW, median 1.58 kW, SD 9.49 kW, max 44.07 kW: strongly right-skewed, with long near-zero periods at night and weekends |
| Lighting target (training weeks 2–5) | mean 2.68 kW, SD 1.23 kW, range 1.00–8.16 kW |
| Test week (week 6) | 8,590 minutes; A/C mean 6.5 kW, lighting mean 3.1 kW |
| Remaining issues | Unmetered loads; possible small logger clock offsets; lighting level drifts upward from September (≈ 2.5 kW) to October (≈ 3.0 kW) |
| Where it lives in the code | `data/processed/clemd_1min.parquet` (from `prepare_data.py`); features built on the fly by `features.build()` |

---

## Chapter 4 Feature Engineering and Selection

### 4.1 Feature design rationale

Every feature comes from the main meter or the clock, never from a sub-meter, so that the model can run on a building that only has a main meter. The 98 features fall into five groups (Table 9; full list in Appendix A).

*Table 9. Feature groups.*

| Group (count) | Feature / construction | Reason for inclusion |
|---|---|---|
| **Power (15)** | Original: real, reactive and apparent power per phase (1-min mean). Derived: total kW, kVAR, kVA; within-minute std, min and max of total kW | The A/C load is part of the total; per-phase values matter because A/C is not spread evenly across phases (Figure 8). Within-minute variability captures compressor cycling |
| **Power quality (16)** | Original: voltage, current (per phase and neutral), frequency, PF per phase, THD per phase and neutral | Inductive and inverter loads lower PF and raise THD; voltage dips with heavy load |
| **Harmonics (53)** | Original: 32 odd current harmonics (H1–H15 × 3 phases + neutral). Derived: 21 ratios Hn/H1 for n = 3–15, per phase | Inverter-driven VRF compressors draw distorted current. Six-pulse rectifiers produce characteristic 5th, 7th, 11th and 13th harmonics [26] |
| **Temporal (9)** | Derived: total kW lagged 1, 5, 15 and 60 min; rolling mean and std over 15 and 60 min; 1-minute change | Recent history separates a building that is ramping up from one holding steady; sudden steps mark switching events |
| **Calendar (5)** | Derived: sin and cos of hour, day of week, weekend flag, office-hours flag (weekday 08:00–17:00) | Occupancy and timetable proxies |

**How the key derived features are calculated.** `p_lag15` is total real power 15 minutes earlier. `p_roll60_mean` is the mean total power over the last 60 minutes, including the current one. `ratio_3H5` is phase-3 5th-harmonic current divided by the phase-3 fundamental. `office_hours` is 1 on weekdays from 08:00 to 16:59.

The NASA temperature feature, listed as optional in the proposal, was not used. Hourly temperature is shared by every minute in an hour and mostly duplicates time of day over a three-week window.

### 4.2 Feature selection

**All 98 features were kept; no automatic selection was applied.** We justify this rather than invent a selection stage. The reasons are:

1. **Redundancy was measured, on development data only.** `features.py` computes absolute correlations among all features on weeks 2–5 (never the test week) and lists **130 pairs with |r| > 0.98** (`results/redundant_feature_pairs.csv`). Examples include phase current and apparent power (r = 0.9999) and total kW and kVA (r = 0.9997).
2. **The models chosen tolerate redundancy.** Ridge's L2 penalty shares weight among correlated inputs instead of letting it explode [27]. Trees simply pick one of several equivalent splits. Dropping features by hand risks removing the one variant that matters for a specific phase.
3. **Selecting by test performance is forbidden**, and selecting within CV folds over 98 features would have used up the small, fixed tuning budget agreed in the proposal.

**A finding we report honestly.** The redundancy check showed that each ratio feature correlates perfectly (r = 1.00) with its raw harmonic. The reason is that CLEMD already reports harmonics as a percentage of the fundamental: every `Current*H1` value is exactly 100. So the 21 ratio features are exact copies of the raw harmonics divided by 100, and the four H1 columns are constant. The model effectively has **73 distinct informative inputs**. This does not affect accuracy (trees and Ridge are unaffected by exact copies), but it does split SHAP credit between twins such as `agg_Current3H5` and `ratio_3H5`. That is one reason we interpret importance by feature group (Section 6.8). The feature set was frozen before this was noticed, and we did not change it afterwards. Removing the duplicates is listed as future work.

### 4.3 Dimensionality reduction

**Not applicable.** PCA was not used. It would mix power, harmonic and calendar signals into components that a facilities team cannot interpret, and the tree models handle 98 inputs without difficulty (about 2 seconds to train LightGBM).

### 4.4 Evidence of usefulness

We did not run a formal feature-ablation experiment. Three pieces of evidence still show that the engineered features add value:

- **Calendar features on their own are not enough.** The time-of-day baseline uses only hour and weekend information and has an A/C test MAE of 2.26 kW, against 1.24 kW for the full feature set (Table 12).
- **Grouped permutation importance (Table 16).** On the test week, shuffling the harmonic group raises the frozen model's MAE by 2.11 kW, and shuffling the temporal group raises it by 0.42 kW. Both groups therefore carry information that the power group does not.
- **The model does not follow the timetable.** Calendar features contribute the least (permutation +0.19 kW), which is why the model handles light weekdays that the timetable baseline gets wrong.

A proper ablation run under the same CV protocol is listed as future work.

### 4.5 Leakage and interpretation checks

- **No target information:** no sub-meter column is used as an input, and `week` is used only to split the data.
- **No future information:** lags and rolling windows look only backwards (`shift` and trailing `rolling`), and are computed inside **contiguous segments**, so a lag never reaches across a missing day or the outage. An `assert` checks that the first minute after every gap has no lag-1 value.
- **No fold leakage in CV:** `TimeSeriesSplit(gap=60)` leaves 60 minutes between each training and validation fold, which is the length of the longest lag.
- **Redundancy check excludes the test week**, and peak windows are defined from *building* demand (an input), not from the target.
- **Interpretation limit:** a feature that predicts A/C well, such as the 5th harmonic, is a *signature* of A/C running, not a lever. Lowering harmonics would not lower cooling. Stakeholders act on the A/C itself.

---

## Chapter 5 Machine Learning Methodology

### 5.1 Task formulation and pipeline

**Task.** Supervised regression. Input: the 98 main-meter features for minute *t*. Output: estimated A/C real power (kW) in minute *t*, and separately lighting-and-socket power. A secondary unsupervised task groups whole days by the shape of their main-meter load profile.

**Why ML and not a simple rule.** A fixed-fraction rule ("A/C = 30% of the total") fails in exactly the office-hours windows that set the peak (Figure 9). The time-of-day baseline, which is the best timetable rule, is beaten by 45% (Table 12).

The pipeline (Figure 2, Section 1.5) runs as nine scripts, in this order: `prepare_data` (O1) → `features` (O1) → `train`: baselines, tuning and **model freeze** (O2) → `evaluate`: one-time test, CIs, robustness and error analysis (O2) → `explain`: SHAP and permutation importance (O3) → `cluster`: operating modes and after-hours energy (O4) → `scenarios`: kW, RM, solar and tCO₂e (O5) → `make_figures` → `build_dashboard`, which produces the presentation.

### 5.2 Baseline and selected algorithms

*Table 10. Models compared.*

| Model | How it works | Why it fits | Role |
|---|---|---|---|
| **Time-of-day average** | Predicts the mean training target for the same hour and day type (weekday or weekend) | Uses no electrical data. If we cannot beat it, the main meter adds nothing beyond the timetable | Baseline 1 |
| **Ridge regression** [27] | Linear model with an L2 penalty on standardised features | Simple, fully interpretable, and handles correlated inputs. Total power alone correlates at r = 0.94 with A/C | Baseline 2, and the default if trees do not clearly win |
| **Random Forest** [28] | Averages 200 decision trees, each fitted to a bootstrap sample with random feature subsets | Learns interactions (e.g. *high power + strong 5th harmonic + office hours = A/C on*), robust to outliers and correlation | Candidate |
| **XGBoost** [29] | Gradient boosting: 400 shallow trees added in sequence, each correcting the errors of the previous ones | Usually the strongest family for tabular data; exact TreeSHAP | Candidate |
| **LightGBM** [30] | Histogram-based gradient boosting that grows leaf-wise | Fast and accurate on tabular data; exact TreeSHAP | Candidate (**frozen choice for A/C**) |
| **k-means** [31] | Partitions days into *k* groups minimising within-group distance; *k* chosen by silhouette [32] | No labels exist for "type of day" | Unsupervised operating modes |

The 1-D CNN stretch goal was not attempted. With about three weeks of A/C data from one building, deep NILM models, which usually need months of data [33], would be hard to train well and much harder to explain to a facilities team.

### 5.3 Evaluation design

![Figure 11. Chronological train/test split](figures/proposal/fig09_split.png)

*Figure 11. Chronological split of the CLEMD data. A/C trains on weeks 4–5 and lighting on weeks 2–5; both are tested once on week 6.*

- **Split (Figure 11).** Strictly chronological. **A/C:** train on weeks 4–5 (16,985 minutes, 66%) and test on week 6 (8,590 minutes, 34%). **Lighting:** train on weeks 2–5 (32,725 minutes, 79%) and test on week 6. A random split would leak information, because neighbouring minutes are nearly identical [25].
- **Cross-validation.** `TimeSeriesSplit(n_splits=4, gap=60)` within the training weeks: four expanding windows, each validating on the next block of time after a 60-minute gap. Every model and configuration uses the same folds.
- **Freeze rule, fixed before tuning.** Pick the best configuration of each model by mean CV MAE. Choose the tree model with the lowest CV MAE **only if it is at least 5% below Ridge**; otherwise choose Ridge. This follows the brief's preference for simple models.
- **Freeze and sealed test.** `features.load()` drops week 6 by default, so no tuning code can see it. The choice was written to `results/freeze.json` on 6 November 2026 at 21:11 and committed (`9e5fc5e`) **before week 6 was ever loaded**. Week 6 was then evaluated once, and nothing was changed after seeing the results. Rerunning `train.py` never overwrites the freeze. It writes `freeze_rerun.json` and checks that the same choice is reproduced (rerun on 10 November: reproduced).
- **Robustness.** Separately, each model is trained on week 4 and tested on week 5, to see how it holds up across weeks.
- **Seeds.** `random_state=0` for all models and k-means, and `numpy.random.default_rng(0)` for the bootstrap and permutation importance.

### 5.4 Training and hyperparameter selection

The search spaces were small and agreed in advance, so that tuning could not quietly overfit the validation folds. We used grid search with mean MAE over the four CV folds as the selection metric; the full grid is in Appendix B. That makes 17 configurations × 4 folds × 2 targets = 136 fits.

*Table 11. Final settings (validation-selected values in bold; everything else is a fixed default we chose).*

| Model | Fixed settings | Searched | Selected (A/C) | Selected (lighting) |
|---|---|---|---|---|
| Time of day | n/a | n/a | n/a | n/a |
| Ridge | StandardScaler | α ∈ {0.1, 1, 10, 100} | **α = 100** | **α = 100** (frozen) |
| Random Forest | 200 trees, max_features 0.33 | max_depth ∈ {None, 12}; min_samples_leaf ∈ {1, 5} | **None, 1** | **None, 5** |
| XGBoost | 400 trees, subsample 0.8, colsample 0.8 | max_depth ∈ {4, 6}; learning_rate ∈ {0.03, 0.1} | **4, 0.03** | **4, 0.03** |
| LightGBM | 400 trees, subsample 0.8, colsample 0.8 | num_leaves ∈ {15, 63}; learning_rate ∈ {0.03, 0.1} | **63, 0.1** (frozen) | **63, 0.1** |

**Freeze outcome.** For A/C, LightGBM's CV MAE (0.987 kW) was 57% below Ridge's (2.275 kW), so the rule chose **LightGBM**. For lighting, the best tree model (Random Forest, 0.363 kW) was *not* 5% better than Ridge (0.360 kW), so the rule chose **Ridge**. No early stopping was used; the number of trees is fixed.

### 5.5 Implementation details

- **Language and packages:** Python 3.11.17; pandas 3.1.1 [34], NumPy 2.4.6, PyArrow 26.0.1, scikit-learn 1.9.1 [35], XGBoost 3.2.0 [29], LightGBM 4.7.0 [30], SHAP 0.51.0 [36], Matplotlib 3.11.2 [37]. All versions are pinned in `requirements.txt`.
- **Environment:** Linux (WSL2) on a standard laptop CPU, with no GPU. The full pipeline from raw CSVs takes about 12 minutes, mostly CV. LightGBM trains in about 2 seconds and predicts a week in well under a second, so retraining it every night on a building management server would be cheap.
- **Model reconstruction:** no model files are stored. `evaluate.py` rebuilds the frozen model and its fitted scaler (if any) from `freeze.json` and refits on the training weeks, which is deterministic with the fixed seeds.
- **Self-checks:** every script ends with `assert` checks, including that SHAP values add up to the prediction, that shaving never raises the peak, and that the cluster day counts add up.

---

## Chapter 6 Evaluation Measures, Results and Discussion

### 6.1 Measures that fit the decision

**Primary selection metric: MAE (kW)**, the average size of the error in physical units. It is easy for facilities staff to read ("on average the estimate is off by 1.2 kW") and it is the metric the freeze rule used.

Complementary measures, each answering a stakeholder question (*ŷ* = estimate, *y* = measured, *n* = minutes, *P* = building power):

- **RMSE** = √(Σ(ŷ − y)²/n): penalises large misses more heavily.
- **R²** = 1 − Σ(ŷ − y)²/Σ(y − ȳ)²: reported but given little weight, because A/C is part of the total, so even a trivial model scores a high R².
- **Peak-window MAE**: MAE on 15-minute means, restricted to the windows where *building* demand is in the top 5% of the test week (≥ 61.9 kW, 29 windows). These are the windows that set the demand charge, so this is **the most decision-relevant measure**.
- **Energy-share error (percentage points)** = 100 × (Σŷ − Σy)/ΣP: whether the model gets A/C's share of building energy right. This feeds the kWh and tCO₂e estimates.
- **Normalised disaggregation error** NDE = √(Σ(ŷ − y)²/Σy²): a standard NILM metric [18], for comparison with the literature.
- **Silhouette score** for clustering [32].

### 6.2 Quantitative comparison

All values below are on the **held-out test week (week 6)**. Every model was retrained at its best CV configuration on the same training weeks and scored with the same definitions.

*Table 12. A/C (primary target, test-week average 6.5 kW), held-out test week. 95% CIs from a day-block bootstrap.*

| Model | MAE kW [95% CI] | RMSE kW | R² | Peak-window MAE kW [95% CI] | Energy-share error (pp) | NDE |
|---|---|---|---|---|---|---|
| Time-of-day average | 2.26 [1.29, 3.25] | 4.28 | 0.80 | 6.54 [3.41, 7.92] | −2.6 | 0.37 |
| Ridge | 1.56 [1.19, 1.91] | **2.35** | **0.94** | 1.95 [0.93, 2.15] | +2.3 | **0.20** |
| Random Forest | 1.25 [0.61, 1.88] | 2.47 | 0.93 | 2.11 [1.72, 4.72] | −1.1 | 0.21 |
| XGBoost | 1.33 [0.61, 2.01] | 2.55 | 0.93 | 1.92 [1.26, 5.21] | **−0.3** | 0.22 |
| **LightGBM (frozen)** | **1.24 [0.56, 1.87]** | 2.57 | 0.93 | **1.52 [1.11, 5.13]** | −0.9 | 0.22 |

*Table 13. Lighting and sockets (secondary target, test-week average 3.1 kW), held-out test week.*

| Model | MAE kW [95% CI] | RMSE kW | R² | Peak-window MAE kW | Energy-share error (pp) |
|---|---|---|---|---|---|
| Time-of-day average | 0.51 [0.30, 0.76] | 0.86 | 0.72 | 1.78 | −1.9 |
| **Ridge (frozen)** | 0.64 [0.55, 0.77] | 0.78 | 0.76 | **1.05** | −3.0 |
| Random Forest | **0.42** [0.24, 0.63] | **0.72** | **0.80** | 1.28 | −1.7 |
| XGBoost | 0.45 | 0.74 | 0.79 | 1.29 | −2.1 |
| LightGBM | 0.43 | 0.75 | 0.78 | 1.50 | −1.9 |

![Figure 12. Model comparison on the test week](figures/report/fig_model_comparison.png)

*Figure 12. Test-week MAE for every model, with 95% day-block bootstrap intervals: A/C over all minutes (left), A/C in the 29 peak windows (centre), lighting and sockets (right). The frozen model for each target is in blue.*

Figure 12 puts Tables 12 and 13 side by side. For A/C, all four learned models clearly beat the timetable baseline, and the three tree models sit together at about 1.2–1.3 kW. The peak-window panel shows why the peak result needs care: LightGBM has the lowest point estimate (1.52 kW), but its interval is wide (1.11–5.13 kW) because one or two badly estimated afternoons can dominate 29 windows. For lighting, the frozen Ridge model (blue) is the worst on typical error. Section 6.5 explains why.

*Table 14. Robustness check: A/C, train week 4 → test week 5 (validation, not the sealed test).*

| Model | MAE kW | RMSE kW | R² | Peak-window MAE kW | Energy-share error (pp) |
|---|---|---|---|---|---|
| Time-of-day average | 3.02 | 4.75 | 0.77 | 8.62 | −9.9 |
| Ridge | 2.81 | 3.66 | 0.87 | 4.08 | −4.5 |
| Random Forest | 1.16 | 2.42 | 0.94 | 1.62 | −1.6 |
| XGBoost | **1.16** | **2.33** | **0.95** | 1.49 | −1.6 |
| LightGBM | 1.18 | 2.46 | 0.94 | **1.04** | **−1.5** |

### 6.3 Uncertainty and consistency

- **Bootstrap.** CIs in Tables 12–13 come from 2,000 resamples of whole **days** (seven calendar dates, six of them full days). Resampling days rather than minutes keeps the within-day correlation, in the spirit of the block bootstrap [38]. The intervals are wide because there are only six full test days, and **the CIs of LightGBM, Random Forest, XGBoost and Ridge overlap**.
- **Across CV folds** (Appendix B, Table B2), LightGBM's A/C MAE ranged from 0.75 to 1.19 kW (SD 0.22), while Ridge's ranged from 1.37 to 3.01 kW (SD 0.85). Tree models were consistently better than Ridge on typical error in every fold, but **peak-window MAE varied a lot between folds** for all models (LightGBM 0.98–4.81 kW), because each fold has only a handful of peak windows.
- **Across weeks** (Table 14), tree models hold up when trained on a single week, with MAE 1.16–1.18 kW. Ridge degrades to 2.81 kW.

![Figure 13. Consistency across folds and weeks](figures/report/fig_consistency.png)

*Figure 13. Consistency of the A/C models. Left: MAE in each of the four expanding-window CV folds (dots) and their mean (tick), at each model's best configuration. Right: MAE when trained on week 4 and tested on week 5.*

Figure 13 shows that the gap between tree models and the two baselines is consistent rather than an accident of one split. Every tree-model fold (0.73–1.26 kW) is below every Ridge fold (1.37–3.01 kW) and every baseline fold (2.33–3.67 kW). The ranking *among* the tree models changes from fold to fold. Ridge also has by far the widest spread, and it more than doubles its error when trained on a single week (right). This matters for UTP, because a new building would start with only a short sub-metering period.

We therefore do **not** claim that LightGBM is significantly better than the other tree models, or than Ridge on peak windows. The honest claim is that tree models are consistently better than Ridge on typical error across folds, weeks and the test week; that LightGBM has the best point estimates on MAE and peak MAE; and that Ridge is competitive on large errors.

### 6.4 Final selection

**A/C: LightGBM**, chosen by the pre-registered rule and confirmed on the test week, where it had the lowest MAE and peak-window MAE. Random Forest and XGBoost are practically equivalent, and LightGBM is the fastest to train of the three. Ridge would be the simpler choice, but it misses typical minutes by 26% more and degrades badly when trained on less data (Table 14), which matters when a new building has only a short sub-metering period. **Lighting: Ridge**, chosen by the rule. It was the best model on peak windows but the worst on typical error in the test week (Section 6.5). We keep the frozen choice, but we do not recommend using any lighting model operationally.

### 6.5 Explain the principal findings

**O2: Does the main meter carry enough information to estimate A/C? Yes.** The frozen model cuts typical error by **45%** against the timetable baseline (1.24 vs 2.26 kW) and by **21%** against Ridge. In peak windows it cuts error by **77%** against the baseline (1.52 vs 6.54 kW). It gets A/C's share of building energy right to within 1 percentage point. It beats the baseline because it reads A/C from electrical signals rather than from the clock: it handles light weekdays such as 24 October, which the timetable treats as normal weekdays.

Ridge has a lower RMSE (2.35 vs 2.57 kW) and tighter CIs, so it makes fewer *very large* misses. The tree models are better on typical minutes but occasionally miss sharp A/C switching events by several kW. Both behaviours are visible in Figure 16.

**Lighting is a negative result, and we report it as one.** Ridge won cross-validation (MAE 0.360) but was the *worst* model on typical test-week error (0.64 kW) and under-estimated lighting by 3.0 points of building energy. The reason is drift. The lighting level rose from about 2.4–2.6 kW in the September weeks used for training to 3.1 kW in the October test week, and a linear model extrapolates poorly when that happens. More fundamentally, lighting and sockets are a small, flat load (around 15% of energy) that changes the main-meter signals very little. **Lighting disaggregation from the main meter alone is not reliable with this data.** Recommendations that depend on lighting therefore use the *measured* lighting boards, and are marked as such.

![Figure 14. Lighting estimate versus measured](figures/report/fig_lighting_test.png)

*Figure 14. Lighting-and-socket load estimated from the main meter (frozen Ridge, dashed) versus measured (orange), test week, 15-minute means.*

Figure 14 shows the failure directly. The estimate follows the weekday on/off pattern, which is why it does well on peak windows, but it runs consistently below the measured load: a week mean of 2.47 kW against 3.07 kW measured. It is also noisy, because it reacts to swings in the main meter that are really A/C. This is the signature of a model fitted to a lower September level that cannot isolate a small load inside a large, changing total.

### 6.6 Visual evidence

![Figure 15. Estimated versus measured A/C over the test week](figures/results/test_week_timeseries.png)

*Figure 15. A/C estimated from the main meter (dashed) versus measured by the sub-meter (blue), with the building total (grey), test week 19–24 October 2023, 15-minute means.*

Figure 15 shows that the estimate follows the daily A/C cycle, including the light Tuesday on 24 October. The largest gaps are on Friday 20 October, when A/C is under-estimated by about 5 kW for most of the afternoon, and around midday on 24 October, when measured A/C briefly drops to about 3 kW but the estimate stays near 15 kW. Night-time and weekend A/C is tracked closely.

![Figure 16. Estimated versus measured A/C scatter](figures/results/test_pred_vs_actual.png)

*Figure 16. Estimated versus measured A/C, 15-minute windows of the test week. Orange points are the top-5% building-demand windows; the dotted line is perfect agreement.*

Points cluster around the diagonal, with no strong systematic bias, and most peak windows (orange) sit within a few kW of it. The largest misses are in the middle range and go both ways: some windows with 3–7 kW of measured A/C are estimated at 14–16 kW, and some at 19–27 kW are under-estimated by 5–12 kW. These are the ambiguous mid-load cases discussed below.

![Figure 17. Residual analysis](figures/report/fig_residuals.png)

*Figure 17. Residual analysis of the frozen A/C model on the test week. Left: residual (estimated − measured) against building load, 15-minute windows. Centre: MAE by building-load band with the number of minutes. Right: distribution of 1-minute residuals.*

The residuals (Figure 17) are centred close to zero: mean -0.17 kW, median -0.01 kW. 70.9% of minutes are within ±1 kW and 92.5% within ±5 kW, so there is **no large systematic over- or under-prediction** across the week. Outside office hours the residuals are almost zero. In weekday office hours they fan out in both directions, with a mean of -1.24 kW, so office-hours A/C is slightly under-estimated on average. At 45–65 kW of building load, 84% of office-hours windows are under-estimated, typically by 2–8 kW. The model is conservative on the busiest afternoons, so savings estimates built on it tend to understate peak A/C rather than overstate it. A small cluster at about 36–38 kW is *over*-estimated by about 10 kW; these are the midday windows on 24 October when the measured A/C briefly dropped (Figure 15). The fan is widest at 30–60 kW of building load and narrows again above 60 kW, which matches the load-band breakdown in Table 15. The distribution has a sharp central peak and long tails on both sides: most minutes are estimated very well, and a small number of switching and mid-load minutes produce the large errors that drive RMSE.

### 6.7 Error and subgroup analysis

*Table 15. Frozen A/C model, test-week MAE by subgroup (n = minutes behind each value).*

| Subgroup | MAE kW | n |
|---|---|---|
| Weekday | 1.78 | 5,710 |
| Weekend | 0.15 | 2,880 |
| Hours 00:00–07:00 (all days) | 0.28–0.58 | 360 per hour |
| Hours 08:00–14:00 (all days) | 2.33–3.38 (worst at 13:00) | 360 per hour |
| Hours 15:00–17:00 (all days) | 0.88–1.82 | 360 per hour |
| Building load < 15 kW | 0.33 | 6,244 |
| 15–30 kW | 2.01 | 319 |
| 30–45 kW | 4.30 | 660 |
| 45–60 kW | 4.66 | 799 |
| ≥ 60 kW | 2.40 | 568 |
| Minutes with a > 5 kW step change | 3.50 | 227 |
| All other minutes | 1.17 | 8,363 |

![Figure 18. Test-week error by hour](figures/results/test_error_by_hour.png)

*Figure 18. Mean absolute error of the frozen A/C model by hour of day, weekdays versus weekends, test week.*

**Where and why it fails.**

1. **Weekday mornings and middays (08:00–14:00).** On weekdays alone, the error rises from 3.4 kW at 08:00 to 5.0 kW at 13:00 (Figure 18). This is when A/C ramps up and its level is least predictable from the timetable.
2. **The 30–60 kW load band.** This is the same ambiguous band shown in Figure 9, where the same total can hide very different amounts of A/C. Above 60 kW the error falls again (2.40 kW), because at those loads A/C is clearly on.
3. **Sudden steps.** In minutes where the building load jumps by more than 5 kW, the error is three times higher (3.50 vs 1.17 kW, n = 227). This is consistent with compressors switching on and off, and with small clock offsets between the separate loggers: a change can appear one minute earlier in the main meter than in the sub-meter.

**Operational consequences.** For peak management, an over-estimate at the peak would make facilities expect more savings from an A/C trim than they would get. An under-estimate would make them overlook A/C as the cause. The model's estimated A/C share of peak load (44.0%) is close to the measured share (45.4%), so neither error dominates at the windows that matter. For after-hours savings, the model over-estimates night-time A/C by 10–27% (Section 6.8), so after-hours savings estimates are somewhat optimistic. Weekend errors (0.15 kW) are negligible. Subgroups with only a few hundred minutes, such as the step changes, rest on four or five days of data, so their exact values should not be over-read.

### 6.8 Explainability and decision usefulness

**O3: What does the A/C model rely on?** We computed exact TreeSHAP values [36], [39] for every test minute. Because many features are exact or near copies of each other, we also summed SHAP within feature groups and ran **grouped** permutation importance, which shuffles a whole group together, five repeats each.

*Table 16. A/C model importance by feature group (test week).*

| Feature group | Mean \|SHAP\| (kW) | Permutation: MAE rise when shuffled (kW, ± SD) |
|---|---|---|
| Power | 4.97 | 3.93 ± 0.04 |
| Harmonics | 1.20 | 2.11 ± 0.02 |
| Power quality | 0.60 | 0.42 ± 0.01 |
| Calendar | 0.44 | 0.19 ± 0.01 |
| Temporal | 0.26 | 0.42 ± 0.01 |

![Figure 19. Top 15 features by mean absolute SHAP](figures/results/shap_global_top15.png)

*Figure 19. The 15 features with the largest mean |SHAP| for the frozen A/C model, test week.*

![Figure 20. SHAP beeswarm](figures/results/shap_beeswarm.png)

*Figure 20. SHAP value of each test minute for the top 12 features. Colour shows the feature value (red = high).*

![Figure 21. Importance by feature group](figures/results/importance_by_group.png)

*Figure 21. Importance by feature group: summed SHAP (left) and grouped permutation importance (right).*

- **Phase-2 real power is by far the strongest feature** (mean |SHAP| 3.98 kW). Phase 2 carries the least non-A/C load (5.6 kW mean, against 8.5 kW and 6.3 kW on phases 1 and 3), so its swings are mostly A/C. It also has the highest correlation with A/C (r = 0.946).
- **Next come the 5th, 7th and 11th current harmonics and THD.** These are the characteristic harmonics of six-pulse rectifiers (orders 6k ± 1) [26], which drive the inverters of VRF compressors. The model is therefore using a physically meaningful A/C signature rather than just "the building is busy". In Figure 20, high 5th-harmonic and THD values (red) push the A/C estimate up. The phase-2 11th harmonic works the other way: *low* values raise the estimate. Because CLEMD reports harmonics as a percentage of the fundamental, a large A/C current raises the fundamental and can lower the relative share of other loads' harmonics. The relationship is therefore not simply "more harmonics = more A/C", and we treat the harmonic group as a signature rather than over-interpret any single order.
- **Calendar features matter little**, so the model does not just follow the timetable. SHAP and permutation importance agree on the top two groups. They disagree slightly on the order of temporal and calendar features, and both of those groups are small.

![Figure 22. Local SHAP explanation of the week's peak](figures/results/shap_local_peak.png)

*Figure 22. Why the model estimates 28.9 kW of A/C during the week's highest 15-minute window (Thursday 19 October, 16:00; building 71.4 kW; measured A/C 30.4 kW; model baseline 5.9 kW).*

**A facilities manager's question: "Why does the model think A/C caused this peak?"** Figure 22 answers it for the week's highest window. Phase-2 power adds +12.4 kW above the 5.9 kW baseline. The 5th-harmonic features and THD add about +3.9 kW together, partly offset by the phase-2 7th harmonic (−0.6 kW). The estimate is 28.9 kW against 30.4 kW measured.

**Limits of the explanation.** SHAP explains what the *model* learned, not what physically causes the load [36]. Credit is split between exact copies (for example `agg_Current3H5` and `ratio_3H5`), which is why we read importance by group. These are associations in one building's data.

**O4: Operating modes and after-hours use.** k-means was run on normalised 24-hour main-meter profiles for the 28 complete days in weeks 2–6. No target was used, so the method works in any building with a main meter.

![Figure 23. Daily operating modes](figures/results/cluster_profiles.png)

*Figure 23. Daily operating modes found by k-means (k = 2): mean hourly profile per mode with individual days (left), and the mode of each day (right).*

*Table 17. Operating modes (k = 2; silhouette 0.74; k = 3: 0.61; k = 4: 0.54).*

| Mode | Days | Weekdays | Building kWh/day | A/C after-hours kWh/day (measured / estimated) | Lighting after-hours kWh/day (measured) |
|---|---|---|---|---|---|
| 0: working day | 16 | 16 | 561 | 26.4 / 32.6 | 33.4 |
| 1: non-working day | 12 | 2 | 268 | 31.7 / 40.2 | 46.1 |

- Silhouette picks **two modes**: working days and non-working days. The two weekdays in the non-working mode are Friday 22 September and **Thursday 28 September 2023, which was the Maulidur Rasul public holiday** [40]. The main meter alone therefore identifies non-working days, with no calendar input.
- With k = 3, a third "light day" mode (375 kWh/day) contains Friday 22 September, Monday 25 September and Friday 29 September, the days around that holiday. This matches the light days we expected in the proposal.
- **Non-working days still use about 32 kWh of A/C and 46 kWh of lighting and sockets a day**, and overnight A/C averages about 1.3 kW. This is the after-hours target in Section 7.3. Measured A/C exists only for weeks 4–6; the estimated column uses the model's out-of-sample estimates, which **run 10–27% high** (week 6: 30.6 estimated vs 27.7 measured kWh/day), so savings built on them are somewhat optimistic.

**Decision usefulness.** The model output is directly usable in two ways: an A/C share for every 15-minute window, which can be checked against the peak, and a daily after-hours A/C total, which can be compared between modes. Section 7 turns these into actions.

### 6.9 Relationship to prior work

CLEMD's authors published no ML results [6], and we found no other disaggregation results on CLEMD, so no direct comparison is possible. The closest Malaysian work, also from UPNM, used a rule-based change-point method to support maximum-demand control [41]. It detects switching events but does not estimate continuous A/C power, and VRF loads with variable-speed compressors break event-based assumptions [19]. Another Malaysian study estimated the CO₂ savings that NILM feedback could produce [42]. In a commercial-building study, Random Forest gave the best cooling-load disaggregation, with a test R² of 96.5% [43]. Our test R² is 0.93, but that study used a different building, period, resolution and split, and is a master's project rather than peer-reviewed work, so **we do not claim to be better or worse**. Our results are consistent with its finding that tree ensembles suit this task. Deep NILM networks perform well on residential appliance data with months of training data [33]; with about three weeks of data from one building, tree models were the more appropriate and more explainable choice.

---

## Chapter 7 Sustainability Insights and Recommendations

> **All UTP figures in this chapter are SCENARIOS for one CLEMD-sized building, built from the model's main-meter A/C estimates on weeks it never trained on (weeks 2, 3 and 6; 20 days). They are not measurements of UTP.** Where week 6's sub-meter exists, each estimate is checked against it.

### 7.1 Link findings to the Grand Challenge

**Energy Security, SDG 7 (Target 7.3).** The pathway from model output to sustainability outcome is:

> **Main-meter data (already on UTP's i-BMS) → model estimates A/C kW every minute → facilities see that A/C sets the peak, and when → demand-triggered A/C trim and after-hours schedules → lower maximum demand (kW, RM) and fewer kWh → lower Scope 2 emissions (SDG 13).**

**The key evidence: the main meter alone shows who sets the peak.** In the test week's top-5% demand windows, the model put A/C at **44.0%** of building load, against **45.4%** measured. It put lighting at 8.3%, against 9.6% measured (Figure 24). All of these windows fell on weekdays between 08:00 and 17:00. So, without any sub-meter, facilities can be told that **A/C sets the peak, on weekday working hours**.

![Figure 24. Who sets the peak](figures/results/scenario_peak_drivers.png)

*Figure 24. Share of building load in the test week's top-5% demand windows: measured by sub-meters versus estimated from the main meter only.*

**Solar timing: the proposal's idea does not hold.** UTP's rooftop PV generates from about 08:00 to 18:00. 77% of the estimated A/C energy (87% of measured A/C energy in weeks 4–6) already falls in those hours, so A/C is already a daytime load that overlaps solar well (Figure 25). Solar output at 14:00–16:00 is still 89% of its 11:00–13:00 level, so the afternoon A/C peak does *not* happen while solar is "falling away", as our proposal assumed.

![Figure 25. Weekday A/C demand versus modelled UTP rooftop solar](figures/proposal/fig10_ac_vs_solar.png)

*Figure 25. Weekday A/C demand (CLEMD, measured) versus modelled UTP rooftop PV output (7.4 MWp × NASA POWER irradiance), each as a percentage of its own daily maximum.*

We tested pre-cooling directly: moving 20% of 14:00–16:00 A/C energy into an earlier window, keeping total energy the same. **Moving it into the solar peak (11:00–13:00) *raises* the period's maximum demand by 5.2 kW** (5.4 kW using measured A/C), because this building is already near its peak at midday, and its daily peaks fall anywhere between 11:00 and 16:59. The best window, 08:00–10:00, when solar is only at 35% of its peak, gives no reduction in the period's maximum (Figure 26). On the peak day, Thursday 19 October, shifting lowers the 14:00–15:45 windows by up to about 7 kW, but the day's maximum (71.4 kW) falls at 16:00, just after the shifted window, so it is unchanged. The building's peak is spread across the afternoon, not confined to one fixed slot. **We therefore withdraw the pre-cooling recommendation** made in the proposal.

![Figure 26. Pre-cooling scenario](figures/results/scenario_precooling.png)

*Figure 26. Pre-cooling scenario on the period's peak weekday (Thursday 19 October 2023): building demand as recorded versus with 20% of 14:00–16:00 A/C moved to 08:00–10:00. The shaded area is mean irradiance at UTP (right axis).*

### 7.2 Actionable recommendations

*Table 18. Recommendations, in priority order.*

| # | Evidence or insight | Stakeholder and action | Expected benefit and condition | When |
|---|---|---|---|---|
| 1 | The main meter recovers A/C's peak share (44.0% vs 45.4%); all peaks fall on weekdays 08:00–17:00 (Section 7.1) | **UTP Property Management:** program the BMS or VRF controllers to trim A/C output (a set-point raise of about 1 °C, or a capacity limit of about 20%) *only* when building demand exceeds a threshold near its 95th percentile (53 kW here) | ≈ 5.8 kW lower maximum demand, **RM 6,200–6,700 a year per building** (estimate, Table 19). *Condition:* occupant comfort trial; threshold set per building | Now: needs only the main meter and controller settings |
| 2 | Pre-cooling into the solar peak raises the maximum by 5.2 kW (Figure 26) | **Property Management and the sustainability office:** do **not** adopt fixed-time pre-cooling; keep A/C timing and focus on limiting the peak | Avoids a scenario penalty of about RM 470–510 a month per building | Now |
| 3 | Non-working days still use ≈ 32 kWh of A/C and ≈ 46 kWh of lighting and sockets a day; overnight A/C ≈ 1.3 kW (Table 17) | **Property Management:** audit after-hours and weekend A/C and lighting schedules; switch off A/C zones on non-working days, using the main-meter day-type clusters to flag abnormal days | ≈ 7.7–9.2 MWh and **5.7–6.8 tCO₂e a year per building** (estimate, Table 20). *Condition:* some night load (servers, refrigerators) is essential | Now: clustering needs no sub-meter |
| 4 | The method works on CLEMD, but UTP uses district cooling and lighting estimates are unreliable (Sections 6.5, 8.1) | **Sustainability office and the registered energy manager:** pilot on one UTP building's i-BMS feed with **2–4 weeks of temporary sub-metering** of its AHU and lighting circuits, then retrain and validate | Turns the scenarios into measured savings; needed before recommendations 1 and 3 are rolled out campus-wide | Next semester; needs budget and approval |
| 5 | Tree models hold up across weeks, but lighting drifted between September and October (Table 14, Section 6.5) | **Energy manager:** retrain monthly and track MAE against any available sub-meter | Keeps estimates reliable as semester use changes | After the pilot |

Recommendations 1–3 can start now, because they only need the main meter and controller changes. Recommendation 4 is the step that allows the benefits to be claimed for UTP.

### 7.3 Quantify impact responsibly

We separate three kinds of number:

- **Measured** in CLEMD: A/C's share of the peak, after-hours energy on the sub-metered weeks, and model errors.
- **Estimated** scenarios for one CLEMD-sized building: Tables 19 and 20.
- **Possible** future UTP benefits: these require the pilot.

We never convert an improvement in accuracy into a claimed energy saving.

**Peak shaving.** Scenario: whenever 15-minute building demand is at or above its 95th percentile (53.1 kW over the 20 unseen days), A/C is trimmed by *x*%. The new maximum is then **recomputed** (a lower peak can be overtaken by another window). Baseline: the highest 15-minute demand over those days, 71.4 kW. Demand charge: RM 89.27–97.06 per kW per month (TNB medium-voltage, standard or time-of-use) [3], [4].

*Table 19. Peak-shaving scenarios (one building; estimate).*

| A/C trim | Max-demand cut, kW | Week 6 check: estimated / measured A/C | RM per month | RM per year |
|---|---|---|---|---|
| 10% | 2.9 | 2.9 / 3.0 | 258–280 | 3,100–3,400 |
| 20% | 5.8 | 5.8 / 6.1 | 516–561 | 6,200–6,700 |
| 30% | 8.7 | 8.7 / 8.1 | 774–841 | 9,300–10,100 |

The model-based cut matches the cut computed from the real sub-meter to within 0.6 kW. In this data the highest window stays the highest after shaving, so the recomputed cut equals the simple upper bound. The proposal's indicative figure (6.3 kW for a 20% trim) used the measured peak of 83.9 kW in weeks 4–6. The figure here uses model estimates on unseen weeks only.

**After-hours savings and carbon.** Scenario: cut after-hours A/C (model estimate) by 50% and after-hours lighting and sockets (measured boards) by 30%. Annualised as 365 × the daily average, and converted with Peninsular Malaysia's 2024 grid emission factor of **0.740 tCO₂e/MWh** (Energy Commission, provisional) [22]. The result is compared with UTP's 20,270 tCO₂e of purchased-electricity emissions [2].

*Table 20. After-hours savings scenarios (one building; estimate); sensitivity to the office-hours definition.*

| Office hours | A/C after-hours kWh/day (est.) | Lighting after-hours kWh/day | Saved kWh/yr | tCO₂e/yr | % of UTP Scope 2 |
|---|---|---|---|---|---|
| 08–17 | 30.8 | 33.1 | 9,243 | 6.8 | 0.034% |
| 08–18 | 27.9 | 31.3 | 8,528 | 6.3 | 0.031% |
| 07–19 | 25.0 | 28.4 | 7,675 | 5.7 | 0.028% |

![Figure 27. Scenario results](figures/report/fig_scenarios.png)

*Figure 27. Scenario results for one CLEMD-sized building (estimates, not measurements). Left: test-week maximum-demand cut from the demand-triggered A/C trim, computed from the model's estimate and checked against the measured A/C. Right: annual savings from the after-hours scenario under three office-hours definitions.*

**Interpretation.** For one building the carbon effect is small, about 6 tCO₂e a year. Its value is that it needs **no new hardware** and can be repeated across every metered building. The peak-shaving value (about RM 6,000 a year per building at a 20% trim) is the stronger financial case, and it is comparable in kind to the RM 1.0 million a year UTP already saves by managing DCP maximum demand [13].

**Assumptions** (all in `scenarios.py`):

- TNB rates come from secondary sources [3], [4] and should be checked against TNB's official schedule [11].
- The emission factor is provisional and will fall as renewables grow [22].
- Annualising 20 days of September–October data ignores semester breaks and seasons.
- The 50% and 30% after-hours cuts are assumed, not tested.
- After-hours A/C estimates run 10–27% high (Section 6.8).
- The PV performance ratio is assumed to be 0.75–0.80, giving a 4.2–4.5 MW mean peak; this affects only the solar magnitudes, not the timing conclusions.
- The demand charge applies at the *campus* meter. Cutting one building's peak lowers UTP's bill only if that building contributes at the time of the campus peak.

### 7.4 Adoption and monitoring

- **What the stakeholder needs.** A 1-minute main-meter feed that includes power per phase, PF, THD and current harmonics. **[Check with UTP facilities]** whether the i-BMS meters record harmonics. If they record only kW and kWh, the model loses its second most important feature group, and accuracy would need to be re-tested.
- **Decision rule.** The demand trigger (near the 95th percentile of the building's 15-minute demand) and the trim size, both set per building.
- **Personnel.** Facilities operators run the trim. The registered energy manager under Act 861 [20] reviews monthly reports.
- **Review.** Monthly comparison of estimated against measured peak, and retraining (Recommendation 5).
- **Comfort and equity.** Trims are small (10–30%) and short. Any UTP trial should collect occupant feedback, because overheated occupants will override the system. Spaces with vulnerable users or sensitive equipment should be excluded.
- **Privacy.** Building-level electricity data can reveal when spaces are occupied [44]. Reports should stay at building or floor level and be aggregated over time, never by individual room or person.
- **False alarms.** A trim triggered at a non-peak moment costs a little comfort but no money, which is an acceptable error direction. Missing the true peak costs a month's demand charge, so the threshold should err low.
- **Monitoring realised benefits.** Track each month's maximum demand and after-hours kWh against the same month in the previous year, and report savings as *measured* only once the pilot provides them.

---

## Chapter 8 Limitations, Conclusion and Future Work

### 8.1 Data and methodological limitations

*Table 21. Limitations, their effect and our response.*

| Limitation | Effect on conclusions | Practical response |
|---|---|---|
| **One building, about three weeks of A/C ground truth, one season (Sep–Oct 2023)** | Results do not generalise to other buildings, semester breaks or hotter months. Six test days give wide CIs | No seasonal claims; CIs reported; Recommendation 4 (pilot) |
| **VRF-cooled building vs UTP's district cooling** | The trained model cannot be copied to UTP; the electrical signature differs (fans and pumps, not compressors) | Transfer the *method*; retrain on a UTP building with temporary sub-metering |
| **Lighting not reliably estimable** | Lighting-based savings rely on *measured* boards, not the model | Recommendations 3 and 5 rest on measured lighting; lighting model not recommended for operational use |
| **Unmetered loads (≈ 55% of energy)** | Limit achievable accuracy | Realistic, since any main meter sees the same mix |
| **Test week was viewed descriptively before the freeze (Section 2.6)** | Small risk that our general view of the data was shaped by it | No tuning or selection used it; freeze record committed before the test run |
| **Duplicated and constant harmonic features (Section 4.2)** | Splits SHAP credit; no effect on accuracy | Group-level interpretation; remove duplicates in future work |
| **Small tuning grid; no feature ablation** | Models may be slightly under-tuned; the value of each feature group is shown by permutation, not by retraining | Stated; future work |
| **After-hours A/C over-estimated by 10–27%** | After-hours savings (Table 20) are optimistic | Stated beside each estimate |
| **Scenario inputs** (secondary-source TNB rates, provisional emission factor, assumed PV ratio, annualisation, office-hours definition) | RM and tCO₂e are indicative only | Ranges and sensitivity shown; all labelled as estimates |
| **Possible logger clock offsets** | Errors at step changes (3.5 kW) | 1-minute averaging; flagged in the error analysis |

### 8.2 Conclusion

This project asked whether a building's main meter, which UTP already has in every building, can show which loads drive its costly demand peaks. Using CLEMD's 1-second data from a Malaysian university building, with its circuit sub-meters as ground truth, the answer for air-conditioning is **yes**.

- **O1 (achieved).** We built a clean 1-minute dataset of 41,680 records from 42 raw files, resolving ten documented quality issues (Table 5), with a pipeline that regenerates every number from raw data.
- **O2 (achieved for A/C; negative result for lighting).** On a sealed test week, the frozen LightGBM model estimated A/C with an MAE of 1.24 kW, 45% better than a timetable baseline and 21% better than Ridge, and 1.52 kW in peak windows. The advantage over Ridge is consistent but not statistically decisive with six test days. Lighting could not be estimated reliably from the main meter.
- **O3 (achieved).** The model relies on phase-2 power and on the 5th, 7th and 11th harmonics characteristic of inverter compressors, which is a physically sensible A/C signature, not the timetable.
- **O4 (achieved).** Clustering the main-meter profiles found working and non-working days, and correctly placed a public holiday among the non-working days. Non-working days still use about 32 kWh of A/C a day.
- **O5 (achieved, with one proposed idea reversed).** From the main meter alone, the model shows that A/C supplies about 44% of peak load. A demand-triggered 20% A/C trim would cut this building's maximum demand by about 5.8 kW (RM 6,200–6,700 a year, estimate). After-hours cuts would save about 6–7 tCO₂e a year per building. Pre-cooling into the solar peak would *raise* the peak and should not be adopted.

The project's contribution to Energy Security is to turn existing meters into a way of finding which load sets the peak, together with a tested rule for limiting it. Its key insight is that the **timing** of the A/C trim matters more than shifting load into solar hours. These savings remain **estimates** until the method is validated on a UTP building.

### 8.3 Prioritised future work

1. **Pilot on one UTP building** (resolves the transfer and district-cooling limitations): use its i-BMS main meter and 2–4 weeks of temporary sub-metering, then retrain and test on a sealed later week using the same protocol.
2. **Confirm the meter capability** (resolves the adoption risk): check whether UTP's meters log harmonics, and if not, re-test the model on power and PF features only.
3. **Longer period** (resolves the single-season limitation): cover a full semester including breaks, to measure drift and set the retraining frequency.
4. **Clean features and run an ablation** (resolves the duplicate-feature and usefulness gaps): remove the constant H1 and duplicated ratio columns and compare feature groups under the same CV.
5. **Comfort-checked trim trial** (resolves the assumed trim response): measure the real kW reduction and occupant response to a 10–20% demand-triggered trim.
6. **Only then** consider more complex models, such as 15-minute-ahead forecasting or sequence models, once more data exists.

---

## References

[1] O. Al-Khadher, A. Mukhtaruddin, F. R. Hashim, M. M. Azizan, H. Mamat, and A. Aqlan, "CLEMD: Circuit-level electrical measurements dataset," figshare, dataset collection, 2024. Accessed: Oct. 17, 2026. [Online]. Available: https://doi.org/10.6084/m9.figshare.c.6946581

[2] Universiti Teknologi PETRONAS, "Sustainability @ UTP." UTP. Accessed: Oct. 17, 2026. [Online]. Available: https://www.utp.edu.my/Pages/Sustainability.aspx

[3] Tanand Technology, "Cut your TNB maximum demand charges with EasiEMS," Jul. 29, 2025. Accessed: Oct. 17, 2026. [Online]. Available: https://www.tanand.com.my/tnb-maximum-demand-easiems/

[4] PlusXnergy, "July 2025 TNB tariff update: What Malaysian businesses need to know," 2025. Accessed: Oct. 17, 2026. [Online]. Available: https://www.plusxnergy.com/july-2025-tnb-tariff-update-what-malaysian-businesses-need-to-know/

[5] Universiti Teknologi PETRONAS, "Energy cost optimisation journey." UTP. Accessed: Oct. 17, 2026. [Online]. Available: https://www.utp.edu.my/Pages/Sustainability/Low%20Carbon%20Campus/Energy-Cost-Optimisation-Journey.aspx

[6] O. Al-Khadher, A. Mukhtaruddin, F. R. Hashim, M. M. Azizan, H. Mamat, and A. Aqlan, "CLEMD, a circuit-level electrical measurements dataset for electrical energy management," *Sci. Data*, vol. 11, Art. no. 594, 2024, doi: 10.1038/s41597-024-03433-7.

[7] S. B. Mohd Ali, M. Hasanuzzaman, N. A. Rahim, M. A. A. Mamun, and U. H. Obaidellah, "Analysis of energy consumption and potential energy savings of an institutional building in Malaysia," *Alexandria Eng. J.*, vol. 60, no. 1, pp. 805–820, 2021, doi: 10.1016/j.aej.2020.10.010.

[8] Economic Research Institute for ASEAN and East Asia, "Fundamentals," in *Technical Guideline for Energy Efficiency in Commercial Buildings*. Jakarta, Indonesia: ERIA, 2021, ch. 2. Accessed: Oct. 17, 2026. [Online]. Available: https://www.eria.org/uploads/media/Research-Project-Report/2021-14-Technical-Guideline-Energy-Efficiency-Commercial-Buildings/8_ch.2-Fundamentals.pdf

[9] R. Saidur, "Energy consumption, energy savings, and emission analysis in Malaysian office buildings," *Energy Policy*, vol. 37, no. 10, pp. 4104–4113, 2009, doi: 10.1016/j.enpol.2009.04.052.

[10] Tenaga Nasional Berhad, "Maximum demand." TNB. Accessed: Oct. 17, 2026. [Online]. Available: https://www.tnb.com.my/commercial-industrial/maximum-demand

[11] Tenaga Nasional Berhad, "New electricity schedule: Fairer rates for over 23.6m customers," press clipping, Jun. 23, 2025. Accessed: Oct. 17, 2026. [Online]. Available: https://www.tnb.com.my/assets/newsclip/23062025a.pdf

[12] Tenaga Nasional Berhad, "Tariff reform to reshape power sector," press clipping, Jul. 9, 2025. Accessed: Oct. 17, 2026. [Online]. Available: https://www.tnb.com.my/assets/newsclip/09072025a.pdf

[13] Universiti Teknologi PETRONAS, "District cooling plant (DCP) optimization." UTP. Accessed: Oct. 17, 2026. [Online]. Available: https://www.utp.edu.my/Pages/Sustainability/Low%20Carbon%20Campus/District%20Cooling-Plant-(DCP)-Optimization.aspx

[14] Universiti Teknologi PETRONAS, "UTP and reNIKOLA partner to enhance solar photovoltaic efficiency," press release, Jul. 13, 2024. Accessed: Oct. 17, 2026. [Online]. Available: https://utp.edu.my/Pages/Media/Press-Release/2024/UTP-and-reNIKOLA-Partner-to-Enhance-Solar-Photovoltaic-Efficiency-.aspx

[15] FocusM, "Gentari accelerates Universiti Teknologi PETRONAS' on-site campus solarisation capacity to 7.7MW," *Focus Malaysia*, Aug. 29, 2026. Accessed: Oct. 17, 2026. [Online]. Available: https://focusmalaysia.my/?p=255924

[16] Universiti Teknologi PETRONAS, "Sustainable campus in action." UTP. Accessed: Oct. 17, 2026. [Online]. Available: https://www.utp.edu.my/Pages/Sustainability/Sustainable%20Campus%20in%20Action.aspx

[17] G. W. Hart, "Nonintrusive appliance load monitoring," *Proc. IEEE*, vol. 80, no. 12, pp. 1870–1891, Dec. 1992, doi: 10.1109/5.192069.

[18] A. Zoha, A. Gluhak, M. A. Imran, and S. Rajasegarar, "Non-intrusive load monitoring approaches for disaggregated energy sensing: A survey," *Sensors*, vol. 12, no. 12, pp. 16838–16866, 2012, doi: 10.3390/s121216838.

[19] N. Batra, O. Parson, M. Berges, A. Singh, and A. Rogers, "A comparison of non-intrusive load monitoring methods for commercial and residential buildings," 2014, *arXiv:1408.6595*, doi: 10.48550/arXiv.1408.6595.

[20] Energy Commission of Malaysia, "Energy Efficiency and Conservation Act 2024 (Act 861)," 2025. Accessed: Oct. 17, 2026. [Online]. Available: https://st.gov.my/node/2491

[21] United Nations General Assembly, "Transforming our world: The 2030 Agenda for Sustainable Development," A/RES/70/1, 2015. Accessed: Oct. 17, 2026. [Online]. Available: https://sdgs.un.org/2030agenda

[22] Energy Commission of Malaysia, "Grid emission factor (GEF) in Malaysia, 2022–2024 (provisional)," 2026. Accessed: Oct. 17, 2026. [Online]. Available: https://myenergystats.st.gov.my/documents/d/guest/grid-emission-factor-gef-in-malaysia-2022-2024-provisional-

[23] Ministry of Economy Malaysia, "National energy transition roadmap," 2023. Accessed: Oct. 17, 2026. [Online]. Available: https://www.ekonomi.gov.my/

[24] NASA Langley Research Center, "POWER Project hourly data, version 2.x," dataset, 2026. Accessed: Oct. 17, 2026. [Online]. Available: https://power.larc.nasa.gov/

[25] C. Bergmeir and J. M. Benítez, "On the use of cross-validation for time series predictor evaluation," *Inf. Sci.*, vol. 191, pp. 192–213, 2012, doi: 10.1016/j.ins.2011.12.028.

[26] *IEEE Recommended Practice and Requirements for Harmonic Control in Electric Power Systems*, IEEE Std 519-2014, 2014, doi: 10.1109/IEEESTD.2014.6826459.

[27] A. E. Hoerl and R. W. Kennard, "Ridge regression: Biased estimation for nonorthogonal problems," *Technometrics*, vol. 12, no. 1, pp. 55–67, 1970, doi: 10.1080/00401706.1970.10488634.

[28] L. Breiman, "Random forests," *Mach. Learn.*, vol. 45, no. 1, pp. 5–32, 2001, doi: 10.1023/A:1010933404324.

[29] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining*, 2016, pp. 785–794, doi: 10.1145/2939672.2939785.

[30] G. Ke *et al.*, "LightGBM: A highly efficient gradient boosting decision tree," in *Adv. Neural Inf. Process. Syst. 30*, 2017, pp. 3146–3154.

[31] J. MacQueen, "Some methods for classification and analysis of multivariate observations," in *Proc. 5th Berkeley Symp. Math. Statist. Probab.*, vol. 1, 1967, pp. 281–297.

[32] P. J. Rousseeuw, "Silhouettes: A graphical aid to the interpretation and validation of cluster analysis," *J. Comput. Appl. Math.*, vol. 20, pp. 53–65, 1987, doi: 10.1016/0377-0427(87)90125-7.

[33] J. Kelly and W. Knottenbelt, "Neural NILM: Deep neural networks applied to energy disaggregation," in *Proc. 2nd ACM Int. Conf. Embedded Syst. Energy-Efficient Built Environ.*, 2015, pp. 55–64, doi: 10.1145/2821650.2821672.

[34] W. McKinney, "Data structures for statistical computing in Python," in *Proc. 9th Python Sci. Conf.*, 2010, pp. 56–61, doi: 10.25080/Majora-92bf1922-00a.

[35] F. Pedregosa *et al.*, "Scikit-learn: Machine learning in Python," *J. Mach. Learn. Res.*, vol. 12, pp. 2825–2830, 2011.

[36] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," in *Adv. Neural Inf. Process. Syst. 30*, 2017, pp. 4765–4774.

[37] J. D. Hunter, "Matplotlib: A 2D graphics environment," *Comput. Sci. Eng.*, vol. 9, no. 3, pp. 90–95, 2007, doi: 10.1109/MCSE.2007.55.

[38] H. R. Künsch, "The jackknife and the bootstrap for general stationary observations," *Ann. Statist.*, vol. 17, no. 3, pp. 1217–1241, 1989, doi: 10.1214/aos/1176347265.

[39] S. M. Lundberg *et al.*, "From local explanations to global understanding with explainable AI for trees," *Nat. Mach. Intell.*, vol. 2, no. 1, pp. 56–67, 2020, doi: 10.1038/s42256-019-0138-9.

[40] Bahagian Kabinet, Perlembagaan dan Perhubungan Antara Kerajaan, Jabatan Perdana Menteri, "Senarai hari kelepasan am persekutuan dan negeri bagi tahun 2023," 2022. **[TODO: add URL and access date after checking the official list.]**

[41] A. Mukhtaruddin, F. R. Hashim, M. K. Awang, H. Mamat, and H. Zakaria, "Development of site-specific non-intrusive load monitoring for maximum demand control," *Indones. J. Electr. Eng. Comput. Sci.*, vol. 23, no. 3, pp. 1814–1824, 2021, doi: 10.11591/ijeecs.v23.i3.pp1814-1824.

[42] K.-K. Kee, Y. S. Lim, J. Wong, and K. H. Chua, "Impact of nonintrusive load monitoring on CO2 emissions in Malaysia," *Bull. Electr. Eng. Inform.*, vol. 10, no. 4, pp. 1803–1810, 2021, doi: 10.11591/eei.v10i4.2979.

[43] M. L. Moreno Guzmán, J. L. Munévar Diaz, and J. J. Jaimes Otero, "Desarrollo de un modelo de análisis de carga no intrusiva para eficiencia energética basado en técnicas de machine learning," M.S. applied project, Pontificia Universidad Javeriana Cali, Cali, Colombia, 2026. Accessed: Oct. 17, 2026. [Online]. Available: https://vitela.javerianacali.edu.co/server/api/core/bitstreams/b3acca3f-2fec-4044-a063-2bf9a1b8788c/content

[44] M. Wickramathilaka, M. P. Abdullah, M. Y. Hassan, and H. Abdullah, "Detection of occupancy status from internet connectivity for non-intrusive load monitoring," *Indones. J. Electr. Eng. Comput. Sci.*, vol. 30, no. 3, pp. 1678–1688, 2023, doi: 10.11591/ijeecs.v30.i3.pp1678-1688.

---

## Appendix A Data Dictionary and Quality Checks

*Table A1. All 98 model features (generated in `results/feature_dictionary.csv`).*

| Group | Features |
|---|---|
| Power (15) | `agg_Real_Power1–3`, `agg_Apparent_Power1–3`, `agg_Reactive_Power1–3` (1-min means, W/VA/VAR); `agg_p_kw`, `agg_q_kvar`, `agg_s_kva` (totals); `agg_p_kw_std`, `agg_p_kw_min`, `agg_p_kw_max` (within-minute) |
| Power quality (16) | `agg_Voltage1–3`, `agg_VoltageN` (V); `agg_Current1–3`, `agg_CurrentN` (A); `agg_Frequency` (Hz); `agg_PF1–3`; `agg_THD1–3`, `agg_THDN` (%) |
| Harmonics (53) | `agg_Current{1,2,3,N}H{1,3,5,7,9,11,13,15}` (% of fundamental; H1 = 100 constant); `ratio_{1,2,3}H{3,5,7,9,11,13,15}` (= Hn/H1, exact copies ÷ 100) |
| Temporal (9) | `p_lag1`, `p_lag5`, `p_lag15`, `p_lag60`; `p_roll15_mean`, `p_roll15_std`, `p_roll60_mean`, `p_roll60_std`; `p_diff1` |
| Calendar (5) | `hour_sin`, `hour_cos`, `dayofweek`, `weekend`, `office_hours` |

*Table A2. Clean 1-minute records per CLEMD week.*

| Week | Dates (2023) | Minutes | Building mean kW | A/C mean kW | Lighting mean kW | Use |
|---|---|---|---|---|---|---|
| 2 | 22–26 Sep | 7,211 | 14.0 | (no file) | 2.59 | Lighting train; clustering; out-of-sample A/C estimates |
| 3 | 28 Sep–3 Oct | 8,651 | 15.7 | (no file) | 2.44 | Same as week 2 |
| 4 | 5–10 Oct | 8,516 | 18.8 | 4.66 | 2.64 | A/C and lighting train (outage removed) |
| 5 | 12–17 Oct | 8,651 | 22.1 | 7.05 | 3.01 | A/C and lighting train |
| 6 | 19–24 Oct | 8,651 | 19.8 | 6.51 | 3.07 | **Sealed test** |

Redundant pairs (|r| > 0.98, weeks 2–5): `results/redundant_feature_pairs.csv` (130 pairs).

## Appendix B Model Settings, Tuning Ranges and Supplementary Results

**Search space** (`train.py`, `MODELS`). Ridge: α ∈ {0.1, 1, 10, 100}. Random Forest (200 trees, max_features 0.33): max_depth ∈ {None, 12} × min_samples_leaf ∈ {1, 5}. XGBoost (400 trees, subsample 0.8, colsample_bytree 0.8): max_depth ∈ {4, 6} × learning_rate ∈ {0.03, 0.1}. LightGBM (400 trees, subsample 0.8, colsample_bytree 0.8): num_leaves ∈ {15, 63} × learning_rate ∈ {0.03, 0.1}. All with `random_state=0`.

*Table B1. Cross-validation results, best configuration per model (mean of four expanding-window folds, training weeks only).*

| Target | Model | CV MAE | CV RMSE | CV R² | CV peak MAE | Fit time (s) |
|---|---|---|---|---|---|---|
| A/C | Time of day | 2.994 | 4.568 | 0.742 | 7.664 | 0.03 |
| A/C | Ridge (α 100) | 2.275 | 3.217 | 0.863 | 4.182 | 0.02 |
| A/C | Random Forest | 1.027 | 2.416 | 0.924 | 3.643 | 7.35 |
| A/C | XGBoost | 1.036 | 2.344 | 0.929 | 2.536 | 1.45 |
| A/C | **LightGBM (frozen)** | **0.987** | 2.365 | 0.929 | 2.587 | 1.98 |
| Lighting | Time of day | 0.429 | 0.753 | 0.580 | 1.456 | 0.05 |
| Lighting | **Ridge (α 100, frozen)** | **0.360** | 0.473 | 0.852 | 0.789 | 0.05 |
| Lighting | Random Forest | 0.363 | 0.544 | 0.811 | 0.896 | 17.24 |
| Lighting | XGBoost | 0.365 | 0.543 | 0.813 | 0.911 | 1.58 |
| Lighting | LightGBM | 0.374 | 0.560 | 0.800 | 0.821 | 2.64 |

*Table B2. A/C CV MAE per fold (kW), best configuration.*

| Model | Fold 1 | Fold 2 | Fold 3 | Fold 4 | SD |
|---|---|---|---|---|---|
| Time of day | 3.67 | 3.05 | 2.33 | 2.93 | 0.55 |
| Ridge | 3.00 | 3.01 | 1.37 | 1.72 | 0.85 |
| Random Forest | 1.09 | 1.21 | 0.73 | 1.08 | 0.21 |
| XGBoost | 0.84 | 1.26 | 0.81 | 1.23 | 0.24 |
| LightGBM | 0.85 | 1.19 | 0.75 | 1.16 | 0.22 |

Full per-fold results for all 136 fits: `results/cv_results.csv`. Freeze record: `results/freeze.json`.

## Appendix C Additional Results

- Lighting Ridge standardised coefficients: `results/ridge_light_coefficients.csv` (largest: THD phase 2, −0.83 kW per SD).
- Local SHAP values at the week's peak: `results/shap_local_peak_ac.csv`.
- Per-day cluster assignments and energy: `results/cluster_days.csv`. k-search: `results/cluster_k_search.csv`.
- Pre-cooling windows tested (20% of 14:00–16:00 A/C moved): 08–10 → 0.0 kW; 09–11 → 0.0 kW; 10–12 → −5.2 kW; 11–13 → −5.2 kW (negative = peak raised). Source: `results/scenarios.json`.
- Out-of-sample predictions for weeks 2, 3 and 6: `results/predictions.csv`.

## Appendix D Implementation Instructions

**Repository:** `ML-ASSIGNMENT/`. This report is `FINAL_REPORT.md` at its root, and all figure links are relative to it. **[TODO: add the repository link or zip file name used for submission.]**

1. **Environment.** Python 3.11 (tested on 3.11.17, Linux/WSL2).
   ```bash
   uv venv .venv && uv pip install -r requirements.txt
   # or: python -m venv .venv && .venv/bin/pip install -r requirements.txt
   ```
2. **Data** (≈ 7 GB, not in git). Download the six CLEMD weekly folders from https://doi.org/10.6084/m9.figshare.c.6946581 into `data/clemd/<weekly folder>/*.csv`, and the NASA POWER hourly file for UTP (4.385 N, 100.979 E, October 2023, UTC) to `data/external/nasa_power_utp_oct2023_utc.csv`.
3. **Run everything** (about 12 minutes): `./run_all.sh` (or `PY=python ./run_all.sh`). The steps must run in order: `prepare_data → features → train → evaluate → explain → cluster → scenarios → make_figures → build_dashboard`.
4. **Expected outputs.** `results/*.csv|json` (all numbers in this report), `figures/proposal/`, `figures/results/` and `figures/report/` (every report figure is mapped to its file in Table D1), and `dashboard/index.html` (the presentation).
5. **Checks.** Every script ends with `assert` self-checks; a run with no traceback means the outputs are consistent. All randomness is seeded (`random_state=0`, `default_rng(0)`). Rerunning `train.py` keeps the committed `freeze.json` and asserts that the rerun reproduces the frozen choice.
6. **Rule.** Week 6 is the sealed test week: `features.load()` excludes it unless `include_test=True`, which only `evaluate.py`, `explain.py` and `cluster.py` use, after the freeze.

*Table D1. Report figures and the files that produce them (all under `figures/`).*

| Figure | File | Script |
|---|---|---|
| 1 | `proposal/fig02_energy_vs_peak_share.png` | `make_figures.py` |
| 2 | `proposal/fig01_workflow.png` | `make_figures.py` |
| 3 | `proposal/fig03_data_availability.png` | `make_figures.py` |
| 4 | `report/fig_target_distributions.png` | `report_figures.py` |
| 5 | `proposal/fig04_week6_timeseries.png` | `make_figures.py` |
| 6 | `proposal/fig05_daily_profile.png` | `make_figures.py` |
| 7 | `proposal/fig06_ac_heatmap.png` | `make_figures.py` |
| 8 | `proposal/fig07_feature_correlation.png` | `make_figures.py` |
| 9 | `proposal/fig08_agg_vs_ac.png` | `make_figures.py` |
| 10 | `report/fig_prep_flow.png` | `report_figures.py` |
| 11 | `proposal/fig09_split.png` | `make_figures.py` |
| 12 | `report/fig_model_comparison.png` | `report_figures.py` |
| 13 | `report/fig_consistency.png` | `report_figures.py` |
| 14 | `report/fig_lighting_test.png` | `report_figures.py` |
| 15 | `results/test_week_timeseries.png` | `evaluate.py` |
| 16 | `results/test_pred_vs_actual.png` | `evaluate.py` |
| 17 | `report/fig_residuals.png` | `report_figures.py` |
| 18 | `results/test_error_by_hour.png` | `evaluate.py` |
| 19 | `results/shap_global_top15.png` | `explain.py` |
| 20 | `results/shap_beeswarm.png` | `explain.py` |
| 21 | `results/importance_by_group.png` | `explain.py` |
| 22 | `results/shap_local_peak.png` | `explain.py` |
| 23 | `results/cluster_profiles.png` | `cluster.py` |
| 24 | `results/scenario_peak_drivers.png` | `scenarios.py` |
| 25 | `proposal/fig10_ac_vs_solar.png` | `make_figures.py` |
| 26 | `results/scenario_precooling.png` | `scenarios.py` |
| 27 | `report/fig_scenarios.png` | `report_figures.py` |

## Appendix E Team Contribution Record

All five members contributed equally. Each member led one stage of the ML lifecycle, reviewed another member's stage, and drafted and proofread their chapters of this report. Every piece of code was checked by a second member, and the final pipeline was rerun from raw data before submission.

*Table E1. Team contribution record.*

| Member and ID | Lead responsibility | Review and support | Report chapters | Share |
|---|---|---|---|---|
| Izzatul Najwa Binti Che Zaki (22007298) | Data acquisition, loader, data-quality log, cleaned dataset (`prepare_data.py`) | Feature engineering; leakage checks | Ch. 2 Data Understanding; Ch. 3 Preprocessing | 20% |
| Nurul Izzati Binti Razali (22007868) | Feature engineering, feature dictionary, redundancy check, baselines (`features.py`) | Model tuning; data-quality log | Ch. 4 Feature Engineering; Ch. 1 Introduction | 20% |
| Daphne Binti Douglas (22006239) | Tree models, hyperparameter tuning, model freeze, test evaluation (`train.py`, `evaluate.py`) | Error analysis; baselines | Ch. 5 Methodology; Ch. 6.1–6.4 Results | 20% |
| Siti Nurmasyitah Binti Ab Aziz (22007601) | SHAP, permutation importance, error analysis, clustering (`explain.py`, `cluster.py`) | Test evaluation; scenario checks | Ch. 6.5–6.9 Discussion; Ch. 8 Limitations and Conclusion | 20% |
| Sharvin A/L Kanesan (22006930) | UTP scenarios, integration, figures, dashboard (`scenarios.py`, `report_figures.py`, `build_dashboard.py`) | Clustering; reproducibility rerun | Ch. 7 Sustainability; Executive Summary; Appendices | 20% |
