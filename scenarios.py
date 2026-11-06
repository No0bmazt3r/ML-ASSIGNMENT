"""UTP scenario analysis from the model's out-of-sample estimates (proposal Section 5.2, Objective 6).

Uses only main-meter-derived A/C estimates (weeks 2, 3 and 6: never the training weeks), because that
is all UTP would have in practice. Week 6 also has the sub-meter, so each headline is checked against it.
Every figure is a labelled SCENARIO for one CLEMD-sized building, not a UTP measurement.
Writes results/scenarios.json and figures/results/scenario_*.png.
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from evaluate import AC, FIG, INK2, LIGHT
from features import RESULTS, ROOT

# --- scenario assumptions (all stated in the report) -----------------------------
RM_PER_KW_MONTH = (89.27, 97.06)  # TNB MV demand charge (capacity + network), standard / ToU, refs [7, 8]
GEF_T_PER_MWH = 0.740             # Peninsular grid emission factor 2024 (provisional), ref [18]
UTP_SCOPE2_T = 20_270             # UTP purchased-electricity emissions, 20.27 million kgCO2e/yr, ref [17]
PV_MWP, PR_RANGE = 7.4, (0.75, 0.78, 0.80)  # UTP rooftop PV, assumed performance ratios
TRIMS = (0.10, 0.20, 0.30)        # A/C trim during peak windows (modest for comfort, Section 5.5)
PRECOOL_SHIFT = 0.20              # share of 14:00-16:00 A/C energy moved earlier
PRECOOL_WINDOWS = [(8, 10), (9, 11), (10, 12), (11, 13)]  # proposal assumed 11-13 (solar peak)
AFTER_CUT = {"ac": 0.50, "light": 0.30}  # after-hours reduction scenarios
OFFICE_HOURS = [(8, 17), (8, 18), (7, 19)]  # sensitivity of the after-hours definition
PV_COLOR = "#1baf7a"


def shave(agg, ac, trim, thr):
    """Max demand after trimming A/C by `trim` whenever demand >= thr (a demand-limiting controller)."""
    return (agg - trim * ac * (agg >= thr)).max()


def precool(q, ac_col, shift, window=(11, 13)):
    """Move `shift` of weekday 14-16h A/C energy into `window` (energy neutral). Returns new building series."""
    new = q["agg_p_kw"].copy()
    wd = q.index.day_of_week < 5
    for d in np.unique(q.index[wd].date):
        day = q.index.date == d
        late = day & (q.index.hour >= 14) & (q.index.hour < 16)
        early = day & (q.index.hour >= window[0]) & (q.index.hour < window[1])
        if late.any() and early.any():
            moved = shift * q.loc[late, ac_col]
            new[late] -= moved
            new[early] += moved.sum() / early.sum()
    return new


def pv_profile():
    path = ROOT / "data" / "external" / "nasa_power_utp_oct2023_utc.csv"
    lines = path.read_text().splitlines()
    nasa = pd.read_csv(path, skiprows=lines.index("-END HEADER-") + 1)
    nasa.index = pd.to_datetime(nasa[["YEAR", "MO", "DY", "HR"]].astype(int).set_axis(
        ["year", "month", "day", "hour"], axis=1)) + pd.Timedelta(hours=8)  # UTC -> MYT
    ghi = nasa["ALLSKY_SFC_SW_DWN"].loc["2023-10-04":"2023-10-24"]
    return ghi.groupby(ghi.index.hour).mean()  # mean W/m2 by hour of day


def main():
    p = pd.read_csv(RESULTS / "predictions.csv", index_col=0, parse_dates=True)
    est = p[p["ac_pred_kw"].notna()]
    q = est[["agg_p_kw", "ac_pred_kw", "ac_kw", "light_kw", "light_pred_kw", "week"]].resample("15min").mean()
    q = q.dropna(subset=["agg_p_kw", "ac_pred_kw"])
    w6 = q[q["week"] == 6]
    out = {"basis": "frozen-model A/C estimates on unseen weeks 2, 3, 6 "
                    f"({q.index.normalize().nunique()} days); week 6 checked against the sub-meter"}

    # 1. peak drivers: who supplies the top-5% windows (week 6: estimate vs measured)
    pk = w6[w6["agg_p_kw"] >= w6["agg_p_kw"].quantile(0.95)]
    tot = pk["agg_p_kw"].sum()
    out["peak_drivers_week6_pct"] = {
        "n_windows": len(pk), "threshold_kw": round(w6["agg_p_kw"].quantile(0.95), 1),
        "ac_estimated": round(100 * pk["ac_pred_kw"].sum() / tot, 1),
        "ac_measured": round(100 * pk["ac_kw"].sum() / tot, 1),
        "light_estimated": round(100 * pk["light_pred_kw"].sum() / tot, 1),
        "light_measured": round(100 * pk["light_kw"].sum() / tot, 1),
        "office_hours_share_pct": round(100 * np.mean((pk.index.day_of_week < 5) & (pk.index.hour >= 8)
                                                      & (pk.index.hour < 17)), 1),
    }

    # 2. peak shaving: trim A/C when demand >= the top-5% threshold, then RECOMPUTE the max
    thr = q["agg_p_kw"].quantile(0.95)
    base_max = q["agg_p_kw"].max()
    shaving = []
    for trim in TRIMS:
        cut = base_max - shave(q["agg_p_kw"], q["ac_pred_kw"], trim, thr)
        cut_w6_est = w6["agg_p_kw"].max() - shave(w6["agg_p_kw"], w6["ac_pred_kw"], trim, thr)
        cut_w6_meas = w6["agg_p_kw"].max() - shave(w6["agg_p_kw"], w6["ac_kw"], trim, thr)
        naive = trim * q.loc[q["agg_p_kw"].idxmax(), "ac_pred_kw"]  # proposal's upper bound
        shaving.append({"trim_pct": int(trim * 100), "max_demand_cut_kw": round(cut, 2),
                        "naive_upper_bound_kw": round(naive, 2),
                        "week6_cut_kw_estimated": round(cut_w6_est, 2), "week6_cut_kw_measured": round(cut_w6_meas, 2),
                        "rm_per_month": [round(cut * r) for r in RM_PER_KW_MONTH],
                        "rm_per_year": [round(12 * cut * r) for r in RM_PER_KW_MONTH]})
    out["peak_shaving"] = {"base_max_15min_kw": round(base_max, 1), "trigger_kw": round(thr, 1), "scenarios": shaving}

    # 3. solar timing + pre-cooling
    ghi = pv_profile()
    pv_hours = ghi[ghi > 0.1 * ghi.max()].index
    ac_h = q["ac_pred_kw"].groupby(q.index.hour).sum()
    wd = q.index.day_of_week < 5
    daily_max_old = q.loc[wd, "agg_p_kw"].groupby(q.index[wd].date).max()
    windows = []
    for win in PRECOOL_WINDOWS:
        new = precool(q, "ac_pred_kw", PRECOOL_SHIFT, win)
        daily_max_new = new[wd].groupby(q.index[wd].date).max()
        cut = q["agg_p_kw"].max() - new.max()
        windows.append({"window": f"{win[0]:02d}-{win[1]:02d}", "max_demand_cut_kw": round(cut, 2),
                        "week6_max_cut_kw_measured_ac": round(w6["agg_p_kw"].max() - precool(w6, "ac_kw", PRECOOL_SHIFT, win).max(), 2),
                        "mean_weekday_peak_cut_kw": round((daily_max_old - daily_max_new).mean(), 2),
                        "weekday_peaks_lowered_pct": round(100 * (daily_max_new < daily_max_old - 0.01).mean(), 1),
                        "pv_irradiance_vs_peak_pct": round(100 * ghi.loc[win[0]:win[1] - 1].mean() / ghi.max(), 1),
                        "rm_per_month": [round(cut * r) for r in RM_PER_KW_MONTH]})
    best = max(windows, key=lambda w: w["max_demand_cut_kw"])
    new = precool(q, "ac_pred_kw", PRECOOL_SHIFT, tuple(int(h) for h in best["window"].split("-")))
    out["solar_and_precooling"] = {
        "pv_hours": f"{pv_hours.min():02d}:00-{pv_hours.max() + 1:02d}:00",
        "ac_energy_in_pv_hours_pct_estimated": round(100 * ac_h[ac_h.index.isin(pv_hours)].sum() / ac_h.sum(), 1),
        "pv_output_14_16_vs_11_13_pct": round(100 * ghi.loc[14:15].mean() / ghi.loc[11:12].mean(), 1),
        "utp_pv_peak_mw_by_pr": {pr: round(PV_MWP * ghi.max() / 1000 * pr, 2) for pr in PR_RANGE},
        "precool_shift_pct": int(PRECOOL_SHIFT * 100),
        "windows": windows,
        "best_window": best["window"],
    }

    # 4. after-hours energy -> kWh, tCO2e (sensitivity to the office-hours definition)
    after = []
    days = est.index.normalize().nunique()
    for start, end in OFFICE_HOURS:
        t = est.index
        off = ~((t.day_of_week < 5) & (t.hour >= start) & (t.hour < end))
        ac_kwh_day = est.loc[off, "ac_pred_kw"].sum() / 60 / days
        light_kwh_day = est.loc[off, "light_kw"].sum() / 60 / days
        w = est["week"] == 6
        ac_meas_day = est.loc[off & w, "ac_kw"].sum() / 60 / est[w].index.normalize().nunique()
        ac_est_w6_day = est.loc[off & w, "ac_pred_kw"].sum() / 60 / est[w].index.normalize().nunique()
        saved_kwh_yr = 365 * (AFTER_CUT["ac"] * ac_kwh_day + AFTER_CUT["light"] * light_kwh_day)
        after.append({"office_hours": f"{start:02d}-{end:02d}", "ac_after_kwh_day_estimated": round(ac_kwh_day, 1),
                      "week6_ac_after_kwh_day_estimated": round(ac_est_w6_day, 1),
                      "week6_ac_after_kwh_day_measured": round(ac_meas_day, 1),
                      "light_after_kwh_day": round(light_kwh_day, 1),
                      "saved_kwh_per_year": round(saved_kwh_yr), "saved_tco2e_per_year": round(saved_kwh_yr / 1000 * GEF_T_PER_MWH, 2),
                      "pct_of_utp_scope2": round(100 * saved_kwh_yr / 1000 * GEF_T_PER_MWH / UTP_SCOPE2_T, 4)})
    out["after_hours"] = {"cuts": AFTER_CUT, "scenarios": after}
    out["assumptions"] = {"rm_per_kw_month": RM_PER_KW_MONTH, "gef_t_per_mwh": GEF_T_PER_MWH,
                          "utp_scope2_t": UTP_SCOPE2_T, "pv_mwp": PV_MWP, "pr_range": PR_RANGE,
                          "annualised_from": f"{days} days in Sep-Oct 2023 (indicative only)",
                          "label": "SCENARIOS for one CLEMD-sized building, not UTP measurements"}
    (RESULTS / "scenarios.json").write_text(json.dumps(out, indent=2, default=str))

    # --- figures ----------------------------------------------------------------
    d = out["peak_drivers_week6_pct"]
    fig, ax = plt.subplots(figsize=(8, 3))
    for i, (lab, a, l) in enumerate([("Measured (sub-meters)", d["ac_measured"], d["light_measured"]),
                                     ("Estimated (main meter only)", d["ac_estimated"], d["light_estimated"])]):
        ax.barh(i, a, color=AC, height=0.55, label="A/C" if i == 0 else None)
        ax.barh(i, l, left=a, color=LIGHT, height=0.55, label="Lighting & sockets" if i == 0 else None)
        ax.barh(i, 100 - a - l, left=a + l, color="#c3c2b7", height=0.55, label="Other" if i == 0 else None)
        ax.text(a / 2, i, f"{a:.0f}%", ha="center", va="center", color="white", weight="bold")
    ax.set_yticks([0, 1], ["Measured (sub-meters)", "Estimated (main meter only)"]); ax.invert_yaxis()
    ax.set_xlim(0, 100); ax.set_xlabel("% of building load in the top-5% demand windows (test week)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.35), ncol=3); ax.grid(axis="y", visible=False)
    ax.set_title("Who sets the peak? The model recovers the A/C share from the main meter")
    fig.savefig(FIG / "scenario_peak_drivers.png"); plt.close(fig)

    day = q.index[wd][np.argmax(q.loc[wd, "agg_p_kw"].to_numpy())].date()  # the period's peak weekday
    sel = q.index.date == day
    fig, ax = plt.subplots(figsize=(9, 4))
    ax2 = ax.twinx()
    ax2.fill_between(ghi.index, 0, ghi.values, color=PV_COLOR, alpha=0.12, lw=0)
    ax2.set_ylabel("Mean irradiance at UTP (W/m²)", color=PV_COLOR); ax2.set_ylim(0, ghi.max() * 2.2)
    ax2.grid(False); ax2.spines["right"].set_visible(True)
    h = q.index[sel].hour + q.index[sel].minute / 60
    ax.plot(h, q.loc[sel, "agg_p_kw"], color=INK2, lw=2, label="Building, as recorded")
    ax.plot(h, new[sel], color=AC, lw=2, ls="--", label=f"With pre-cooling ({int(PRECOOL_SHIFT*100)}% of 14-16h A/C moved to {best['window']}h)")
    b0, b1 = (int(h) for h in best["window"].split("-"))
    ax.axvspan(b0, b1, color=PV_COLOR, alpha=0.08, lw=0); ax.axvspan(14, 16, color=AC, alpha=0.06, lw=0)
    ax.set_xlim(0, 24); ax.set_xticks(range(0, 25, 2)); ax.set_xlabel("Hour of day")
    ax.set_ylabel("Building demand, 15-min (kW)"); ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title(f"Pre-cooling scenario on the peak weekday ({pd.Timestamp(day):%a %d %b %Y})")
    fig.savefig(FIG / "scenario_precooling.png"); plt.close(fig)

    print(json.dumps(out, indent=2, default=str))
    # self-check: shaving can never raise the peak, and a bigger trim never cuts less
    cuts = [s["max_demand_cut_kw"] for s in shaving]
    assert all(c >= 0 for c in cuts) and cuts == sorted(cuts)


if __name__ == "__main__":
    main()
