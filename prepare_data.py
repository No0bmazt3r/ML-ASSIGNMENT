# step 1: read the raw CLEMD csv files, clean them and save one 1-minute table
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
CLEMD = ROOT / "data" / "clemd"
OUT = ROOT / "data" / "processed" / "clemd_1min.parquet"

# folder name -> (week number, start date). week 1 is not here because it has no main meter file
WEEKS = {
    "2-21 Sep to  27 Sep": (2, datetime(2023, 9, 21)),
    "3-27 Sep to 4 Oct": (3, datetime(2023, 9, 27)),
    "4-4 Oct to 11 Oct": (4, datetime(2023, 10, 4)),
    "5-11 Oct to 18 Oct": (5, datetime(2023, 10, 11)),
    "6-18 Oct to 25 Oct": (6, datetime(2023, 10, 18)),
}
# sub-meter files we need: the A/C panel and the three lighting boards
SUBS = {"CP AC": "ac", "DB TG": "tg", "DB T1": "t1", "DB ML 1": "ml1"}
# week 4 has the main meter file spelt wrong (Aggregtae.csv) so we accept both names
FILE_ALIASES = {"Aggregate": ["Aggregate.csv", "Aggregtae.csv"]}
P = ["Real Power1", "Real Power2", "Real Power3"]


# some files use M/D/Y and some D/M/Y, so we try both and keep the one that matches the folder start date
def date_format(first_date: str, start: datetime) -> str:
    for fmt in ("%m/%d/%Y", "%d/%m/%Y"):
        try:
            if datetime.strptime(first_date, fmt) == start:
                return fmt
        except ValueError:
            pass
    raise ValueError(f"first date {first_date!r} matches neither format for {start:%d %b}")


# find the csv for one circuit inside a week folder (returns None if the file is missing)
def find(folder: str, circuit: str) -> Path | None:
    for name in FILE_ALIASES.get(circuit, [f"{circuit}.csv"]):
        if (CLEMD / folder / name).exists():
            return CLEMD / folder / name
    return None


# read one csv, parse the timestamps and add total real power in kW
def load(path: Path, start: datetime, all_cols: bool) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=None if all_cols else ["Date", "Time", *P], dtype={"Date": str, "Time": str})
    df = df.dropna(subset=["Date"])
    fmt = date_format(df["Date"].iloc[0], start)
    df.index = pd.to_datetime(df.pop("Date") + " " + df.pop("Time"), format=f"{fmt} %I:%M:%S %p")
    df = df.apply(pd.to_numeric, errors="coerce")
    df["p_kw"] = df[P].sum(axis=1) / 1000
    return df


# build one week: main meter + sub-meters, all averaged to 1 minute
def week_frame(folder: str, week: int, start: datetime) -> pd.DataFrame:
    agg = load(find(folder, "Aggregate"), start, all_cols=True)
    agg["q_kvar"] = agg[["Reactive Power1", "Reactive Power2", "Reactive Power3"]].sum(axis=1) / 1000
    agg["s_kva"] = agg[["Apparent Power1", "Apparent Power2", "Apparent Power3"]].sum(axis=1) / 1000
    p = agg["p_kw"].resample("1min")
    parts = [agg.add_prefix("agg_").resample("1min").mean(),
             p.std().rename("agg_p_kw_std"), p.min().rename("agg_p_kw_min"), p.max().rename("agg_p_kw_max")]
    # add each sub-meter if the file exists (weeks 2-3 have no A/C file)
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


# load every week, remove the power outage and save the parquet
def main():
    missing = [f for f in WEEKS if not (CLEMD / f).is_dir()]
    if missing:
        raise SystemExit("missing CLEMD folder(s) in data/clemd: " + ", ".join(repr(f) for f in missing)
                         + "\ndownload them from https://doi.org/10.6084/m9.figshare.c.6946581 (see README > Data)")
    frames = []
    for folder, (week, start) in WEEKS.items():
        print(f"loading week {week} ...", flush=True)
        frames.append(week_frame(folder, week, start))
    df = pd.concat(frames)
    # on 5 Oct the supply went down (all circuits ~0 V), that is not real demand so we drop it
    outage = df["agg_Voltage1"] < 100
    print(f"dropping {outage.sum()} outage minutes")
    df = df[~outage]
    df.columns = [c.replace(" ", "_") for c in df.columns]
    df["light_kw"] = df[["tg_kw", "t1_kw", "ml1_kw"]].sum(axis=1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT)
    # quick checks so we know the dates and values make sense
    assert df.index.min() >= datetime(2023, 9, 21, 23) and df.index.max() <= datetime(2023, 10, 25, 1)
    assert df.index.is_monotonic_increasing and not df.index.duplicated().any()
    assert df.loc[df.week >= 4, "ac_kw"].notna().mean() > 0.99 and df.loc[df.week < 4, "ac_kw"].isna().all()
    assert 5 < df["agg_p_kw"].mean() < 100 and (df["agg_p_kw"] >= df["light_kw"]).mean() > 0.99
    print(df.shape, df.index.min(), df.index.max())
    print(df.groupby("week")[["agg_p_kw", "ac_kw", "light_kw"]].agg(["count", "mean", "max"]).round(1))


if __name__ == "__main__":
    main()
