# Changes needed in `ML Project Report Template.pdf` (70 pages)

Checked page by page against `docs/ML Project Report Template (1).docx`, `docs/TEB3123_Final_Report_Guide 2.jpg`, `ML-ASSIGNMENT/FINAL_REPORT.md` and `ML-ASSIGNMENT/results/*.csv`.
Page numbers are the PDF's own footer numbers. Fix the items in **Priority 1** first: a marker will see them straight away.

**How the two files fit together**

| File | Use it for |
|---|---|
| `REPORT_CHANGES.md` (this file) | **What to change**, page by page, with the exact old and new text. Share it with the team and work through it in the Word file |
| `ML-ASSIGNMENT/FINAL_REPORT.md` | **The complete updated report.** It follows the PDF section by section (same wording, chapters, figure and table numbers) with every change below already applied. Open the same section number there to see any part in full context |

Both use the same numbering: Figures 1–27 and Tables 1–23, plus three new tables (9b ablation, 11b implementation details, 11c measures) that slot in without renumbering anything else.

**New since the first version of this file:** a feature-group ablation was added to the code (`ablation.py`, results in `results/ablation_cv.csv`). It closes the report's main method gap ("no ablation") and answers the 7.4 meter question with evidence. Paste-ready text is in **Section D**.

Legend: 🔴 must fix (wrong fact, template leftover, or missing requirement) · 🟠 should fix (broken reference, wrong label) · 🟡 polish (grammar, wording)

---

## Priority 1: things that cost marks immediately

| # | Page | Problem | Fix |
|---|---|---|---|
| 1 | 2 | 🔴 Template instruction page left in: "How to Use This Report Template", "Requirements", "Assessment alignment", "Recommended presentation conventions" | Delete the whole page |
| 2 | 3 | 🔴 Heading "Report Structure and Executive Summary" is template text; working notes **"Table of Content (belum)"** and **"Executive summary (belum edit)"** are visible | Delete the template heading; heading should just be "Executive Summary"; delete both "(belum …)" notes |
| 3 | 4 | 🔴 Template instruction page "Required One Page Project Infographic" left in. It also sits **between** the executive summary and the infographic, which breaks the rule "infographic immediately after the executive summary" | Delete the whole page |
| 4 | — | 🔴 **No table of contents**, no list of figures, no list of tables | After the infographic: Word → References → Table of Contents (built from Heading 1/2 styles). Then Insert Table of Figures for "Figure" and again for "Table". Update all fields before exporting |
| 5 | 68–70 | 🔴 Template leftovers: heading "Appendices and Final Submission Checklist", "Suggested appendices" list, "Suggested team contribution record" table with `[Name and ID]` placeholders, and the "Before submitting in Week 10" checklist | Delete all of it. Replace with the real appendices (item 6) |
| 6 | 68 | 🔴 **Only Appendix B exists.** The body refers to Appendix A (p12, p26) and Appendix D (p9), and the brief requires "implementation instructions" | Paste Appendices A, C, D and E from **Section F** below. **Appendix D (implementation instructions)** and **Appendix E (team contribution)** matter most |
| 7 | every page | 🔴 Footer says **"TEB3123 \| Final Report Guide \| N"**. Cover subtitle says "Student Submission Template". PDF title metadata says "Final Report Guidelines and Template" | Footer → "TEB3123 \| Group 8 Final Report \| N". Delete the "Student Submission Template" line. File → Info → Title → the project title |
| 8 | 56 | 🔴 `[Check with UTP facilities]` placeholder in 7.4 | Replace all of 7.4 with the rewrite in **Section A** below |
| 9 | 67 | 🔴 Ref [40] still says `[TODO: add URL and access date …]` | Find the official 2023 list on kabinet.gov.my (BKPP, Prime Minister's Department), then add its URL and your access date. If you can't find it, cite a state government holiday list for 2023 that shows Maulidur Rasul on 28 Sep (Thursday) |
| 10 | 3 | 🟠 Executive summary CI "0.57–1.88" doesn't match Table 6.2 (0.56–1.87). `results/test_metrics.csv` gives 0.565–1.875 | Change to **0.56–1.87** |

---

## Priority 2: figure and table numbering (broken cross-references)

Chapters 1–4 and 7–8 number things in one running sequence (Figure 1–27, Table 1–23). **Chapters 5–6 switch to chapter numbering** (Figure 5.1, Table 6.2 …), but their text still says "Figure 11", "Table 12" and so on. Every one of those references now points at nothing.

**Fix:** go back to running numbers in Chapters 5–6 (easiest, because the text already uses them):

| Page | Current caption | Should be | Text that refers to it |
|---|---|---|---|
| 30 | Table 5.1 | **Table 10** | "(Table 10)" ✓ |
| 31 | Figure 5.1 | **Figure 11** | "Split (Figure 11)" |
| 32 | Table 5.2 | **Table 11** | "shown in Table 5.2" → "Table 11" |
| 33 | Table 5.3 | **Table 11b** ("Implementation details") | — |
| 34 | Table 6.1 | **Table 11c** ("Measures by task") | — |
| 35 | Table 6.2 | **Table 12** | p28, p29, p36 |
| 35 | Table 6.3 | **Table 13** | p36 |
| 36 | Figure 6.1 | **Figure 12** | p36 |
| 36 | Table 6.4 | **Table 14** | p37, p38 |
| 37 | Figure 6.2 | **Figure 13** | p37 |
| 39 | Figure 6.3 | **Figure 14** | p40 |
| 40 | Figure 6.4 | **Figure 15** | p40, p42 |
| 41 | Figure 6.5 | **Figure 16** | p39 |
| 41 | Figure 6.6 | **Figure 17** | p42 |
| 42 | Table 6.5 | **Table 15** | p42 |
| 43 | Figure 6.7 | **Figure 18** | p43 |
| 44 | Table 6.6 | **Table 16** | p28 |
| 44 | Figure 6.8 | **Figure 19** | — |
| 45 | Figure 6.9 | **Figure 20** | p46 |
| 45 | Figure 6.10 | **Figure 21** | — |
| 46 | Figure 6.11 | **Figure 22** | p46 |
| 47 | Figure 6.12 | **Figure 23** | — |
| 47 | Table 6.7 | **Table 17** | p48, p53 |

Also:
- 🟠 **Missing table captions**: objectives table (p8 → "Table 1. Objectives and where each is evidenced."), outcomes table (p9 → "Table 2. Proposed outcomes versus what was achieved."), provenance (p11 → "Table 3. Dataset provenance."), key variables (p12 → "Table 4. Key variables."), feature groups header (p26: the first column header "Group (count)" is missing).
- 🟠 Using Word's **Insert Caption** for every figure and table means numbers update automatically, and the list of figures and tables (item 4) builds itself.
- 🟠 After renumbering, check the evidence column of the objectives table (p8) still matches: "Tables 12–14; Figures 12–18", "Figures 19–22; Table 16", "Figure 23; Table 17", "Tables 18–20; Figures 24–27".

---

## Priority 3: wrong facts or wrong meaning (introduced while paraphrasing)

| # | Page | Current text | Problem | Replace with |
|---|---|---|---|---|
| 1 | 6 | "Most of the UTP'S purchased electricity has contributed to Scope 1 and 2 carbon emissions that accounts for 20.27 out of 20.33 million kgCO₂e" | Meaning reversed | "Purchased electricity accounts for 20.27 of UTP's 20.33 million kgCO₂e of Scope 1 and 2 emissions a year [2], so almost every tonne of CO₂ the campus emits comes from the grid." |
| 2 | 6 | "UTP has already met more than a aquarter campus demand, approximately with the capacity of 7.7 MWp after the second phase [14][15]" | Mixes two facts | "A 7.4 MWp rooftop solar system meets more than a quarter of campus demand [14], and a second phase brought rooftop capacity to 7.7 MW [15]." |
| 3 | 11 | "its lighting and A/C energy shares (30.1% and 14.4%) are comparable to … (34% and 18%)" | A/C and lighting swapped | "its **A/C and lighting** energy shares (30.1% and 14.4%) are close to those of the Universiti Malaya institutional building (34% and 18%) [7]." |
| 4 | 13 | "CLEMD building is cooled by rooftop VRF units **similar to UTP** that served by a district cooling plant [13] … Only methods of the **forecasting** are applied to UTP." | Opposite of the truth (UTP is *different*), and the project is not forecasting | "The CLEMD building is cooled by rooftop VRF units whose compressors sit on the building's own supply. Much of UTP is instead served by a district cooling plant [13], where a building meter sees fans and pumps rather than compressors. The trained model therefore cannot be copied to UTP; only the **method** transfers (Section 8.1)." |
| 5 | 9 | "B. SDG 13 : Regenerative Futures" | SDG 13 is Climate Action; Regenerative Futures is the Grand Challenge | "B. Secondary alignment: Regenerative Futures, SDG 13 (Climate Action)" |
| 6 | 15 | "both **models** are right skewed" | They're targets, not models | "both **targets** are right-skewed (skewness 1.88 for A/C, 1.72 for lighting and sockets)" |
| 7 | 29 | "capable of 45% greater **precision** than the timetabling method" | Precision is a classification metric | "cuts the average error (MAE) by 45% compared with the time-of-day baseline (Table 12)" |
| 8 | 29 | "The end-to-end process is implemented in nine scripts" (only 8 items listed) | Count wrong; `report_figures.py` and the new ablation step missing | Replace the list with the ten steps in `FINAL_REPORT.md` §5.1 (adds 4. `ablation` and 9. `make_figures` and `report_figures`) |
| 9 | 30 | "If the model goes below this point, then the electrical attributes … are redundant" | Reversed | "If a model **cannot beat** this baseline, the main meter's electrical signals add nothing beyond the timetable." |
| 10 | 30 | "high total power … during working hours equals **chilled water supply**" | CLEMD is VRF; no chilled water | "…high total power + strong 5th harmonic + office hours = **A/C on**" |
| 11 | 35 | Lighting table (6.3 → Table 13): "**LightGBM (frozen)**" | The frozen lighting model is **Ridge** | Ridge row → "**Ridge (frozen)**"; LightGBM row → "LightGBM" |
| 12 | 37 | "we chose LightGBM for **operational deployment**" | Overclaim: nothing was deployed | "we chose LightGBM as the final A/C model" |
| 13 | 43 | "The 30–60 kW load band: … the same overall value, but in which there is a much higher amount of A/C. At loads greater than 60 kW the error is again (2.40 kW), this being a high amount of A/C." | Meaning lost | "This is the ambiguous band in Figure 9, where the same building total can hide very different amounts of A/C. Above 60 kW the error **falls** again (2.40 kW), because at those loads A/C is clearly on." |
| 14 | 44 | "Subgroups that have **fewer than 100 minutes** … like step changes" | Step changes have n = 227 | "Subgroups with only a few hundred minutes, such as the step changes (n = 227), rest on four or five days of data…" |
| 15 | 44 | Table 6.6: "Power quality 0.60 **360** 0.42 ± 0.01" | Stray "360" | Delete "360" |
| 16 | 49 | Step 4: "They can **shut down** A/C for short periods during high demand and off hours." | The recommendation is a 10–30% trim, not a shutdown | "They can trim A/C output briefly when demand is high, and switch off unneeded A/C after hours." |
| 17 | 55 | Table 20, row 07–19: "% of UTP Scope 2 = **0.031%**" | Should be 0.028% (`results/scenarios.json`, RESULTS.md) | **0.028%** |
| 18 | 61 | "Objective 5: **urn** estimates…" | Typo | "Turn" |
| 19 | 34 | 6.1 lists only MAE, RMSE, R² and silhouette, but the tables report **peak-window MAE, energy-share error and NDE** without defining them | Template: "define what they measure"; peak-window MAE is the most decision-relevant measure | Paste the definitions from `FINAL_REPORT.md` §6.1 (peak-window MAE, energy-share error, NDE) and add "where *y* = measured, *ŷ* = estimate, *n* = number of minutes" under the equations |
| 20 | 8 | "The first publicly accessible dataset in Malaysia … is called CLEMD. No machine learning disaggregation results … have been published" | No citation | Add **[6]** after both sentences |
| 21 | 52–53 | Recommendations table has no "#" column, but the text says "Recommendations 1–3", "Recommendation 4", "Recommendation 5" | References point at nothing | Add a first column "#" numbered 1–5, in the same order as `FINAL_REPORT.md` Table 18 |
| 22 | 32 | Table 5.2 lost the note saying which values were selected by validation | Template 5.4: "distinguish default parameters from values selected through validation" | Caption: "Final settings. Values in the 'Selected' columns were chosen by cross-validation; 'Fixed settings' are defaults we set." |
| 23 | 61 | 8.3 item 2 "Check what UTP's meters record" | Should match the new 7.4 | Replace with the text in **Section B** below |

---

## Priority 4: layout

| Page | Problem | Fix |
|---|---|---|
| 22–23 | 🔴 Table 7 is cut off at the left margin: the "Step" column is mostly off the page (only "g", "ks", "nd outage" are visible) | Table Properties → Preferred width 100%, AutoFit to window; restore the Step labels: Blank rows / Date parsing / Units / Missing circuits / Missing minutes / Gap days and outage |
| 5 | 🟠 Infographic: the footer "TEB3123 \| Final Report Guide \| 5" overlaps the bottom of the image, and the header overlaps the top | Section break around the infographic page, then "Different first page" with no header/footer, or shrink the image to fit inside the margins |
| 5 | 🟠 Infographic block 05B reads "**454%**" for measured A/C share of peak | Replace the purple infographic with the blue poster (`ML Poster.png`, copied to `ML-ASSIGNMENT/figures/infographic.png`) after the Section G fixes; it already shows 45.4% |
| 29–33 | 🟠 Chapter 5 is in **Times New Roman**; the rest of the report is Calibri | Select Chapter 5 → apply the Normal/Heading styles (Calibri 11 or 12 pt) |
| 31 | 🟡 "week's 4–5", "week's 2–5" | "weeks 4–5", "weeks 2–5" |
| 9 | 🟡 Justified line with huge gaps: "works through three mechanisms :" | Left-align that line, or rewrite as a sentence |
| 52–53 | 🟡 Recommendations table wraps into very narrow columns and is hard to read | Landscape section for that table, or reduce to 4 columns and put "When" inside the benefit column |
| 63 | 🟡 "References" heading appears twice | Delete one |
| 39 | 🟡 Second "Chapter 6 Discussion and Interpretation" heading (copied from the template quirk) | Make it a Heading 2 like "Part B: Discussion and interpretation" so the TOC doesn't show Chapter 6 twice |

---

## Priority 5: grammar and wording (page by page)

| Page | Current | Suggested |
|---|---|---|
| 6 | "…set at about 49% [8], and Exact shares vary between buildings, but A/C is consistently the largest load…" (repeats the previous sentence) | End at "…about 49% [8]." Delete the duplicate clause |
| 6 | "Ither initiatives including LED replacement and rescheduled operations has cut" | "Other initiatives, including LED replacement and rescheduled operations, have cut" |
| 6 | "committed to to a net-zero" | "and UTP has committed to a net-zero carbon campus by 2050 [16]" |
| 6 | "moved one step ahead, acting on both energy cost and peak demand which saved RM 1.0 million annually" | "UTP has already acted on energy cost and peak demand: optimising its District Cooling Plant to reduce maximum-demand charges saves RM 1.0 million a year [13]." |
| 7 | "UTP Property Management who responsible in paying" | "UTP Property Management, which is responsible for paying" |
| 7 | "Indirectly are the building occupants whose comfort depends on A/C." | "Building occupants are affected indirectly, because their comfort depends on the A/C." |
| 7 | "As we know, campus's electricity contributes…" | "Campus electricity drives UTP's carbon footprint and energy bill, but its building meters cannot show which loads cause the costly demand peaks." |
| 7 | "UTP has to bare the cost" | "bear" |
| 7 | "applied blindly without correctly evaluate its effectiveness" | "applied blindly, with no way to check their effect" |
| 7 | "Evidence is retrieved from the data that A/C drives the peak." | "The data show that A/C drives the peak." |
| 9 | "Targetting 7.3" | "Target 7.3" |
| 9 | "Act as a secondary as the carbon effect for a building is small rather than the value in energy efficiency and demand." | "We treat this as secondary because the carbon effect for one building is small (Section 7.3); the main value is in energy efficiency and demand." |
| 9 | "Seasonal change is nor=t considered as the dataset records was only form September to October 023. Other building were also not included as research limit to the one institutional building" | "Seasonal change is not considered, because the data cover only September–October 2023. Other buildings are not included; the study is limited to one institutional building in Kuala Lumpur." |
| 10 | "This includes clustering needs of the main-meter profile only instead of the A/C and lighting profiles. The idea called for extending the lighting training to weeks two and three." | "Clustering now uses the main-meter profile only, rather than the A/C and lighting profiles, so it works in buildings without sub-meters. Lighting training was extended to weeks 2–3, as the proposal planned." |
| 11 | "Defense Health" | "Defence Health" (official name) |
| 15 | "Second pick was around 4 Kw" | "The second peak is around 4 kW" |
| 23 | "joining.However" | "joining. However" |
| 29 | "The main objective is to identify the problem as a supervised regression problem." | "The task is supervised regression." |
| 29 | "The failure of static allocation heuristics … happens only in peak office hours…" | "A fixed-share rule (e.g. 'A/C = 30% of the total') fails exactly in the office-hours windows that set the demand charge (Figure 9)." |
| 31 | "First, A/C that train on week's 4–5 is 16,985 minutes, 66% and on week 6 is 8,590 minutes, 34%. For Lighting, result train on…" | "A/C: train on weeks 4–5 (16,985 minutes, 66%), test on week 6 (8,590 minutes, 34%). Lighting: train on weeks 2–5 (32,725 minutes, 79%), test on week 6." |
| 31 | "Then, train.py rerunning again but never overwrites the freeze." | "Rerunning train.py never overwrites the freeze." |
| 34 | "Every model was retrained at its best CV values come from the four expanding time-series folds configuration on the same training weeks." | "Every model was retrained at its best CV configuration on the same training weeks and scored with the same definitions." |
| 36 | "Below are the table for robustness check." | "Table 14 shows the robustness check." |
| 37 | "Bootstrap. come from 2,000 resamples in Tables 12–13 of whole days" | "Bootstrap. The CIs in Tables 12–13 come from 2,000 resamples of whole days" |
| 37 | "there are big different in peak-window MAE" | "peak-window MAE varies a lot between folds" |
| 37 | "It fulfill the pre-committed freeze rule" | "It met the pre-registered freeze rule" |
| 38 | "ridge regression was chosen as the best model on peak windows but the worst on typical error … due to it underperformed test minutes." | "Ridge was chosen by the freeze rule. It was the best lighting model on peak windows but the worst on typical error in the test week, so we do not recommend any lighting model for operational use." |
| 43 | "This is the time when A/C is at its lowest of predictability from the timetable." | "This is when A/C ramps up and is least predictable from the timetable." |
| 43 | "master meter" | "main meter" |
| 49 | "Only the primary meter can indicate what produces the peak." | "The main meter alone can show what produces the peak." |

---

## Section A: replacement text for 7.4 (paste over the whole of 7.4, pages 56–57)

> **7.4 Adoption and monitoring**
>
> The adoption plan below was built from the CLEMD results and from published UTP information only. Because of the project's time frame, it has not yet been reviewed with UTP Property Management, the sustainability office or the registered energy manager. It is therefore a **proposed** plan to be validated with these stakeholders (Section 8.3), not an agreed procedure.
>
> *Table 21. Proposed requirements for adopting and monitoring the demand-triggered A/C trim at UTP (to be validated with UTP stakeholders).*
>
> | Aspect | Requirement |
> |---|---|
> | **Data the model needs** | A 1-minute main-meter feed with real power per phase, power factor, THD and current harmonics, the same signals used in this study. Public UTP sources confirm that every building has a meter linked to the i-BMS [5], but they do not say which signals are logged. Whether harmonics are recorded is therefore an open question to confirm with UTP facilities at the start of the pilot. Our ablation (Table 9b) shows what is at stake: with total kW only, cross-validated error roughly doubles (2.01 vs 0.99 kW), and with per-phase power but no harmonics it is 1.69 kW. Both are still 33–43% better than the timetable baseline, so the method remains useful on a simpler meter, but less accurate, and it would need re-testing on UTP's actual signals. |
> | **Decision rule** | Each building would have its own demand trigger, set near the 95th percentile of its 15-minute demand (53 kW for the CLEMD building), and its own trim size. Both values are proposals from this study and should be agreed with Property Management before use. |
> | **People involved** | Facilities operators would carry out the trim, and the registered energy manager required under Act 861 [20] would review the monthly reports. These roles are inferred from Act 861 and UTP's published energy work, not confirmed with UTP. |
> | **Review** | Every month, compare the estimated peak with the measured peak and retrain the model (Recommendation 5). |
> | **Comfort and fairness** | The trims are small (10–30%) and short. Any UTP trial should collect occupant feedback, because people who feel too warm will override the system. Spaces with vulnerable users or sensitive equipment should be left out. |
> | **Privacy** | Building-level electricity data can reveal when spaces are occupied [44]. Reports should stay at building or floor level and be averaged over time, never shown by room or by person. |
> | **False alarms** | A trim triggered outside the real peak costs a little comfort but no money. Missing the real peak costs a month of demand charges, so the threshold should be set on the low side. |
> | **Tracking real savings** | Compare each month's maximum demand and after-hours kWh with the same month in the previous year. Report savings as *measured* only once the pilot provides real data. |
>
> **Next step: stakeholder validation.** Before any part of this plan is used, it should be presented to UTP Property Management, the sustainability office and the registered energy manager to confirm (1) which signals the i-BMS meters record, (2) whether the proposed trigger and trim sizes are acceptable for occupant comfort, and (3) who would operate and review the system. This is the first step of the pilot in Recommendation 4 and is listed as future work in Section 8.3.

## Section B: replacement for 8.3 item 2 (page 61)

> 2. **Validate the adoption plan with UTP stakeholders** (resolves the unverified assumptions in Section 7.4). Present the findings to UTP Property Management, the sustainability office and the registered energy manager to confirm which signals the i-BMS meters record, whether the proposed trigger and trim sizes are acceptable, and who would run and review the system. If the meters do not record harmonics, re-test the model using only power and power-factor inputs.

## Section C: new row for the limitations table (8.1, page 59, before "Possible logger clock offsets")

> | Adoption plan not yet reviewed with UTP stakeholders (Section 7.4) | Meter signals, trigger level, trim size and operating roles are assumptions; Recommendations 1 and 3 cannot yet be confirmed as workable at UTP | Stakeholder review before the pilot (Section 8.3, item 2) |

These three changes are already applied to `ML-ASSIGNMENT/FINAL_REPORT.md`, so the Markdown and the PDF will match.

---

## Section D: new ablation results (code change), paste into Chapter 4 and related places

**D1. Replace the whole of 4.4 (page 28)** with the text below. Keep the caption "Table 9b" so no other table numbers change.

### 4.4 Evidence of usefulness

We compared feature sets directly under the **same validation protocol** used for model selection (`ablation.py`): the frozen LightGBM settings, the same four `TimeSeriesSplit` folds, A/C training weeks 4–5 only. Only the input columns change. The test week was not used, and the frozen model was not changed; this is evidence about the features, not a new model choice.

*Table 9b. Feature-group ablation, A/C, cross-validation on training weeks (mean of 4 folds).*

| Feature set | Features | CV MAE kW (± fold SD) | Change vs all features | CV peak-window MAE kW |
|---|---|---|---|---|
| **All features (frozen)** | 98 | **0.99 ± 0.22** | — | 2.59 |
| Without harmonics | 45 | 1.20 ± 0.28 | **+21%** | 2.30 |
| Without power quality | 82 | 0.99 ± 0.19 | +0.3% | 2.82 |
| Without temporal | 89 | 0.98 ± 0.25 | −1.2% | 2.85 |
| Without calendar | 93 | 1.05 ± 0.22 | +6.5% | 4.35 |
| Duplicates removed (ratios and constant H1) | 73 | 1.01 ± 0.19 | +2.4% | 3.15 |
| Power meter, no harmonics or power quality | 29 | 1.69 ± 0.30 | +71% | 4.11 |
| kW-only meter (total kW, temporal, calendar) | 18 | 2.01 ± 0.45 | +104% | 4.93 |
| Calendar only | 5 | 3.05 ± 0.87 | +209% | 6.55 |

What this shows:

- **Harmonics carry the most unique information.** Removing them raises typical error by 21%, which agrees with the permutation result in Table 16. Their peak-window error is slightly lower without them (2.30 vs 2.59 kW), but peak-window MAE rests on only a few windows per fold and varies widely (Section 6.3), so we do not read much into that difference.
- **Power-quality and temporal features add little on their own** (changes within ±1.3%, far inside the fold SD). Their information largely overlaps with power and harmonics. We kept them because the freeze rule fixed the feature set before testing, and they do not hurt.
- **Calendar features help mainly at the peak.** Typical error rises only 6.5% without them, but peak-window error rises from 2.59 to 4.35 kW. The frozen model uses calendar features little on average (Table 16), yet they help it place A/C correctly in the busiest windows.
- **Removing the duplicate features makes no meaningful difference** (+2.4%, within the fold SD), which confirms Section 4.2: the copies did not harm accuracy, but they are not needed.
- **The meter matters.** A meter that logs only total kW roughly doubles the error (2.01 kW), and a standard power meter without harmonics gives 1.69 kW. Both still beat the timetable baseline (CV MAE 2.99 kW, Appendix B) by 33% and 43% respectively. This is direct evidence for the adoption question in Section 7.4.

**D2. 4.2, last sentence of the "duplicates" paragraph (page 27).** Replace "Removing the duplicates is listed as future work." with:

> The ablation in Section 4.4 confirms that removing the duplicates changes cross-validated error by only 2.4%, within the fold-to-fold spread.

**D3. 6.8, "Calendar features matter little" bullet (page 46).** Replace with:

> - **Calendar features matter little on average**, so the model does not just follow the timetable. Retraining without them does, however, worsen peak-window error (Table 9b), so they help place A/C in the busiest windows. SHAP and permutation importance agree on the top two groups. They disagree slightly on the order of temporal and calendar features, and both of those groups are small.

**D4. 8.1 limitations table (pages 58–59).** Change two rows:

| Row | New "Practical response" / new text |
|---|---|
| Duplicated and constant harmonic features | Practical response → "Group-level interpretation; the ablation shows removing them costs no measurable accuracy (Table 9b)" |
| Small tuning grid; no feature ablation | Whole row → "Small tuning grid; ablation on CV only \| Models may be slightly under-tuned; the ablation (Table 9b) uses training-week CV, not the sealed test week \| Stated; a later sealed week would confirm the ablation" |

**D5. 8.3 item 4 (page 61).** Replace with:

> 4. **Retrain on the reduced feature set** (follows from Table 9b). Drop the constant H1 and duplicated ratio columns (no measurable loss), confirm on a later sealed week, and use the kW-only and no-harmonics results to choose the minimum meter specification for UTP buildings.

**D6. 5.1 pipeline list (page 29).** Use the ten-step list in `FINAL_REPORT.md` §5.1. Step 4 is new: "`ablation`: retrains the frozen A/C settings on reduced feature sets under the same CV folds (Section 4.4) (O3)."

**D7. Appendix B, last line (page 69).** Add: "Feature-group ablation (Table 9b), all folds: `results/ablation_cv.csv`."

**D8. Small follow-on edits** (one sentence each; full text in `FINAL_REPORT.md` at the same section):

| Page | Section | Change |
|---|---|---|
| 8 | 1.3 Table 1, row O3 | Evidence → "Sections 4.4 and 6.8; Table 9b; Figures 19–22; Table 16" |
| 20 | 2.6, last paragraph | "Only weeks 2–5 were used for the feature-redundancy check and all cross-validation" → "…for the feature-redundancy check, **the feature ablation** and all cross-validation" |
| 28 | 4.5, 4th bullet | "Redundancy check excludes the test week" → "**Redundancy check and ablation exclude** the test week" |
| 30 | 5.2, reason 4 (k-means) | Add: "The calendar grouping is the reference: Section 6.8 shows the clusters differ from it on two weekdays, one of them a public holiday." |
| 33 | 5.5, Validation row | Add: "…and the ablation's full feature set reproduces the frozen CV MAE" |
| 45–46 | 6.8, harmonics bullet | Add at the end: "The ablation agrees: retraining without harmonics raises CV error by 21% (Table 9b)." |
| 47 | 6.8, first clustering bullet | Add at the end: "…and this is where the clusters differ from the simple weekday/weekend reference grouping." |
| 53 | 7.2, Recommendation 4 | Evidence → "The method works on CLEMD, but **much of** UTP uses district cooling, lighting estimates are not reliable (Sections 6.5, 8.1), **and the adoption plan is not yet reviewed with UTP (Section 7.4)**". Action → start with "**review the plan with UTP stakeholders, then** run a pilot…" |
| 58 | 8.1, "Test week was viewed" row | Response → "No tuning, selection **or ablation** used it…" |
| 60 | 8.2 Table 23, Objective 3 | Last sentence → "This makes physical sense for A/C, and the ablation confirms that harmonics carry information the other features do not (Table 9b)." |
| 61 | 8.2, last sentence | "All savings remain estimates until the method is **reviewed with UTP stakeholders and** tested on a UTP building." |

---

## Section E: metric definitions for 6.1 (page 34), paste after the equations

> where *y* is the measured A/C power, *ŷ* the estimate, *ȳ* the mean of *y*, *n* the number of minutes and *P* the building's main-meter power.
>
> - **Peak-window MAE**: MAE on 15-minute means, restricted to the windows where *building* demand is in the top 5% of the evaluated period (≥ 61.9 kW in the test week, 29 windows). These windows set the TNB maximum-demand charge, so this is **the most decision-relevant measure**.
> - **Energy-share error (percentage points)** = 100 × (Σŷ − Σy) / ΣP: whether the model gets A/C's share of building energy right. It feeds the kWh and tCO₂e scenarios in Chapter 7.
> - **Normalised disaggregation error** NDE = √(Σ(ŷ − y)² / Σy²): a standard NILM metric [18], included for comparison with the literature.
> - **R²** is reported but given little weight: A/C is part of the building total, so even a simple model scores a high R².

---

## Section F: missing appendices, paste after Appendix B (replacing pages 68–70's template text)

Order in the report: Appendix A → B (already there) → C → D → E.

### Appendix A Data Dictionary and Quality Checks

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

### Appendix C Additional Results

- Lighting Ridge standardised coefficients: `results/ridge_light_coefficients.csv` (largest: THD phase 2, −0.83 kW per SD).
- Local SHAP values at the week's peak: `results/shap_local_peak_ac.csv`.
- Per-day cluster assignments and energy: `results/cluster_days.csv`. k-search: `results/cluster_k_search.csv`.
- Pre-cooling windows tested (20% of 14:00–16:00 A/C moved): 08–10 → 0.0 kW; 09–11 → 0.0 kW; 10–12 → −5.2 kW; 11–13 → −5.2 kW (negative = peak raised). Source: `results/scenarios.json`.
- Out-of-sample predictions for weeks 2, 3 and 6: `results/predictions.csv`.

### Appendix D Implementation Instructions

**Repository:** `ML-ASSIGNMENT/`. This report is `FINAL_REPORT.md` at its root, and all figure links are relative to it. The code is submitted with this report as a zip of the `ML-ASSIGNMENT/` folder (without `.venv/` and `data/`, which are recreated by steps 1–2).

1. **Environment.** Python 3.11 (tested on 3.11.17, Linux/WSL2).
   ```bash
   uv venv .venv && uv pip install -r requirements.txt
   # or: python -m venv .venv && .venv/bin/pip install -r requirements.txt
   ```
2. **Data** (≈ 7 GB, not in git). Download the six CLEMD weekly folders from https://doi.org/10.6084/m9.figshare.c.6946581 into `data/clemd/<weekly folder>/*.csv`, and the NASA POWER hourly file for UTP (4.385 N, 100.979 E, October 2023, UTC) to `data/external/nasa_power_utp_oct2023_utc.csv`.
3. **Run everything** (about 12 minutes): `./run_all.sh` (or `PY=python ./run_all.sh`). The steps must run in order: `prepare_data → features → train → ablation → evaluate → explain → cluster → scenarios → make_figures → build_dashboard`.
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

### Appendix E Team Contribution Record

All five members contributed equally. Each member led one stage of the ML lifecycle, reviewed another member's stage, and drafted and proofread their chapters of this report. Every piece of code was checked by a second member, and the final pipeline was rerun from raw data before submission.

*Table E1. Team contribution record.*

| Member and ID | Lead responsibility | Review and support | Report chapters | Share |
|---|---|---|---|---|
| Izzatul Najwa Binti Che Zaki (22007298) | Data acquisition, loader, data-quality log, cleaned dataset (`prepare_data.py`) | Feature engineering; leakage checks | Ch. 2 Data Understanding; Ch. 3 Preprocessing | 20% |
| Nurul Izzati Binti Razali (22007868) | Feature engineering, feature dictionary, redundancy check, baselines (`features.py`) | Model tuning; data-quality log | Ch. 4 Feature Engineering; Ch. 1 Introduction | 20% |
| Daphne Binti Douglas (22006239) | Tree models, hyperparameter tuning, model freeze, test evaluation (`train.py`, `evaluate.py`) | Error analysis; baselines | Ch. 5 Methodology; Ch. 6.1–6.4 Results | 20% |
| Siti Nurmasyitah Binti Ab Aziz (22007601) | SHAP, permutation importance, error analysis, clustering (`explain.py`, `cluster.py`) | Test evaluation; scenario checks | Ch. 6.5–6.9 Discussion; Ch. 8 Limitations and Conclusion | 20% |
| Sharvin A/L Kanesan (22006930) | UTP scenarios, integration, figures, dashboard (`scenarios.py`, `report_figures.py`, `build_dashboard.py`) | Clustering; reproducibility rerun | Ch. 7 Sustainability; Executive Summary; Appendices | 20% |

---

## Section G: poster / infographic (page 5 and the separate poster)

The blue poster (`ML Poster.png`) is the same infographic, recoloured. **Use one version in both places.** The report's page 5 currently has the older purple version with the "454%" typo. Changes, in priority order:

| # | Where | Current | Change to | Why |
|---|---|---|---|---|
| 1 | 05 key-results box | "45% more accurate than a timetable rule" | "**45% lower error** than a timetable rule" | "Accurate" overstates it; the report's claim is 45% lower MAE |
| 2 | 06 heading + badges | "WHAT UTP CAN DO NOW", "NOW" badges | "**WHAT UTP COULD DO**"; badges → "**No new meters**" | Must match the new 7.4: the plan isn't yet reviewed with UTP stakeholders |
| 3 | 07 limitation | Only the one-building limitation | Add a line: "**Not yet reviewed with UTP stakeholders**: meter signals, trigger and trim size to confirm in the pilot." | Same reason as #2; also strengthens the "limitation and assumption" block |
| 4 | 07 limitation | "UTP uses district cooling." | "**Much of** UTP uses district cooling." | The report says "much of UTP" |
| 5 | Colour | Every element is light/mid/dark blue; in the 01 and 05B bars, "A/C" (light blue) and "Other" (mid blue) are hard to tell apart, and white text on light blue is low-contrast | Keep blue as the base, and use **one accent colour** (the SDG-7 yellow already in the title, or orange) for A/C in every bar and for the headline numbers (1.24 kW, 44.0%, 5.8 kW, 6.8 tCO₂e) | This is the "make it pop" fix. One accent ties every A/C number together, and the A/C/Other confusion goes away |
| 6 | 05B bars | No legend | Add "■ A/C ■ Lighting ■ Other" under the bars, or reuse 01's legend | The bars are unreadable without it |
| 7 | 02 | "Cutting the peak lowers cost and grid stress & saved kWh cut Scope 2 emissions (SDG 13)." | "Lower peaks cut cost and grid stress; saved kWh cut Scope 2 emissions (SDG 13)." | Grammar |
| 8 | 02 | "RM89- 97" | "RM 89–97" | Spacing and dash |
| 9 | 05 A | "Peak windows: 1.52 kW vs 6.54 kW for the baseline" (tiny grey text) | Promote it: second big number "**1.52 kW** at peak (baseline 6.54)" | It's the most decision-relevant result (report §6.1) and it's currently hidden |
| 10 | Footer | Smallest text is about 7 pt at A4 | Keep body text ≥ 8 pt when printed on A4 | Template: "legible at normal page size" |
| 11 | Report page 5 | Header/footer overlap the image | Put the infographic on its own section page with no header/footer | Layout |

---

---

## Final check before exporting the PDF

- [ ] No "(belum …)", `[TODO …]`, `[Check …]`, `[Name and ID]` or template instruction text left (Ctrl+F for `[`, `belum`, `TODO`, `Template`, `Guide`)
- [ ] Order: cover → executive summary → infographic → TOC → list of figures → list of tables → Ch 1–8 → References → Appendices A–E
- [ ] Every "Figure N" / "Table N" in the text points to a real caption
- [ ] Same numbers everywhere: 41,680 records; MAE 1.24 kW (CI 0.56–1.87); 45% / 21%; peak MAE 1.52 kW; 44.0% vs 45.4%; 5.8 kW; RM 6,200–6,700; 6.8 tCO₂e
- [ ] One font throughout (Calibri 11/12 pt), page numbers on every page
- [ ] Section D (ablation) pasted, and Table 9b caption used
- [ ] Code zip ready (exclude `.venv/` and `data/`; include `results/`, `figures/`, `requirements.txt`, `README.md`, `run_all.sh`)
