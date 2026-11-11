"""Extra figures for the final report (distributions, prep flow, model comparison, residuals,
consistency, lighting test, scenarios). Reads results/ and the processed parquet only: no new results.
Run after scenarios.py. Writes figures/report/*.png.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

from evaluate import AC, INK2, LIGHT
from features import RESULTS, ROOT, TEST_WEEK, dataset, load

FIG = ROOT / "figures" / "report"
OTHER = "#c3c2b7"
NAMES = {"time_of_day": "Time-of-day avg.", "ridge": "Ridge", "random_forest": "Random Forest",
         "xgboost": "XGBoost", "lightgbm": "LightGBM"}
ORDER = list(NAMES)


def save(fig, name):
    fig.savefig(FIG / name)
    plt.close(fig)


def distributions():
    _, y_ac, _ = dataset("ac")
    _, y_l, _ = dataset("light")
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    for ax, y, c, title in ((axes[0], y_ac, AC, "A/C power, training weeks 4–5"),
                            (axes[1], y_l, LIGHT, "Lighting & sockets power, training weeks 2–5")):
        ax.hist(y, bins=60, color=c, edgecolor="#fcfcfb", linewidth=0.5)
        for v, ls, lab in ((y.median(), ":", "median"), (y.mean(), "--", "mean")):
            ax.axvline(v, color=INK2, ls=ls, lw=1.2, label=f"{lab} {v:.1f} kW")
        ax.legend(fontsize=8.5, loc="upper right")
        ax.set_xlabel("Real power, 1-min mean (kW)"); ax.set_ylabel("Minutes"); ax.set_title(title)
        ax.grid(axis="x", visible=False)
    save(fig, "fig_target_distributions.png")
    return {"ac_skew": round(float(y_ac.skew()), 2), "light_skew": round(float(y_l.skew()), 2),
            "ac_below_1kw_pct": round(100 * float((y_ac < 1).mean()), 1)}


def prep_flow():
    df = load(include_test=True)
    n_ac = len(dataset("ac")[0]); n_l = len(dataset("light")[0])
    n_test = len(pd.read_csv(RESULTS / "predictions.csv", usecols=["week"]).query("week == @TEST_WEEK"))
    steps = [("Raw CLEMD", "42 CSV files\n1-second rows\n≈ 5.9 GB"),
             ("Load weeks 2–6", "fix dates, typo file,\nblank rows;\nweek 1 dropped"),
             ("Resample + join", f"{len(df) + 135:,} minutes\nmain meter +\nsub-meters"),
             ("Remove outage", f"−135 min (5 Oct)\n→ {len(df):,} clean\nminutes"),
             ("Build features", "98 features\nlags within\nsegments;\n−365 incomplete"),
             ("Partition", f"A/C train {n_ac:,}\nlight train {n_l:,}\ntest (wk 6) {n_test:,}")]
    fig, ax = plt.subplots(figsize=(12, 2.8))
    ax.set_xlim(0, len(steps)); ax.set_ylim(0, 1); ax.axis("off")
    for i, (head, body) in enumerate(steps):
        ax.add_patch(FancyBboxPatch((i + 0.06, 0.08), 0.84, 0.8, boxstyle="round,pad=0.02,rounding_size=0.05",
                                    fc="#e3eefb" if i < 5 else "#fde6dc", ec=INK2, lw=1))
        ax.text(i + 0.48, 0.76, head, ha="center", va="center", fontsize=10, weight="bold")
        ax.text(i + 0.48, 0.40, body, ha="center", va="center", fontsize=8.5, color=INK2)
        if i < len(steps) - 1:
            ax.annotate("", (i + 1.05, 0.48), (i + 0.91, 0.48), arrowprops=dict(arrowstyle="-|>", color=INK2))
    ax.set_title("Data preparation sequence with record counts", loc="left")
    save(fig, "fig_prep_flow.png")


def model_comparison():
    tm = pd.read_csv(RESULTS / "test_metrics.csv").set_index(["target", "model"])
    panels = [("ac", "mae", "mae_ci", "A/C: MAE, all test minutes"),
              ("ac", "peak_mae_15min", "peak_mae_ci", "A/C: MAE in the 29 peak windows"),
              ("light", "mae", "mae_ci", "Lighting & sockets: MAE")]
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.4), sharey=True)
    y = np.arange(len(ORDER))[::-1]
    for ax, (t, col, ci, title) in zip(axes, panels):
        d = tm.loc[t].loc[ORDER]
        colors = [AC if f else OTHER for f in d["frozen"]]
        ax.barh(y, d[col], color=colors, height=0.6)
        ax.errorbar(d[col], y, xerr=[d[col] - d[f"{ci}_lo"], d[f"{ci}_hi"] - d[col]], fmt="none",
                    ecolor=INK2, elinewidth=1, capsize=3)
        for yi, v, hi in zip(y, d[col], d[f"{ci}_hi"]):
            ax.text(hi, yi, f"  {v:.2f}", va="center", fontsize=8.5, color=INK2)
        ax.set_xlim(0, d[f"{ci}_hi"].max() * 1.2)
        ax.set_title(title, fontsize=10.5); ax.set_xlabel("kW (bar = estimate, line = 95% CI)")
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(y, [NAMES[m] for m in ORDER])
    fig.suptitle("Held-out test week (19–24 Oct 2023): frozen model in blue", x=0.01, y=1.06, ha="left",
                 fontweight="bold", fontsize=12)
    save(fig, "fig_model_comparison.png")


def residuals():
    p = pd.read_csv(RESULTS / "predictions.csv", index_col=0, parse_dates=True)
    w6 = p[p["week"] == TEST_WEEK]
    res = w6["ac_pred_kw"] - w6["ac_kw"]
    q = w6[["agg_p_kw", "ac_kw", "ac_pred_kw"]].resample("15min").mean().dropna()
    q["res"] = q["ac_pred_kw"] - q["ac_kw"]
    err = pd.read_csv(RESULTS / "error_breakdown_ac.csv").query("by == 'load_band'")
    fig, axes = plt.subplots(1, 3, figsize=(14, 3.8), gridspec_kw={"width_ratios": [1.3, 1, 1], "wspace": 0.35})
    ax = axes[0]
    office = (q.index.day_of_week < 5) & (q.index.hour >= 8) & (q.index.hour < 17)
    ax.scatter(q.loc[~office, "agg_p_kw"], q.loc[~office, "res"], s=9, color=OTHER, label="Outside office hours")
    ax.scatter(q.loc[office, "agg_p_kw"], q.loc[office, "res"], s=9, color=AC, alpha=0.8, label="Weekday office hours")
    ax.axhline(0, color=INK2, lw=1)
    ax.set_xlabel("Building power, 15-min mean (kW)"); ax.set_ylabel("Estimated − measured A/C (kW)")
    ax.set_title("Residual vs building load", fontsize=10.5); ax.legend(fontsize=8, loc="lower left")
    ax = axes[1]
    ax.bar(err["value"], err["mae_kw"], color=AC, width=0.6)
    for x, v, n in zip(err["value"], err["mae_kw"], err["count"]):
        ax.text(x, v + 0.08, f"{v:.1f}\nn={n:,}", ha="center", fontsize=8, color=INK2)
    ax.set_ylim(0, err["mae_kw"].max() * 1.3)
    ax.set_xlabel("Building load band (kW)"); ax.set_ylabel("MAE (kW)"); ax.grid(axis="x", visible=False)
    ax.set_title("Error by load band (1-min)", fontsize=10.5)
    ax = axes[2]
    ax.hist(res.clip(-15, 15), bins=60, color=AC, edgecolor="#fcfcfb", linewidth=0.4)
    ax.axvline(0, color=INK2, lw=1)
    ax.set_xlabel("Residual, 1-min (kW; clipped at ±15)"); ax.set_ylabel("Minutes"); ax.grid(axis="x", visible=False)
    ax.set_title(f"Residual distribution (mean {res.mean():+.2f} kW)", fontsize=10.5)
    fig.suptitle("Residual analysis, frozen A/C model, test week", x=0.01, y=1.06, ha="left", fontweight="bold", fontsize=12)
    save(fig, "fig_residuals.png")
    return {"res_mean": round(float(res.mean()), 2), "res_median": round(float(res.median()), 2),
            "within_1kw_pct": round(100 * float((res.abs() <= 1).mean()), 1),
            "within_5kw_pct": round(100 * float((res.abs() <= 5).mean()), 1),
            "office_res_mean": round(float(q.loc[office, "res"].mean()), 2),
            "under_45_65_pct": round(100 * float((q.loc[office & q["agg_p_kw"].between(45, 65), "res"] < 0).mean()), 0)}


def consistency():
    cv = pd.read_csv(RESULTS / "cv_results.csv").query("target == 'ac'")
    freeze = json.loads((RESULTS / "freeze.json").read_text())
    best = freeze["targets"]["ac"]["cv_best_params_per_model"]
    rob = pd.read_csv(RESULTS / "robustness_w4_to_w5.csv").set_index("model")
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.6), sharey=True)
    y = np.arange(len(ORDER))[::-1]
    ax = axes[0]
    for yi, m in zip(y, ORDER):
        f = cv[(cv.model == m) & (cv.params == json.dumps(best[m]))]["mae"]
        c = AC if m == "lightgbm" else INK2
        ax.scatter(f, [yi] * len(f), s=40, color=c, alpha=0.7, zorder=3)
        ax.plot([f.min(), f.max()], [yi, yi], color=c, lw=1.5)
        ax.scatter([f.mean()], [yi], marker="|", s=300, color=c, zorder=4)
    ax.set_yticks(y, [NAMES[m] for m in ORDER]); ax.set_xlabel("MAE (kW)")
    ax.set_title("A/C cross-validation: 4 folds (dots), mean (tick)", fontsize=10.5)
    ax.grid(axis="y", visible=False)
    ax = axes[1]
    d = rob.loc[ORDER, "mae"]
    ax.barh(y, d, color=[AC if m == "lightgbm" else OTHER for m in ORDER], height=0.6)
    for yi, v in zip(y, d):
        ax.text(v + 0.05, yi, f"{v:.2f}", va="center", fontsize=8.5, color=INK2)
    ax.set_xlabel("MAE (kW)"); ax.set_title("Robustness: train week 4 → test week 5", fontsize=10.5)
    ax.grid(axis="y", visible=False)
    save(fig, "fig_consistency.png")


def lighting_test():
    p = pd.read_csv(RESULTS / "predictions.csv", index_col=0, parse_dates=True)
    q = p[p["week"] == TEST_WEEK][["light_kw", "light_pred_kw"]].resample("15min").mean().dropna()
    fig, ax = plt.subplots(figsize=(11, 3.4))
    ax.plot(q.index, q["light_kw"], color=LIGHT, lw=2, label="Lighting & sockets measured (sub-meters)")
    ax.plot(q.index, q["light_pred_kw"], color=INK2, lw=1.3, ls="--", label="Estimated from main meter (Ridge, frozen)")
    ax.set_ylabel("Real power, 15-min mean (kW)"); ax.set_ylim(0, None)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d %b")); ax.legend(loc="upper right", fontsize=8.5)
    ax.set_title("Lighting estimated from the main meter vs measured, test week (19–24 Oct 2023)")
    save(fig, "fig_lighting_test.png")
    return {"light_meas_mean": round(float(q["light_kw"].mean()), 2), "light_pred_mean": round(float(q["light_pred_kw"].mean()), 2)}


def scenarios():
    s = json.loads((RESULTS / "scenarios.json").read_text())
    sh = pd.DataFrame(s["peak_shaving"]["scenarios"])
    ah = pd.DataFrame(s["after_hours"]["scenarios"])
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.6))
    ax = axes[0]
    x = np.arange(len(sh)); w = 0.36
    ax.bar(x - w / 2, sh["week6_cut_kw_estimated"], w, color=AC, label="From main-meter estimate")
    ax.bar(x + w / 2, sh["week6_cut_kw_measured"], w, color=OTHER, label="From measured A/C (check)")
    for xi, a, b in zip(x, sh["week6_cut_kw_estimated"], sh["week6_cut_kw_measured"]):
        ax.text(xi - w / 2, a + 0.15, f"{a:.1f}", ha="center", fontsize=8.5, color=INK2)
        ax.text(xi + w / 2, b + 0.15, f"{b:.1f}", ha="center", fontsize=8.5, color=INK2)
    ax.set_xticks(x, [f"{t}% trim" for t in sh["trim_pct"]]); ax.set_ylabel("Max-demand cut, test week (kW)")
    ax.set_title("Peak shaving: model vs sub-meter (estimate)", fontsize=10.5)
    ax.legend(fontsize=8.5, loc="upper left"); ax.grid(axis="x", visible=False)
    ax = axes[1]
    ax.bar(ah["office_hours"], ah["saved_tco2e_per_year"], color=AC, width=0.55)
    for xi, v, k in zip(ah["office_hours"], ah["saved_tco2e_per_year"], ah["saved_kwh_per_year"]):
        ax.text(xi, v + 0.12, f"{v:.1f} t\n{k:,} kWh", ha="center", fontsize=8.5, color=INK2)
    ax.set_ylim(0, ah["saved_tco2e_per_year"].max() * 1.3)
    ax.set_xlabel("Office-hours definition (weekdays)"); ax.set_ylabel("tCO₂e per year")
    ax.set_title("After-hours cut (A/C −50%, lighting −30%), one building (estimate)", fontsize=10.5)
    ax.grid(axis="x", visible=False)
    save(fig, "fig_scenarios.png")


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    stats = {**distributions(), **residuals(), **lighting_test()}
    prep_flow(); model_comparison(); consistency(); scenarios()
    (FIG / "report_stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))
    assert len(list(FIG.glob("*.png"))) == 7


if __name__ == "__main__":
    main()
