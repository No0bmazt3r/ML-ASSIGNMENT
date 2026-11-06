"""Main-meter feature table (proposal Section 3.2 / 4.3 step 3).

Every input comes from the Aggregate (main) meter or the clock: never from a sub-meter.
Run directly to write the feature dictionary and redundancy check to results/.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed" / "clemd_1min.parquet"
RESULTS = ROOT / "results"
TEST_WEEK = 6  # sealed until the model freeze (proposal Section 6)
WORK_START, WORK_END = 8, 17  # weekday office hours
LAGS, WINDOWS = (1, 5, 15, 60), (15, 60)  # minutes
TARGETS = {"ac": "ac_kw", "light": "light_kw"}


def load(include_test: bool = False) -> pd.DataFrame:
    df = pd.read_parquet(DATA)
    return df if include_test else df[df["week"] != TEST_WEEK]


def build(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    """Return (X, {feature: group}). Rows whose lags reach before a data gap are NaN; caller drops them."""
    groups, cols = {}, {}

    def add(group, name, values):
        cols[name], groups[name] = values, group

    agg = df.filter(like="agg_")
    for c in agg:
        if c.startswith("agg_Current") and "H" in c.removeprefix("agg_Current"):
            group = "harmonics"
        elif any(k in c for k in ("PF", "THD", "Voltage", "Current", "Frequency")):
            group = "power_quality"
        else:
            group = "power"
        add(group, c, agg[c])
    for ph in "123":  # harmonic content relative to the fundamental
        h1 = agg[f"agg_Current{ph}H1"].replace(0, np.nan)
        for h in (3, 5, 7, 9, 11, 13, 15):
            add("harmonics", f"ratio_{ph}H{h}", agg[f"agg_Current{ph}H{h}"] / h1)

    # temporal: computed inside contiguous segments so nothing crosses the week gaps or the outage
    seg = (df.index.to_series().diff() != pd.Timedelta("1min")).cumsum()
    p = df["agg_p_kw"].groupby(seg)
    for lag in LAGS:
        add("temporal", f"p_lag{lag}", p.shift(lag))
    for w in WINDOWS:
        add("temporal", f"p_roll{w}_mean", p.transform(lambda s: s.rolling(w).mean()))
        add("temporal", f"p_roll{w}_std", p.transform(lambda s: s.rolling(w).std()))
    add("temporal", "p_diff1", p.diff())

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


def dataset(target: str, include_test: bool = False):
    """X, y, meta for one target ('ac' or 'light'), rows with complete features and a measured target."""
    df = load(include_test)
    X, _ = build(df)
    keep = X.notna().all(axis=1) & df[TARGETS[target]].notna()
    return X[keep], df.loc[keep, TARGETS[target]], df.loc[keep, ["agg_p_kw", "week"]]


def main():
    df = load()  # dev weeks only: the redundancy check must not look at the test week
    X, groups = build(df)
    RESULTS.mkdir(exist_ok=True)
    pd.Series(groups, name="group").rename_axis("feature").to_csv(RESULTS / "feature_dictionary.csv")
    corr = X.dropna().corr().abs()
    pairs = corr.where(np.triu(np.ones(corr.shape, bool), 1)).stack()
    pairs[pairs > 0.98].sort_values(ascending=False).rename("abs_r").to_csv(RESULTS / "redundant_feature_pairs.csv")
    print(pd.Series(groups).value_counts().to_string(), f"\ntotal {len(groups)} features,",
          f"{(pairs > 0.98).sum()} pairs with |r| > 0.98")
    # self-check: lags never cross a gap (first minute after the 5 Oct outage has no lag-1)
    after_gap = df.index.to_series().diff() > pd.Timedelta("1min")
    assert X.loc[after_gap, "p_lag1"].isna().all()
    assert (X["p_lag1"].iloc[1:5].values == df["agg_p_kw"].iloc[0:4].values).all()


if __name__ == "__main__":
    main()
