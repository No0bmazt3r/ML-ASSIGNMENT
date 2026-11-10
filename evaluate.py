"""One-time test on sealed week 6 + robustness test (proposal Section 4.3 step 6, Phase 3).

Refits every model at its frozen / best-CV config on the dev weeks, scores it on week 6, and adds
day-block bootstrap CIs, NDE, an error breakdown and a week-4 -> week-5 robustness test.
Writes results/test_metrics.csv, results/robustness_w4_to_w5.csv, results/error_breakdown_ac.csv,
results/predictions.csv (out-of-sample estimates used by cluster.py / scenarios.py) and figures/results/.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from features import RESULTS, ROOT, TARGETS, TEST_WEEK, build, load
from train import MODELS, scores

FIG = ROOT / "figures" / "results"
FREEZE = json.loads((RESULTS / "freeze.json").read_text())
TRAIN_WEEKS = {t: set(w) for t, w in FREEZE["train_weeks"].items()}
N_BOOT = 2000
AC, LIGHT, INK2, GRID, SURF = "#2a78d6", "#eb6834", "#52514e", "#e6e5e0", "#fcfcfb"  # same palette as proposal
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
                     "axes.grid": True, "grid.color": GRID, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlelocation": "left", "legend.frameon": False,
                     "savefig.dpi": 200, "savefig.bbox": "tight", "font.size": 10})


def make(target: str, model: str):
    """Unfitted estimator: the frozen model, or any other model at its best CV config (for comparison)."""
    params = FREEZE["targets"][target]["cv_best_params_per_model"][model]
    return MODELS[model][0](**params)


def frozen(target: str):
    return make(target, FREEZE["targets"][target]["chosen_model"])


def full_table():
    """All weeks (test included), features + targets, rows with complete features."""
    df = load(include_test=True)
    X, _ = build(df)
    keep = X.notna().all(axis=1)
    return X[keep], df[keep]


def bootstrap(y, pred, agg, rng) -> dict:
    """95% CIs by resampling whole days (block bootstrap) for MAE and peak-window MAE."""
    q = pd.DataFrame({"y": y, "pred": pred, "agg": agg}).resample("15min").mean().dropna()
    q["peak"] = q["agg"] >= q["agg"].quantile(0.95)
    q["err"] = (q["pred"] - q["y"]).abs()
    m = pd.DataFrame({"err": (pred - y).abs()})
    days = np.unique(q.index.date)
    q_day, m_day = q.groupby(q.index.date), m.groupby(m.index.date)
    sums = pd.DataFrame({"m_sum": m_day["err"].sum(), "m_n": m_day["err"].size(),
                         "p_sum": q_day.apply(lambda d: d.loc[d.peak, "err"].sum()),
                         "p_n": q_day["peak"].sum()}).reindex(days).fillna(0)
    idx = rng.integers(0, len(days), size=(N_BOOT, len(days)))
    s = sums.to_numpy()[idx].sum(axis=1)  # (N_BOOT, 4)
    mae, peak = s[:, 0] / s[:, 1], s[:, 2] / np.where(s[:, 3] > 0, s[:, 3], np.nan)
    lo, hi = lambda a: np.nanpercentile(a, 2.5), lambda a: np.nanpercentile(a, 97.5)
    return {"mae_ci_lo": lo(mae), "mae_ci_hi": hi(mae), "peak_mae_ci_lo": lo(peak), "peak_mae_ci_hi": hi(peak),
            "n_peak_windows": int(q["peak"].sum()), "n_days": len(days)}


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(0)
    X, df = full_table()
    rows, preds = [], {}
    for target, col in TARGETS.items():
        train = df["week"].isin(TRAIN_WEEKS[target]) & df[col].notna()
        test = df["week"] == TEST_WEEK
        for model in MODELS:
            est = make(target, model).fit(X[train], df.loc[train, col])
            pred = pd.Series(est.predict(X[test]), index=X.index[test])
            y, agg = df.loc[test, col], df.loc[test, "agg_p_kw"]
            is_frozen = model == FREEZE["targets"][target]["chosen_model"]
            rows.append({"target": target, "model": model, "frozen": is_frozen, **scores(y, pred, agg),
                         "nde": np.sqrt(((pred - y) ** 2).sum() / (y ** 2).sum()), **bootstrap(y, pred, agg, rng)})
            if is_frozen:  # out-of-sample estimates everywhere the model did not train: test week + weeks 2-3
                unseen = ~df["week"].isin(TRAIN_WEEKS[target])
                preds[f"{target}_pred_kw"] = pd.Series(est.predict(X[unseen]), index=X.index[unseen])
    metrics = pd.DataFrame(rows)
    metrics.to_csv(RESULTS / "test_metrics.csv", index=False)

    out = df[["week", "agg_p_kw", "ac_kw", "light_kw"]].join(pd.DataFrame(preds))
    out = out[out["ac_pred_kw"].notna() | out["light_pred_kw"].notna()]  # rows with an out-of-sample estimate
    out.round(4).to_csv(RESULTS / "predictions.csv")

    # robustness: does a model trained on one week hold up on the next? (A/C, every model)
    rob = []
    tr, te = (df["week"] == 4), (df["week"] == 5)
    for model in MODELS:
        est = make("ac", model).fit(X[tr], df.loc[tr, "ac_kw"])
        pred = pd.Series(est.predict(X[te]), index=X.index[te])
        rob.append({"model": model, **scores(df.loc[te, "ac_kw"], pred, df.loc[te, "agg_p_kw"])})
    pd.DataFrame(rob).to_csv(RESULTS / "robustness_w4_to_w5.csv", index=False)

    # error breakdown for the frozen A/C model on week 6
    w6 = out[out["week"] == TEST_WEEK].copy()
    w6["abs_err"] = (w6["ac_pred_kw"] - w6["ac_kw"]).abs()
    w6["hour"] = w6.index.hour
    w6["day_type"] = np.where(w6.index.day_of_week >= 5, "weekend", "weekday")
    w6["load_band"] = pd.cut(w6["agg_p_kw"], [0, 15, 30, 45, 60, 200], labels=["<15", "15-30", "30-45", "45-60", "60+"])
    w6["step"] = w6["agg_p_kw"].diff().abs() > 5  # sudden switching (>5 kW in a minute)
    parts = [w6.groupby(k, observed=True)["abs_err"].agg(["mean", "count"]).assign(by=k).rename_axis("value").reset_index()
             for k in ("hour", "day_type", "load_band", "step")]
    pd.concat(parts).rename(columns={"mean": "mae_kw"}).round(3).to_csv(RESULTS / "error_breakdown_ac.csv", index=False)

    # figures: test-week time series, predicted vs actual, error by hour
    q = w6[["ac_kw", "ac_pred_kw", "agg_p_kw"]].resample("15min").mean().dropna()
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(q.index, q["agg_p_kw"], color=INK2, lw=1, alpha=0.6, label="Whole building (input)")
    ax.plot(q.index, q["ac_kw"], color=AC, lw=2, label="A/C measured (sub-meter)")
    ax.plot(q.index, q["ac_pred_kw"], color=LIGHT, lw=1.3, ls="--", label="A/C estimated from main meter")
    ax.set_ylabel("Real power, 15-min mean (kW)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d %b"))
    ax.legend(loc="upper right", ncol=3, fontsize=8.5)
    ax.set_title("A/C estimated from the main meter vs measured, test week (19-24 Oct 2023)")
    fig.savefig(FIG / "test_week_timeseries.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.5, 5))
    peak = q["agg_p_kw"] >= q["agg_p_kw"].quantile(0.95)
    ax.scatter(q["ac_kw"][~peak], q["ac_pred_kw"][~peak], s=8, color=AC, alpha=0.5, label="All 15-min windows")
    ax.scatter(q["ac_kw"][peak], q["ac_pred_kw"][peak], s=18, color=LIGHT, label="Top 5% demand windows")
    lim = q[["ac_kw", "ac_pred_kw"]].max().max() * 1.05
    ax.plot([0, lim], [0, lim], color=INK2, lw=1, ls=":")
    ax.set_xlim(0, lim); ax.set_ylim(0, lim)
    ax.set_xlabel("Measured A/C (kW)"); ax.set_ylabel("Estimated A/C (kW)"); ax.legend(loc="upper left")
    ax.set_title("Estimated vs measured A/C, test week")
    fig.savefig(FIG / "test_pred_vs_actual.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 3.5))
    by_hour = w6.groupby(["hour", "day_type"])["abs_err"].mean().unstack()
    for col, c in (("weekday", AC), ("weekend", INK2)):
        ax.plot(by_hour.index, by_hour[col], color=c, marker="o", ms=3, label=col.capitalize())
    ax.set_xticks(range(0, 24, 2)); ax.set_xlabel("Hour of day"); ax.set_ylabel("MAE (kW)"); ax.legend()
    ax.set_title("Where the A/C model errs: test-week error by hour")
    fig.savefig(FIG / "test_error_by_hour.png"); plt.close(fig)

    show = ["target", "model", "frozen", "mae", "mae_ci_lo", "mae_ci_hi", "rmse", "r2", "peak_mae_15min",
            "peak_mae_ci_lo", "peak_mae_ci_hi", "energy_share_err_pp", "nde"]
    print(metrics[show].round(3).to_string(index=False))
    print("\nrobustness (train wk4 -> test wk5, A/C):\n", pd.DataFrame(rob).round(3).to_string(index=False))
    # self-check: the frozen A/C model's test predictions line up with the truth index and are finite
    assert w6["ac_pred_kw"].notna().all() and np.isfinite(w6["ac_pred_kw"]).all() and len(w6) > 8000


if __name__ == "__main__":
    main()
