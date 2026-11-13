"""Feature-group ablation for the frozen A/C model (report Section 4.4), dev weeks only.

Same LightGBM settings, same TimeSeriesSplit folds as train.py; only the input columns change.
The test week is never loaded and the frozen model/freeze.json are untouched: this is evidence
about the features, not a new model choice. Also answers Section 7.4's open question: how
accurate is the method if a UTP meter logs only kW (no harmonics / power quality)?
Writes results/ablation_cv.csv.
"""
import json

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

from features import RESULTS, build, dataset, load
from train import GAP, MODELS, N_SPLITS, scores


def feature_sets(cols: list[str], groups: dict[str, str]) -> dict[str, list[str]]:
    by = lambda *g: [c for c in cols if groups[c] in g]
    kw_total = ["agg_p_kw", "agg_p_kw_std", "agg_p_kw_min", "agg_p_kw_max"]
    duplicates = {c for c in cols if c.startswith("ratio_") or c.endswith("H1")}  # Section 4.2: exact copies / constants
    sets = {"all 98 features (frozen)": cols}
    for g in ("harmonics", "power_quality", "temporal", "calendar"):
        sets[f"without {g.replace('_', ' ')}"] = [c for c in cols if groups[c] != g]
    sets["duplicates removed (73)"] = [c for c in cols if c not in duplicates]
    sets["power meter, no harmonics/PQ"] = by("power", "temporal", "calendar")
    sets["kW-only meter"] = kw_total + by("temporal", "calendar")
    sets["calendar only"] = by("calendar")
    return sets


def main():
    X, y, meta = dataset("ac")
    _, groups = build(load())
    params = json.loads((RESULTS / "freeze.json").read_text())["targets"]["ac"]["params"]
    make = MODELS["lightgbm"][0]
    folds = list(TimeSeriesSplit(N_SPLITS, gap=GAP).split(X))
    rows = []
    for name, cols in feature_sets(list(X.columns), groups).items():
        for fold, (tr, va) in enumerate(folds):
            model = make(**params).fit(X.iloc[tr][cols], y.iloc[tr])
            pred = pd.Series(model.predict(X.iloc[va][cols]), index=X.index[va])
            rows.append({"feature_set": name, "n_features": len(cols), "fold": fold,
                         **scores(y.iloc[va], pred, meta["agg_p_kw"].iloc[va])})
        last = pd.DataFrame(rows[-N_SPLITS:])
        print(f"{name:32s} {len(cols):3d} feats  MAE {last.mae.mean():.3f}  peak MAE {last.peak_mae_15min.mean():.3f}")
    df = pd.DataFrame(rows)
    summary = df.groupby(["feature_set", "n_features"], sort=False).agg(
        mae=("mae", "mean"), mae_sd=("mae", "std"), rmse=("rmse", "mean"),
        peak_mae=("peak_mae_15min", "mean"), energy_share_err_pp=("energy_share_err_pp", "mean")).reset_index()
    full = summary.loc[0, "mae"]
    summary["mae_change_vs_full_pct"] = 100 * (summary["mae"] / full - 1)
    summary.round(4).to_csv(RESULTS / "ablation_cv.csv", index=False)
    print(summary.round(3).to_string(index=False))
    # self-check: the full set reproduces the frozen CV MAE in freeze.json
    frozen = json.loads((RESULTS / "freeze.json").read_text())["targets"]["ac"]["cv_best_per_model"]["lightgbm"]["mae"]
    assert np.isclose(full, frozen, atol=1e-3), (full, frozen)


if __name__ == "__main__":
    main()
