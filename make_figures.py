"""Problem/data figures (EDA, workflow, split) + headline stats, from data/processed/clemd_1min.parquet.

Run after the rest of the pipeline. Writes figures/proposal/*.png and figures/proposal/stats.json.
Figure titles carry no numbers: the report's captions number them.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch

from evaluate import AC, GRID, INK2, LIGHT, SURF
from features import DATA, ROOT, WORK_END, WORK_START
from scenarios import PR_RANGE, PV_COLOR as PV, PV_MWP, pv_profile

FIG = ROOT / "figures" / "proposal"
FIG.mkdir(parents=True, exist_ok=True)
df = pd.read_parquet(DATA)
df = df[df["week"] >= 4]  # these figures use the A/C weeks only

# Colour follows the entity in every figure (same palette as the results figures)
OTHER, INK = "#c3c2b7", "#0b0b0b"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": INK2, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "axes.axisbelow": True,
    "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "lines.linewidth": 2, "legend.frameon": False, "savefig.dpi": 200, "savefig.bbox": "tight",
})


def save(fig, name):
    fig.savefig(FIG / name)
    plt.close(fig)


df["other_kw"] = (df["agg_p_kw"] - df["ac_kw"] - df["light_kw"]).clip(lower=0)
df["hour"] = df.index.hour
df["weekend"] = df.index.day_of_week >= 5
df["working"] = ~df["weekend"] & df["hour"].between(WORK_START, WORK_END - 1)
q15 = df[["agg_p_kw", "ac_kw", "light_kw", "other_kw"]].resample("15min").mean().dropna()
peak = q15[q15["agg_p_kw"] >= q15["agg_p_kw"].quantile(0.95)]
stats = {}

# ---- workflow -------------------------------------------------------
fig, ax = plt.subplots(figsize=(13, 3.2))
ax.axis("off"); ax.set_xlim(0, 12.9); ax.set_ylim(0, 3.2)
steps = [("Problem", "Which loads set\nthe peak?"), ("Data", "CLEMD main meter\n+ sub-meters (1 s)"),
         ("Features", "Power, PF, THD,\nharmonics, lags, time"), ("ML", "Baselines → RF →\nXGBoost/LightGBM;\nk-means"),
         ("Evaluation", "MAE, RMSE, R²,\npeak-window error"), ("Interpretation", "SHAP, error\nanalysis"),
         ("Sustainability", "UTP scenarios:\nkW, RM, PV, tCO₂e")]
for i, (head, body) in enumerate(steps):
    x = 0.05 + i * 1.84
    ax.add_patch(FancyBboxPatch((x, 0.5), 1.6, 2.2, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc="#cde2fb" if head != "Sustainability" else "#c7eedd", ec=INK2, lw=1))
    ax.text(x + 0.8, 2.35, head, ha="center", va="center", weight="bold", fontsize=9.5)
    ax.text(x + 0.8, 1.35, body, ha="center", va="center", fontsize=8.5, color=INK2)
    if i < len(steps) - 1:
        ax.annotate("", (x + 1.82, 1.6), (x + 1.62, 1.6), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.5))
ax.set_title("Project workflow")
save(fig, "fig01_workflow.png")

# ---- data availability ----------------------------------------------
circuits = ["Aggregate", "CP AC", "DB TG", "DB T1", "DB ML 1", "DB ML 2", "EMSB 1", "SSB MF"]
avail = np.array([  # 1 ok, 0 missing, 0.5 unusable duplicate (from DATASET_NOTES inventory)
    [0, 1, 1, 1, 1, 0.5, 1, 1], [1, 0, 1, 1, 1, 0, 1, 1], [1, 0, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1]])
weeks = ["W1 16–21 Sep", "W2 21–27 Sep", "W3 27 Sep–4 Oct", "W4 4–11 Oct", "W5 11–18 Oct", "W6 18–25 Oct"]
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.grid(False)
colors = {1: "#2a78d6", 0: "#f3f2ee", 0.5: "#eda100"}
for r in range(6):
    for c in range(8):
        v = avail[r, c]
        ax.add_patch(plt.Rectangle((c + 0.04, r + 0.04), 0.92, 0.92, fc=colors[v], ec=SURF))
        ax.text(c + 0.5, r + 0.5, {1: "✓", 0: "missing", 0.5: "dup."}[v], ha="center", va="center",
                fontsize=8 if v != 1 else 11, color="white" if v == 1 else INK2)
ax.add_patch(plt.Rectangle((0, 3), 2, 3, fill=False, ec=INK, lw=2.2))
ax.set_xlim(0, 8); ax.set_ylim(6, 0)
ax.set_xticks(np.arange(8) + 0.5, circuits, rotation=0)
ax.set_yticks(np.arange(6) + 0.5, weeks)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_title("CLEMD file availability (outlined: modelling set)")
save(fig, "fig03_data_availability.png")

# ---- week 6 time series ---------------------------------------------
w6 = q15.loc["2023-10-19":"2023-10-24"]
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(w6.index, w6["agg_p_kw"], color=INK2, lw=1.5, label="Whole building (main meter)")
ax.plot(w6.index, w6["ac_kw"], color=AC, label="Air-conditioning (CP AC)")
ax.plot(w6.index, w6["light_kw"], color=LIGHT, label="Lighting & sockets (DB TG + T1 + ML 1)")
ax.set_ylabel("Real power, 15-min mean (kW)")
ax.legend(loc="upper right", ncol=3, fontsize=8.5)
ax.set_ylim(0, w6["agg_p_kw"].max() * 1.18)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d %b"))
ax.set_title("Building, A/C and lighting load (19–24 Oct 2023)")
save(fig, "fig04_week6_timeseries.png")

# ---- average daily profile, weekday vs weekend ----------------------
fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
for ax, (wk, title) in zip(axes, [(False, "Weekdays"), (True, "Weekends")]):
    prof = df[df["weekend"] == wk].groupby("hour")[["ac_kw", "light_kw", "other_kw"]].mean()
    ax.stackplot(prof.index, prof["ac_kw"], prof["light_kw"], prof["other_kw"],
                 colors=[AC, LIGHT, OTHER], edgecolor=SURF, linewidth=1.5,
                 labels=["Air-conditioning", "Lighting & sockets", "Other / unmetered"])
    ax.axvspan(WORK_START, WORK_END, color=INK2, alpha=0.06, lw=0) if not wk else None
    ax.set_title(title, fontsize=11, loc="left")
    ax.set_xticks(range(0, 24, 3), [f"{h:02d}:00" for h in range(0, 24, 3)])
    ax.set_xlim(0, 23); ax.set_xlabel("Hour of day")
axes[0].set_ylabel("Mean real power (kW)")
axes[1].legend(loc="upper right", fontsize=8.5)
axes[0].text(WORK_START + 0.2, axes[0].get_ylim()[1] * 0.97, "office hours\n08:00-17:00", fontsize=8, color=INK2, va="top")
fig.suptitle("Average daily load profile", x=0.01, ha="left",
             fontweight="bold", fontsize=12)
save(fig, "fig05_daily_profile.png")

# ---- share of energy vs share of peak --------------------------------
def shares(frame):
    tot = frame["agg_p_kw"].sum()
    return [frame[c].sum() / tot * 100 for c in ("ac_kw", "light_kw", "other_kw")]

energy, peaks = shares(q15), shares(peak)
stats["ac_share_energy_pct"], stats["light_share_energy_pct"], _ = [round(v, 1) for v in energy]
stats["ac_share_peak_pct"], stats["light_share_peak_pct"], _ = [round(v, 1) for v in peaks]
stats["peak_threshold_kw"] = round(q15["agg_p_kw"].quantile(0.95), 1)
stats["peak_windows_in_office_hours_pct"] = round(
    100 * np.mean([(not t.day_of_week >= 5) and WORK_START <= t.hour < WORK_END for t in peak.index]), 1)
fig, ax = plt.subplots(figsize=(9, 3.4))
labels = ["All 15-min windows\n(share of energy)", "Top 5% demand windows\n(share of peak)"]
for i, vals in enumerate([energy, peaks]):
    left = 0
    for v, col, name in zip(vals, [AC, LIGHT, OTHER], ["Air-conditioning", "Lighting & sockets", "Other / unmetered"]):
        ax.barh(i, v, left=left, color=col, edgecolor=SURF, linewidth=2, height=0.55, label=name if i == 0 else None)
        ax.text(left + v / 2, i, f"{v:.0f}%", ha="center", va="center", fontsize=10,
                color="white" if col != OTHER else INK, weight="bold")
        left += v
ax.set_yticks([0, 1], labels); ax.invert_yaxis()
ax.set_xlim(0, 100); ax.set_xlabel("% of whole-building load")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=3, fontsize=9)
ax.grid(axis="y", visible=False)
ax.set_title("A/C share grows at peak demand")
save(fig, "fig02_energy_vs_peak_share.png")

# ---- A/C heatmap day x hour -----------------------------------------
hm = df.groupby([df.index.date, "hour"])["ac_kw"].mean().unstack().dropna(how="all")
hm = hm.loc[[d for d in hm.index if hm.loc[d].notna().sum() >= 20]]
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.grid(False)
cmap = LinearSegmentedColormap.from_list("blue", ["#f3f2ee", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
im = ax.imshow(hm.values, aspect="auto", cmap=cmap, vmin=0)
ax.set_yticks(range(len(hm)), [pd.Timestamp(d).strftime("%a %d %b") for d in hm.index], fontsize=8)
ax.set_xticks(range(0, 24, 2), [f"{h:02d}" for h in range(0, 24, 2)])
ax.set_xlabel("Hour of day")
for i, d in enumerate(hm.index):
    if pd.Timestamp(d).day_of_week >= 5:
        ax.text(23.7, i, "weekend", fontsize=7, color=INK2, va="center")
cb = fig.colorbar(im, ax=ax, pad=0.09); cb.set_label("Mean A/C power (kW)"); cb.outline.set_visible(False)
ax.set_title("Hourly A/C load for each day")
save(fig, "fig06_ac_heatmap.png")

# ---- main meter vs A/C (why ML is needed) ---------------------------
s = q15.sample(min(1500, len(q15)), random_state=0)
hrs = s.index.hour
fig, ax = plt.subplots(figsize=(7.5, 5))
office = (s.index.day_of_week < 5) & (hrs >= WORK_START) & (hrs < WORK_END)
ax.scatter(s["agg_p_kw"][~office], s["ac_kw"][~office], s=10, color=OTHER, alpha=0.8, label="Outside office hours")
ax.scatter(s["agg_p_kw"][office], s["ac_kw"][office], s=10, color=AC, alpha=0.7, label="Weekday office hours")
r = np.corrcoef(q15["agg_p_kw"], q15["ac_kw"])[0, 1]
stats["corr_agg_ac_15min"] = round(r, 3)
ax.set_xlabel("Whole-building power, main meter (kW)"); ax.set_ylabel("A/C power, sub-meter (kW)")
ax.legend(loc="upper left", fontsize=9)
ax.text(0.98, 0.04, f"Overall Pearson r = {r:.2f}, but at 40–60 kW total\nthe A/C load ranges from about 4 to 35 kW",
        transform=ax.transAxes, ha="right", fontsize=9, color=INK2)
ax.set_title("Total building power versus A/C power")
save(fig, "fig08_agg_vs_ac.png")

# ---- candidate feature correlation ----------------------------------
feat = {
    "Total real power": "agg_p_kw", "Total reactive power": "agg_q_kvar", "Total apparent power": "agg_s_kva",
    "Within-minute power std": "agg_p_kw_std", "PF phase 1": "agg_PF1", "PF phase 2": "agg_PF2",
    "PF phase 3": "agg_PF3", "THD phase 1": "agg_THD1", "THD phase 2": "agg_THD2", "THD phase 3": "agg_THD3",
    "Neutral current": "agg_CurrentN", "5th harmonic, phase 1": "agg_Current1H5",
    "7th harmonic, phase 1": "agg_Current1H7", "3rd harmonic, neutral": "agg_CurrentNH3",
}
corr = pd.Series({k: df[v].corr(df["ac_kw"]) for k, v in feat.items() if v in df}).sort_values()
stats["feature_corr_with_ac"] = corr.round(3).to_dict()
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(corr.index, corr.values, color=AC, height=0.6, edgecolor=SURF)
for i, v in enumerate(corr.values):
    ax.text(v + (0.02 if v >= 0 else -0.02), i, f"{v:.2f}", va="center", ha="left" if v >= 0 else "right", fontsize=8.5)
ax.axvline(0, color=INK2, lw=1)
ax.set_xlim(-1.1, 1.1); ax.set_xlabel("Pearson correlation with A/C power (1-min data)")
ax.grid(axis="y", visible=False)
ax.set_title("Main-meter signals correlated with A/C power")
save(fig, "fig07_feature_correlation.png")

# ---- A/C profile vs modelled UTP rooftop PV --------------------------
pv_mw = PV_MWP * pv_profile() / 1000 * PR_RANGE[1]  # mid performance ratio (0.78)
ac_prof = df[~df["weekend"]].groupby("hour")["ac_kw"].mean()
pv_hours = pv_mw[pv_mw > 0.1 * pv_mw.max()].index
ac_hourly = df["ac_kw"].resample("1h").mean().dropna()
stats["ac_energy_in_pv_hours_pct"] = round(100 * ac_hourly[ac_hourly.index.hour.isin(pv_hours)].sum() / ac_hourly.sum(), 1)
stats["pv_hours"] = f"{min(pv_hours):02d}:00-{max(pv_hours) + 1:02d}:00"
stats["pv_peak_mw_mean_profile"] = round(pv_mw.max(), 2)
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(ac_prof.index, ac_prof / ac_prof.max() * 100, color=AC, marker="o", ms=4, label="A/C load, CLEMD weekdays")
ax.plot(pv_mw.index, pv_mw / pv_mw.max() * 100, color=PV, marker="s", ms=4, label="Modelled UTP rooftop PV (7.4 MWp, NASA POWER)")
ax.fill_between(pv_mw.index, 0, np.minimum(ac_prof.reindex(pv_mw.index) / ac_prof.max(), pv_mw / pv_mw.max()) * 100,
                color=PV, alpha=0.12, lw=0)
ax.text(ac_prof.idxmax() + 0.3, 103, "A/C", color=INK, fontsize=9, weight="bold")
ax.text(pv_mw.idxmax() - 2.4, 103, "Solar PV", color=INK, fontsize=9, weight="bold")
ax.set_ylim(0, 112); ax.set_xlim(0, 23)
ax.set_xticks(range(0, 24, 2), [f"{h:02d}" for h in range(0, 24, 2)]); ax.set_xlabel("Hour of day (Malaysia time)")
ax.set_ylabel("% of own daily maximum")
ax.legend(loc="upper left", fontsize=8.5)
ax.set_title("Weekday A/C demand versus modelled rooftop solar")
save(fig, "fig10_ac_vs_solar.png")

# ---- chronological split -------------------------------------------
fig, ax = plt.subplots(figsize=(11, 2.6))
daily = df["agg_p_kw"].resample("1h").mean()
ax.plot(daily.index, daily, color=INK2, lw=1)
for wk, col, lab in [(4, AC, "Train"), (5, AC, "Train"), (6, LIGHT, "Test")]:
    seg = df[df["week"] == wk]
    ax.axvspan(seg.index.min(), seg.index.max(), color=col, alpha=0.13, lw=0)
    ax.text(seg.index.min() + (seg.index.max() - seg.index.min()) / 2, daily.max() * 1.02,
            f"{lab}: week {wk}", ha="center", fontsize=9, weight="bold")
ax.set_ylim(0, daily.max() * 1.18); ax.set_ylabel("Building kW (hourly)"); ax.set_xlabel("Date (CLEMD recording, October 2023)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
ax.set_title("Chronological train/test split (A/C target; lighting also trains on weeks 2-3)")
save(fig, "fig09_split.png")

# ---- headline numbers -------------------------------------------------------
stats.update({
    "rows_1min": len(df), "days": int(pd.Series(df.index.date).nunique()),
    "mean_building_kw": round(df["agg_p_kw"].mean(), 1), "mean_ac_kw": round(df["ac_kw"].mean(), 1),
    "max_building_kw_1min": round(df["agg_p_kw"].max(), 1), "max_ac_kw_1min": round(df["ac_kw"].max(), 1),
    "max_building_kw_15min": round(q15["agg_p_kw"].max(), 1),
    "ac_at_building_15min_peak_kw": round(q15.loc[q15["agg_p_kw"].idxmax(), "ac_kw"], 1),
    "ac_after_hours_energy_pct": round(100 * df.loc[~df["working"], "ac_kw"].sum() / df["ac_kw"].sum(), 1),
    "light_after_hours_energy_pct": round(100 * df.loc[~df["working"], "light_kw"].sum() / df["light_kw"].sum(), 1),
    "ac_night_mean_kw_00_06": round(df[df["hour"] < 6]["ac_kw"].mean(), 2),
    "building_night_mean_kw_00_06": round(df[df["hour"] < 6]["agg_p_kw"].mean(), 1),
})
(FIG / "stats.json").write_text(json.dumps(stats, indent=2, default=str))
print(json.dumps(stats, indent=2, default=str))
