"""k-means on daily load-profile shapes + after-hours energy per operating mode (proposal Objective 5).

Clusters use the main meter only (normalised 24-h building profile), so they work where only a main
meter exists. Weeks 2-6 give ~30 full days. Per cluster: measured A/C and lighting after-hours energy
(where sub-meters exist) and the frozen model's out-of-sample A/C estimate (weeks 2, 3 and 6).
Writes results/cluster_*.csv and figures/results/cluster_profiles.png.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from evaluate import AC, FIG, INK2, LIGHT
from features import RESULTS, WORK_END, WORK_START, load

K_RANGE = range(2, 7)
COLORS = [AC, LIGHT, INK2, "#1baf7a", "#eda100", "#8a5cd6"]


def daily_profiles(df):
    """Hourly mean building kW per day; keep days with all 24 hours >= 45 min of data."""
    hourly = df["agg_p_kw"].resample("1h").agg(["mean", "count"])
    hourly = hourly[hourly["count"] >= 45]["mean"]
    prof = hourly.groupby([hourly.index.date, hourly.index.hour]).first().unstack()
    return prof.dropna()


def main():
    df = load(include_test=True)  # clustering is unsupervised: it never sees a target
    pred = pd.read_csv(RESULTS / "predictions.csv", index_col=0, parse_dates=True)
    df = df.join(pred[["ac_pred_kw"]])
    prof = daily_profiles(df)
    shape = prof.div(prof.max(axis=1), axis=0)  # compare days by shape, not size

    search = []
    for k in K_RANGE:
        km = KMeans(k, n_init=50, random_state=0).fit(shape)
        search.append({"k": k, "silhouette": silhouette_score(shape, km.labels_), "inertia": km.inertia_})
    search = pd.DataFrame(search)
    search.to_csv(RESULTS / "cluster_k_search.csv", index=False)
    k = int(search.loc[search["silhouette"].idxmax(), "k"])
    km = KMeans(k, n_init=50, random_state=0).fit(shape)
    # order clusters by daily energy so cluster 0 is always the heaviest mode
    energy = prof.sum(axis=1)
    order = energy.groupby(km.labels_).mean().sort_values(ascending=False).index
    labels = pd.Series(pd.Series(range(k), index=order).loc[km.labels_].to_numpy(), index=prof.index, name="cluster")

    # after-hours energy per day (kWh = mean kW over minutes / 60 * minutes)
    t = df.index
    after = ~((t.day_of_week < 5) & (t.hour >= WORK_START) & (t.hour < WORK_END))
    day = pd.Index(t.date, name="date")
    kwh = lambda s: s.groupby(day).sum() / 60  # 1-min kW samples -> kWh
    per_day = pd.DataFrame({
        "building_kwh": kwh(df["agg_p_kw"]),
        "ac_kwh_measured": kwh(df["ac_kw"]).where(df["ac_kw"].notna().groupby(day).any()),
        "ac_after_kwh_measured": kwh(df["ac_kw"].where(after)).where(df["ac_kw"].notna().groupby(day).any()),
        "ac_after_kwh_estimated": kwh(df["ac_pred_kw"].where(after)).where(df["ac_pred_kw"].notna().groupby(day).any()),
        "light_kwh": kwh(df["light_kw"]),
        "light_after_kwh": kwh(df["light_kw"].where(after)),
    }).loc[prof.index].join(labels)
    per_day["weekday"] = pd.to_datetime(per_day.index).day_name()
    per_day.round(2).to_csv(RESULTS / "cluster_days.csv")
    summary = per_day.groupby("cluster").agg(
        days=("building_kwh", "size"),
        weekdays=("weekday", lambda s: int((~s.isin(["Saturday", "Sunday"])).sum())),
        building_kwh_day=("building_kwh", "mean"),
        ac_kwh_day_measured=("ac_kwh_measured", "mean"),
        ac_after_kwh_day_measured=("ac_after_kwh_measured", "mean"),
        ac_after_kwh_day_estimated=("ac_after_kwh_estimated", "mean"),
        light_kwh_day=("light_kwh", "mean"),
        light_after_kwh_day=("light_after_kwh", "mean"),
    ).round(2)
    summary.to_csv(RESULTS / "cluster_summary.csv")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), gridspec_kw={"width_ratios": [1.3, 1]})
    for c in range(k):
        days = labels[labels == c].index
        axes[0].plot(prof.columns, prof.loc[days].mean(), color=COLORS[c], lw=2.2,
                     label=f"Mode {c} ({len(days)} days, {summary.loc[c, 'weekdays']} weekdays)")
        for d in days:
            axes[0].plot(prof.columns, prof.loc[d], color=COLORS[c], lw=0.5, alpha=0.25)
    axes[0].axvspan(WORK_START, WORK_END, color=INK2, alpha=0.06, lw=0)
    axes[0].set_xticks(range(0, 24, 3)); axes[0].set_xlabel("Hour of day"); axes[0].set_ylabel("Building kW (hourly)")
    axes[0].legend(fontsize=8.5, loc="upper left"); axes[0].set_title(f"Daily operating modes (k-means, k={k})")
    dates = pd.to_datetime(labels.index)
    axes[1].scatter(dates, [0] * len(dates), c=[COLORS[c] for c in labels], s=110, marker="s")
    for d, c in zip(dates, labels):
        axes[1].text(d, 0.12, d.strftime("%a"), rotation=90, ha="center", fontsize=6.5, color=INK2)
    axes[1].set_yticks([]); axes[1].set_ylim(-0.3, 0.6); axes[1].grid(False)
    axes[1].xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    axes[1].tick_params(axis="x", labelsize=8); axes[1].set_title("Mode of each day (ticks = Mondays)")
    fig.savefig(FIG / "cluster_profiles.png"); plt.close(fig)

    print(search.round(3).to_string(index=False), f"\nchosen k = {k}\n")
    print(summary.to_string())
    print("\n", per_day[["cluster", "weekday"]].T.to_string())
    assert labels.size == len(prof) and summary["days"].sum() == len(prof)


if __name__ == "__main__":
    main()
