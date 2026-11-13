# step 2: turn the main meter data into model features (no sub-meter data is used as input)
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed" / "clemd_1min.parquet"
RESULTS = ROOT / "results"
# week 6 is our sealed test week, we do not touch it until the model is frozen
TEST_WEEK = 6
WORK_START, WORK_END = 8, 17
LAGS, WINDOWS = (1, 5, 15, 60), (15, 60)
TARGETS = {"ac": "ac_kw", "light": "light_kw"}


# load the 1-minute data, by default without the test week
def load(include_test: bool = False) -> pd.DataFrame:
    if not DATA.exists():
        raise SystemExit(f"{DATA} not found: run prepare_data.py first (it needs the raw CLEMD folders, see README > Data)")
    df = pd.read_parquet(DATA)
    return df if include_test else df[df["week"] != TEST_WEEK]


# make all 98 features and remember which group each one belongs to
def build(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    groups, cols = {}, {}

    def add(group, name, values):
        cols[name], groups[name] = values, group

    agg = df.filter(like="agg_")
    # raw main meter columns: power, power quality and harmonics
    for c in agg:
        if c.startswith("agg_Current") and "H" in c.removeprefix("agg_Current"):
            group = "harmonics"
        elif any(k in c for k in ("PF", "THD", "Voltage", "Current", "Frequency")):
            group = "power_quality"
        else:
            group = "power"
        add(group, c, agg[c])
    # harmonic size compared to the fundamental for each phase
    for ph in "123":
        h1 = agg[f"agg_Current{ph}H1"].replace(0, np.nan)
        for h in (3, 5, 7, 9, 11, 13, 15):
            add("harmonics", f"ratio_{ph}H{h}", agg[f"agg_Current{ph}H{h}"] / h1)

    # split the data where there are gaps so lags never jump across a missing day or the outage
    seg = (df.index.to_series().diff() != pd.Timedelta("1min")).cumsum()
    p = df["agg_p_kw"].groupby(seg)
    # past power values (lags) and rolling averages
    for lag in LAGS:
        add("temporal", f"p_lag{lag}", p.shift(lag))
    for w in WINDOWS:
        add("temporal", f"p_roll{w}_mean", p.transform(lambda s: s.rolling(w).mean()))
        add("temporal", f"p_roll{w}_std", p.transform(lambda s: s.rolling(w).std()))
    add("temporal", "p_diff1", p.diff())

    # calendar features: hour of day, weekday, weekend and office hours
    t = df.index
    hour = t.hour + t.minute / 60
    weekend = t.day_of_week >= 5
    add("calendar", "hour_sin", np.sin(2 * np.pi * hour / 24))
    add("calendar", "hour_cos", np.cos(2 * np.pi * hour / 24))
    add("calendar", "dayofweek", t.day_of_week)
    add("calendar", "weekend", weekend.astype(int))
    add("calendar", "office_hours", (~weekend & (t.hour >= WORK_START) & (t.hour < WORK_END)).astype(int))

    X = pd.DataFrame(cols, index=df.index)
    return X, groups


# X, y and extra info for one target (ac or light), only rows with all features filled
def dataset(target: str, include_test: bool = False):
    df = load(include_test)
    X, _ = build(df)
    keep = X.notna().all(axis=1) & df[TARGETS[target]].notna()
    return X[keep], df.loc[keep, TARGETS[target]], df.loc[keep, ["agg_p_kw", "week"]]


# save the feature list and check which features are almost duplicates (training weeks only)
def main():
    df = load()
    X, groups = build(df)
    RESULTS.mkdir(exist_ok=True)
    pd.Series(groups, name="group").rename_axis("feature").to_csv(RESULTS / "feature_dictionary.csv")
    corr = X.dropna().corr().abs()
    pairs = corr.where(np.triu(np.ones(corr.shape, bool), 1)).stack()
    pairs[pairs > 0.98].sort_values(ascending=False).rename("abs_r").to_csv(RESULTS / "redundant_feature_pairs.csv")
    print(pd.Series(groups).value_counts().to_string(), f"\ntotal {len(groups)} features,",
          f"{(pairs > 0.98).sum()} pairs with |r| > 0.98")
    # check that the first minute after a gap has no lag value
    after_gap = df.index.to_series().diff() > pd.Timedelta("1min")
    assert X.loc[after_gap, "p_lag1"].isna().all()
    assert (X["p_lag1"].iloc[1:5].values == df["agg_p_kw"].iloc[0:4].values).all()


if __name__ == "__main__":
    main()
