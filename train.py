"""Baselines + tree models, tuned with expanding-window CV on dev weeks only, then frozen.

Proposal Section 4.3 steps 4-5 / Phases 1-2. The test week (6) is never loaded here.
Writes results/cv_results.csv (every config x fold) and results/freeze.json (the model freeze record).
"""
import json
import subprocess
import time
from datetime import datetime

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import ParameterGrid, TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from features import RESULTS, dataset

N_SPLITS, GAP = 4, 60  # 4 expanding folds; 60-min gap so the longest lag can't see the validation fold
MIN_GAIN_OVER_RIDGE = 0.05  # a tree model must cut Ridge's CV MAE by >= 5% to be chosen (proposal 4.4)


class TimeOfDay(BaseEstimator, RegressorMixin):
    """Baseline 1: mean target for the same hour on the same day type (weekday/weekend). No electrical input."""

    def fit(self, X, y):
        self.table_ = y.groupby([X.index.day_of_week >= 5, X.index.hour]).mean()
        self.default_ = y.mean()
        return self

    def predict(self, X):
        keys = zip(X.index.day_of_week >= 5, X.index.hour)
        return np.array([self.table_.get(k, self.default_) for k in keys])


# Small, pre-agreed search spaces (proposal Phase 2). Edit here BEFORE freezing, never after.
MODELS = {
    "time_of_day": (TimeOfDay, {}),
    "ridge": (lambda **p: make_pipeline(StandardScaler(), Ridge(**p)), {"alpha": [0.1, 1, 10, 100]}),
    "random_forest": (lambda **p: RandomForestRegressor(n_estimators=200, max_features=0.33, n_jobs=-1,
                                                        random_state=0, **p),
                      {"max_depth": [None, 12], "min_samples_leaf": [1, 5]}),
    "xgboost": (lambda **p: XGBRegressor(n_estimators=400, subsample=0.8, colsample_bytree=0.8, n_jobs=-1,
                                         random_state=0, **p),
                {"max_depth": [4, 6], "learning_rate": [0.03, 0.1]}),
    "lightgbm": (lambda **p: LGBMRegressor(n_estimators=400, subsample=0.8, subsample_freq=1,
                                           colsample_bytree=0.8, random_state=0, verbose=-1, **p),
                 {"num_leaves": [15, 63], "learning_rate": [0.03, 0.1]}),
}


def scores(y, pred, agg_kw) -> dict:
    """Proposal 4.4 metrics. Peak windows = top 5% of 15-min building demand within the evaluated period."""
    err = pred - y
    q = pd.DataFrame({"y": y, "pred": pred, "agg": agg_kw}).resample("15min").mean().dropna()
    peak = q[q["agg"] >= q["agg"].quantile(0.95)]
    return {
        "mae": np.abs(err).mean(),
        "rmse": np.sqrt((err ** 2).mean()),
        "r2": 1 - (err ** 2).sum() / ((y - y.mean()) ** 2).sum(),
        "peak_mae_15min": (peak["pred"] - peak["y"]).abs().mean(),
        "energy_share_err_pp": 100 * (pred.sum() - y.sum()) / agg_kw.sum(),
    }


def cross_validate(target: str) -> pd.DataFrame:
    X, y, meta = dataset(target)
    print(f"\n[{target}] {len(X)} rows, weeks {sorted(meta['week'].unique())}, {X.shape[1]} features")
    rows = []
    for name, (make, grid) in MODELS.items():
        for params in ParameterGrid(grid):
            for fold, (tr, va) in enumerate(TimeSeriesSplit(N_SPLITS, gap=GAP).split(X)):
                t0 = time.time()
                model = make(**params).fit(X.iloc[tr], y.iloc[tr])
                pred = pd.Series(model.predict(X.iloc[va]), index=X.index[va])
                rows.append({"target": target, "model": name, "params": json.dumps(params), "fold": fold,
                             "fit_s": time.time() - t0, **scores(y.iloc[va], pred, meta["agg_p_kw"].iloc[va])})
            last = pd.DataFrame(rows[-N_SPLITS:])
            print(f"  {name:14s} {json.dumps(params):48s} MAE {last.mae.mean():.3f}  "
                  f"peak MAE {last.peak_mae_15min.mean():.3f}")
    return pd.DataFrame(rows)


def choose(cv: pd.DataFrame) -> dict:
    """Best config per model by mean CV MAE; then the freeze rule against Ridge."""
    summary = cv.groupby(["model", "params"]).mean(numeric_only=True).drop(columns="fold").reset_index()
    best = summary.loc[summary.groupby("model")["mae"].idxmin()].set_index("model")
    ridge_mae = best.loc["ridge", "mae"]
    trees = best.drop(index=["time_of_day", "ridge"])
    top = trees["mae"].idxmin()
    chosen = top if trees.loc[top, "mae"] <= (1 - MIN_GAIN_OVER_RIDGE) * ridge_mae else "ridge"
    return {
        "chosen_model": chosen,
        "params": json.loads(best.loc[chosen, "params"]),
        "rule": f"lowest CV MAE among tree models, only if >= {MIN_GAIN_OVER_RIDGE:.0%} below Ridge; else Ridge",
        "cv_best_per_model": best.drop(columns="params").round(4).to_dict(orient="index"),
        "cv_best_params_per_model": {m: json.loads(p) for m, p in best["params"].items()},
    }


def main():
    RESULTS.mkdir(exist_ok=True)
    cv = pd.concat([cross_validate(t) for t in ("ac", "light")])
    cv.to_csv(RESULTS / "cv_results.csv", index=False)
    X, _, _ = dataset("ac")
    git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
    commit = git("rev-parse", "--short", "HEAD") + ("-dirty" if git("status", "--porcelain", "--", "*.py") else "")
    freeze = {
        "frozen_at": datetime.now().isoformat(timespec="seconds"),
        "git_commit": commit,
        "train_weeks": {"ac": [4, 5], "light": [2, 3, 4, 5]},
        "test_week": 6,
        "cv": f"TimeSeriesSplit(n_splits={N_SPLITS}, gap={GAP} min), expanding window",
        "features": list(X.columns),
        "targets": {t: choose(cv[cv.target == t]) for t in ("ac", "light")},
    }
    (RESULTS / "freeze.json").write_text(json.dumps(freeze, indent=2))
    for t, f in freeze["targets"].items():
        print(f"\nFROZEN [{t}]: {f['chosen_model']} {f['params']}")
        print(pd.DataFrame(f["cv_best_per_model"]).T[["mae", "rmse", "r2", "peak_mae_15min",
                                                      "energy_share_err_pp", "fit_s"]].round(3).to_string())


if __name__ == "__main__":
    main()
