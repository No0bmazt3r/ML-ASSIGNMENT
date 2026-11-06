"""Load CLEMD weeks 2-6, fix dates, resample 1 s -> 1 min, save parquet.

Output: data/processed/clemd_1min.parquet
  agg_*        main-meter signals (1-min mean) + agg_p_kw_std/min/max (within-minute)
  ac_kw        CP AC real power (NaN in weeks 2-3: no CP AC file)
  tg_kw, t1_kw, ml1_kw, light_kw (= tg + t1 + ml1)
  week         CLEMD week number (2-6). Week 6 is the sealed test week.
Week 1 is skipped: it has no Aggregate (main meter) file.
"""
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
CLEMD = ROOT / "data" / "clemd"
OUT = ROOT / "data" / "processed" / "clemd_1min.parquet"

WEEKS = {  # folder -> (week no., start date; each week starts 11:55 PM on this date)
    "2-21 Sep to  27 Sep": (2, datetime(2023, 9, 21)),
    "3-27 Sep to 4 Oct": (3, datetime(2023, 9, 27)),
    "4-4 Oct to 11 Oct": (4, datetime(2023, 10, 4)),
    "5-11 Oct to 18 Oct": (5, datetime(2023, 10, 11)),
    "6-18 Oct to 25 Oct": (6, datetime(2023, 10, 18)),
}
SUBS = {"CP AC": "ac", "DB TG": "tg", "DB T1": "t1", "DB ML 1": "ml1"}
FILE_ALIASES = {"Aggregate": ["Aggregate.csv", "Aggregtae.csv"]}  # week 4 typo
P = ["Real Power1", "Real Power2", "Real Power3"]


def date_format(first_date: str, start: datetime) -> str:
    """Files mix M/D/Y and D/M/Y: pick the one that maps row 1 to the folder start date."""
    for fmt in ("%m/%d/%Y", "%d/%m/%Y"):
        try:
            if datetime.strptime(first_date, fmt) == start:
                return fmt
        except ValueError:
            pass
    raise ValueError(f"first date {first_date!r} matches neither format for {start:%d %b}")


def find(folder: str, circuit: str) -> Path | None:
    for name in FILE_ALIASES.get(circuit, [f"{circuit}.csv"]):
        if (CLEMD / folder / name).exists():
            return CLEMD / folder / name
    return None


def load(path: Path, start: datetime, all_cols: bool) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=None if all_cols else ["Date", "Time", *P], dtype={"Date": str, "Time": str})
    df = df.dropna(subset=["Date"])  # trailing blank rows
    fmt = date_format(df["Date"].iloc[0], start)
    df.index = pd.to_datetime(df.pop("Date") + " " + df.pop("Time"), format=f"{fmt} %I:%M:%S %p")
    df = df.apply(pd.to_numeric, errors="coerce")
    df["p_kw"] = df[P].sum(axis=1) / 1000
    return df


def week_frame(folder: str, week: int, start: datetime) -> pd.DataFrame:
    agg = load(find(folder, "Aggregate"), start, all_cols=True)
    agg["q_kvar"] = agg[["Reactive Power1", "Reactive Power2", "Reactive Power3"]].sum(axis=1) / 1000
    agg["s_kva"] = agg[["Apparent Power1", "Apparent Power2", "Apparent Power3"]].sum(axis=1) / 1000
    p = agg["p_kw"].resample("1min")
    parts = [agg.add_prefix("agg_").resample("1min").mean(),
             p.std().rename("agg_p_kw_std"), p.min().rename("agg_p_kw_min"), p.max().rename("agg_p_kw_max")]
    for circuit, short in SUBS.items():
        path = find(folder, circuit)
        if path is None:
            print(f"  week {week}: no {circuit}")
            continue
        parts.append(load(path, start, all_cols=False)["p_kw"].resample("1min").mean().rename(f"{short}_kw"))
    out = pd.concat(parts, axis=1).dropna(subset=["agg_p_kw", "tg_kw", "t1_kw", "ml1_kw"])
    if "ac_kw" not in out:
        out["ac_kw"] = float("nan")
    out["week"] = week
    return out


def main():
    frames = []
    for folder, (week, start) in WEEKS.items():
        print(f"loading week {week} ...", flush=True)
        frames.append(week_frame(folder, week, start))
    df = pd.concat(frames)
    outage = df["agg_Voltage1"] < 100  # supply interruption (5 Oct 14:49-17:03): every circuit reads ~0 V
    print(f"dropping {outage.sum()} outage minutes")
    df = df[~outage]
    df.columns = [c.replace(" ", "_") for c in df.columns]
    df["light_kw"] = df[["tg_kw", "t1_kw", "ml1_kw"]].sum(axis=1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT)
    # self-check: dates landed in Sep-Oct 2023, no overlap, A/C only where CP AC exists, sane magnitudes
    assert df.index.min() >= datetime(2023, 9, 21, 23) and df.index.max() <= datetime(2023, 10, 25, 1)
    assert df.index.is_monotonic_increasing and not df.index.duplicated().any()
    assert df.loc[df.week >= 4, "ac_kw"].notna().mean() > 0.99 and df.loc[df.week < 4, "ac_kw"].isna().all()
    assert 5 < df["agg_p_kw"].mean() < 100 and (df["agg_p_kw"] >= df["light_kw"]).mean() > 0.99
    print(df.shape, df.index.min(), df.index.max())
    print(df.groupby("week")[["agg_p_kw", "ac_kw", "light_kw"]].agg(["count", "mean", "max"]).round(1))


if __name__ == "__main__":
    main()
