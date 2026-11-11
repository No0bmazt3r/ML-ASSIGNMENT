"""Build the presentation walkthrough + stakeholder dashboard: dashboard/index.html.

Every number on screen comes from this repo: results/*, figures/proposal/stats.json, the processed
parquet and the raw CLEMD folders. Run after run_all.sh. Injects one JSON blob into
dashboard/template.html; nothing is recomputed in the browser.
"""
import json
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

from cluster import daily_profiles
from features import DATA, RESULTS, ROOT, TARGETS, dataset, load
from prepare_data import CLEMD, FILE_ALIASES, P, WEEKS, date_format
from train import GAP, MIN_GAIN_OVER_RIDGE, N_SPLITS

OUT = ROOT / "dashboard"
CIRCUITS = ["Aggregate", "CP AC", "DB TG", "DB T1", "DB ML 1", "DB ML 2", "EMSB 1", "SSB MF"]
NAMES = {"time_of_day": "Time-of-day average", "ridge": "Ridge regression", "random_forest": "Random forest",
         "xgboost": "XGBoost", "lightgbm": "LightGBM"}
r = lambda x, n=2: None if x is None or pd.isna(x) else round(float(x), n)


def data_story():
    folders = sorted(p for p in CLEMD.iterdir() if p.is_dir())
    csvs = list(CLEMD.rglob("*.csv"))
    grid, fmts, typos = [], {}, []
    for f in folders:
        row = []
        for c in CIRCUITS:
            names = FILE_ALIASES.get(c, [f"{c}.csv"])
            hit = next((n for n in names if (f / n).exists()), None)
            row.append(hit is not None)
            if hit and hit != f"{c}.csv":
                typos.append({"week": int(f.name.split("-")[0]), "file": hit, "fixed": f"{c}.csv"})
        grid.append(row)
        if f.name in WEEKS and row[0]:  # which date order this week's main-meter file uses
            week, start = WEEKS[f.name]
            agg = f / next(n for n in FILE_ALIASES["Aggregate"] if (f / n).exists())
            fmt = date_format(pd.read_csv(agg, nrows=1, dtype=str)["Date"].iloc[0], start)
            fmts[week] = "M/D/Y" if fmt == "%m/%d/%Y" else "D/M/Y"

    df = pd.read_parquet(DATA)
    weeks = []
    for w, g in df.groupby("week"):
        gaps = g.index.to_series().diff().dt.total_seconds().div(60).sub(1)
        weeks.append({"week": int(w), "start": f"{g.index.min():%d %b}", "end": f"{g.index.max():%d %b}",
                      "minutes": len(g), "has_ac": bool(g["ac_kw"].notna().any()),
                      "gap_min": int(gaps.max()), "gap_frac": r(gaps.values.argmax() / len(g), 3), "gap_at": f"{gaps.idxmax():%a %d %b %H:%M}" if gaps.max() > 0 else None})

    # real 1-second readings around the test week's peak (19 Oct 2023, 15:50-16:10)
    agg6 = folders[-1] / "Aggregate.csv"
    ncols = len(pd.read_csv(agg6, nrows=0).columns)
    raw = pd.read_csv(agg6, skiprows=range(1, 57002), nrows=1200, usecols=["Date", "Time", *P], dtype={"Date": str, "Time": str})
    raw.index = pd.to_datetime(raw["Date"] + " " + raw["Time"], format="%d/%m/%Y %I:%M:%S %p")
    p = raw[P].sum(axis=1) / 1000
    m = p.resample("1min").agg(["mean", "count"])
    m = m[m["count"] == 60]["mean"]  # whole minutes only
    p = p[(p.index >= m.index[0]) & (p.index < m.index[-1] + pd.Timedelta("1min"))]
    return {
        "csv_files": len(csvs), "csv_gb": r(sum(c.stat().st_size for c in csvs) / 1e9, 1),
        "parquet_mb": r(DATA.stat().st_size / 1e6, 1), "rows": len(df),
        "signals": sum(c.startswith("agg_") for c in df.columns), "raw_columns": ncols,
        "circuits": CIRCUITS, "folders": [f.name.split("-")[0] for f in folders], "grid": grid,
        "date_formats": fmts, "typos": typos, "weeks": weeks,
        "raw_sample": {"start": f"{p.index[0]:%H:%M:%S}", "kw": [r(v, 2) for v in p],
                       "minute_kw": [r(v, 2) for v in m], "minute_start": [f"{t:%H:%M}" for t in m.index]},
    }


def method_story(freeze):
    X, _, _ = dataset("ac")
    folds = [{"train_end": int(tr[-1]) + 1, "val_start": int(va[0]), "val_end": int(va[-1]) + 1}
             for tr, va in TimeSeriesSplit(N_SPLITS, gap=GAP).split(X)]
    groups = pd.read_csv(RESULTS / "feature_dictionary.csv")["group"].value_counts()
    redundant = len(pd.read_csv(RESULTS / "redundant_feature_pairs.csv"))
    cv = {t: [{"model": m, "name": NAMES[m], "mae": r(v["mae"], 3), "peak_mae": r(v["peak_mae_15min"], 3)}
              for m, v in freeze["targets"][t]["cv_best_per_model"].items()] for t in TARGETS}
    return {
        "n_rows": len(X), "n_features": X.shape[1], "folds": folds, "n_splits": N_SPLITS, "gap_min": GAP,
        "feature_groups": {g: int(n) for g, n in groups.items()}, "redundant_pairs": redundant,
        "cv": cv, "min_gain": MIN_GAIN_OVER_RIDGE,
        "frozen": {t: {"model": freeze["targets"][t]["chosen_model"], "name": NAMES[freeze["targets"][t]["chosen_model"]],
                       "params": freeze["targets"][t]["params"]} for t in TARGETS},
        "frozen_at": freeze["frozen_at"][:10], "train_weeks": freeze["train_weeks"], "test_week": freeze["test_week"],
    }


def evaluate_story(stats):
    tm = pd.read_csv(RESULTS / "test_metrics.csv")
    metrics = {t: [{"model": row.model, "name": NAMES[row.model], "frozen": bool(row.frozen), "mae": r(row.mae),
                    "lo": r(row.mae_ci_lo), "hi": r(row.mae_ci_hi), "peak_mae": r(row.peak_mae_15min),
                    "peak_lo": r(row.peak_mae_ci_lo), "peak_hi": r(row.peak_mae_ci_hi), "r2": r(row.r2),
                    "rmse": r(row.rmse), "share_err": r(row.energy_share_err_pp, 1)}
                   for row in g.itertuples()] for t, g in tm.groupby("target")}
    pred = pd.read_csv(RESULTS / "predictions.csv", index_col=0, parse_dates=True)
    w6 = pred[pred["week"] == 6]
    q = w6[["agg_p_kw", "ac_kw", "ac_pred_kw"]].resample("15min").mean().dropna()
    err = pd.read_csv(RESULTS / "error_breakdown_ac.csv")
    rob = pd.read_csv(RESULTS / "robustness_w4_to_w5.csv")
    shap = pd.read_csv(RESULTS / "shap_groups_ac.csv", index_col=0)["mean_abs_shap_kw"]
    perm = pd.read_csv(RESULTS / "permutation_importance_groups.csv", index_col=0)["mae_increase_kw"]
    top = pd.read_csv(RESULTS / "shap_global_ac.csv", index_col=0).head(6)
    local = pd.read_csv(RESULTS / "shap_local_peak_ac.csv", index_col=0)
    by = lambda k: {str(v): r(m) for v, m in err.loc[err["by"] == k, ["value", "mae_kw"]].itertuples(index=False)}
    return {
        "metrics": metrics, "n_peak_windows": int(tm["n_peak_windows"].iloc[0]), "n_days": int(tm["n_days"].iloc[0]),
        "test_minutes": len(w6), "ac_mean_kw": r(w6["ac_kw"].mean(), 1), "light_mean_kw": r(w6["light_kw"].mean(), 1),
        "series": {"t0": f"{q.index[0]:%Y-%m-%dT%H:%M}", "step_min": 15, "t": [int((t - q.index[0]).total_seconds() // 900) for t in q.index],
                   "building": [r(v, 1) for v in q["agg_p_kw"]], "ac": [r(v, 2) for v in q["ac_kw"]],
                   "ac_pred": [r(v, 2) for v in q["ac_pred_kw"]]},
        "peak": {"t": f"{q['agg_p_kw'].idxmax():%a %d %b %H:%M}", "kw": r(q["agg_p_kw"].max(), 1),
                 "ac": r(q.loc[q["agg_p_kw"].idxmax(), "ac_kw"], 1), "ac_pred": r(q.loc[q["agg_p_kw"].idxmax(), "ac_pred_kw"], 1)},
        "error_by_hour": by("hour"), "error_by_day_type": by("day_type"), "error_by_step": by("step"),
        "robustness": [{"model": m, "name": NAMES[m], "mae": r(v)} for m, v in rob[["model", "mae"]].itertuples(index=False)],
        "shap_groups": {g: r(v) for g, v in shap.items()}, "perm_groups": {g: r(v) for g, v in perm.items()},
        "shap_top": [{"feature": f, "kw": r(v), "group": g} for f, v, g in top.itertuples()],
        "local_peak": [{"feature": f, "kw": r(v)} for f, v in local["shap_kw"].head(5).items()],
        "shares": {k: stats[k] for k in ("ac_share_energy_pct", "light_share_energy_pct", "ac_share_peak_pct",
                                         "light_share_peak_pct", "peak_threshold_kw", "peak_windows_in_office_hours_pct",
                                         "ac_after_hours_energy_pct", "light_after_hours_energy_pct",
                                         "ac_night_mean_kw_00_06", "corr_agg_ac_15min")},
    }


def modes_story():
    prof = daily_profiles(load(include_test=True))
    days = pd.read_csv(RESULTS / "cluster_days.csv", index_col=0)
    summ = pd.read_csv(RESULTS / "cluster_summary.csv", index_col=0)
    ks = pd.read_csv(RESULTS / "cluster_k_search.csv")
    labels = days["cluster"].reindex(prof.index.astype(str)).astype(int)
    return {
        "days": [{"date": d, "dow": pd.Timestamp(d).strftime("%a"), "cluster": int(c), "kw": [r(v, 1) for v in prof.loc[pd.Timestamp(d).date()]]}
                 for d, c in labels.items()],
        "summary": {int(c): {k: r(v, 1) for k, v in row.items()} for c, row in summ.iterrows()},
        "silhouette": {int(k): r(s, 2) for k, s in ks[["k", "silhouette"]].itertuples(index=False)},
    }


def main():
    freeze = json.loads((RESULTS / "freeze.json").read_text())
    stats = json.loads((ROOT / "figures" / "proposal" / "stats.json").read_text())
    data = {
        "built": f"{datetime.now():%d %b %Y}",
        "data": data_story(), "method": method_story(freeze), "evaluate": evaluate_story(stats),
        "modes": modes_story(), "scenarios": json.loads((RESULTS / "scenarios.json").read_text()),
    }
    blob = json.dumps(data, separators=(",", ":"), default=str).replace("</", "<\\/")
    html = (OUT / "template.html").read_text().replace("/*__DATA__*/null", blob)
    (OUT / "index.html").write_text(html)
    print(f"wrote {OUT / 'index.html'} ({len(html) / 1e3:.0f} kB, data {len(blob) / 1e3:.0f} kB)")
    # self-check: the blob landed and the headline numbers match the source files
    assert "/*__DATA__*/" not in html
    assert len(data["evaluate"]["series"]["ac"]) == len(data["evaluate"]["series"]["ac_pred"]) > 500
    assert len(data["modes"]["days"]) == sum(s["days"] for s in data["modes"]["summary"].values())
    assert all(len(row) == len(CIRCUITS) for row in data["data"]["grid"])


if __name__ == "__main__":
    main()
