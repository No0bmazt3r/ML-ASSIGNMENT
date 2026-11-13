import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from evaluate import AC, FIG, INK2, TRAIN_WEEKS, frozen, full_table
from features import RESULTS, TEST_WEEK, build, load

N_REPEATS = 5


# step 5: explain the frozen A/C model with SHAP and grouped permutation importance
def main():
    X, df = full_table()
    _, groups = build(load().head(100))
    group = pd.Series(groups)
    train = df["week"].isin(TRAIN_WEEKS["ac"]) & df["ac_kw"].notna()
    test = df["week"] == TEST_WEEK
    model = frozen("ac").fit(X[train], df.loc[train, "ac_kw"])
    Xt, yt = X[test], df.loc[test, "ac_kw"]

    # SHAP value of every feature for every test minute, then averaged by feature and by group
    sv = pd.DataFrame(shap.TreeExplainer(model).shap_values(Xt), index=Xt.index, columns=Xt.columns)
    glob = sv.abs().mean().sort_values(ascending=False).rename("mean_abs_shap_kw")
    glob.to_frame().assign(group=group).to_csv(RESULTS / "shap_global_ac.csv")
    by_group = sv.T.groupby(group).sum().T.abs().mean().sort_values(ascending=False).rename("mean_abs_shap_kw")
    by_group.to_csv(RESULTS / "shap_groups_ac.csv")

    # local explanation for the highest 15-minute window of the test week
    q = df.loc[test, "agg_p_kw"].resample("15min").mean()
    t0 = q.idxmax()
    win = sv.loc[t0:t0 + pd.Timedelta("14min")].mean().sort_values(key=abs, ascending=False)
    local = win.head(10).rename("shap_kw").to_frame()
    local["feature_value"] = Xt.loc[t0:t0 + pd.Timedelta("14min"), local.index].mean()
    local.to_csv(RESULTS / "shap_local_peak_ac.csv")
    base = float(np.mean(model.predict(X[train])))
    pred_win = model.predict(Xt.loc[t0:t0 + pd.Timedelta("14min")]).mean()
    meas_win = yt.loc[t0:t0 + pd.Timedelta("14min")].mean()

    # permutation importance: shuffle one whole feature group and see how much the error goes up
    rng = np.random.default_rng(0)
    mae0 = np.abs(model.predict(Xt) - yt).mean()
    perm = {}
    for g, cols in group.groupby(group).groups.items():
        rises = []
        for _ in range(N_REPEATS):
            Xp = Xt.copy()
            Xp[list(cols)] = Xp[list(cols)].to_numpy()[rng.permutation(len(Xp))]
            rises.append(np.abs(model.predict(Xp) - yt).mean() - mae0)
        perm[g] = {"mae_increase_kw": np.mean(rises), "std": np.std(rises), "n_features": len(cols)}
    perm = pd.DataFrame(perm).T.sort_values("mae_increase_kw", ascending=False)
    perm.to_csv(RESULTS / "permutation_importance_groups.csv")

    # ridge coefficients for the lighting model
    trl = df["week"].isin(TRAIN_WEEKS["light"])
    ridge = frozen("light").fit(X[trl], df.loc[trl, "light_kw"])
    coef = pd.Series(ridge[-1].coef_, index=X.columns).sort_values(key=abs, ascending=False)
    coef.rename("coef_kw_per_sd").to_frame().assign(group=group).to_csv(RESULTS / "ridge_light_coefficients.csv")

    # figures: top 15 features, beeswarm, groups and the peak window
    top = glob.head(15)[::-1]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(top.index, top.values, color=AC, height=0.6)
    ax.set_xlabel("Mean |SHAP| (kW of A/C estimate)"); ax.grid(axis="y", visible=False)
    ax.set_title("What the A/C model relies on (test week, top 15 features)")
    fig.savefig(FIG / "shap_global_top15.png"); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    axes[0].barh(by_group.index[::-1], by_group.values[::-1], color=AC, height=0.6)
    axes[0].set_xlabel("Mean |SHAP| summed within group (kW)"); axes[0].set_title("SHAP by feature group")
    axes[1].barh(perm.index[::-1], perm["mae_increase_kw"][::-1], xerr=perm["std"][::-1], color=INK2, height=0.6)
    axes[1].set_xlabel("MAE increase when group is shuffled (kW)"); axes[1].set_title("Permutation importance")
    for a in axes:
        a.grid(axis="y", visible=False)
    fig.savefig(FIG / "importance_by_group.png"); plt.close(fig)

    fig = plt.figure(figsize=(8, 5))
    shap.summary_plot(sv[glob.head(12).index].to_numpy(), Xt[glob.head(12).index], show=False, plot_size=None)
    plt.title("SHAP values per minute, top 12 features (test week)", loc="left", fontweight="bold")
    plt.savefig(FIG / "shap_beeswarm.png"); plt.close("all")

    fig, ax = plt.subplots(figsize=(8, 4))
    loc = local["shap_kw"][::-1]
    ax.barh(loc.index, loc.values, color=[AC if v > 0 else INK2 for v in loc.values], height=0.6)
    ax.axvline(0, color=INK2, lw=1); ax.grid(axis="y", visible=False)
    ax.set_xlabel("Contribution to the A/C estimate (kW)")
    ax.set_title(f"Why the model estimates {pred_win:.1f} kW A/C at the week's peak\n"
                 f"({t0:%a %d %b %H:%M}, building {q.max():.1f} kW, measured A/C {meas_win:.1f} kW, "
                 f"baseline {base:.1f} kW)", fontsize=10)
    fig.savefig(FIG / "shap_local_peak.png"); plt.close(fig)

    print("SHAP top 10:\n", glob.head(10).round(3).to_string())
    print("\nSHAP by group:\n", by_group.round(3).to_string())
    print("\npermutation importance by group:\n", perm.round(3).to_string())
    print(f"\npeak window {t0}: building {q.max():.1f} kW, A/C measured {meas_win:.1f}, estimated {pred_win:.1f}")
    print(local.round(3).to_string())
    print("\nlighting Ridge top coefficients:\n", coef.head(10).round(3).to_string())
    ev = shap.TreeExplainer(model).expected_value
    assert np.allclose(ev + sv.iloc[:50].sum(axis=1), model.predict(Xt.iloc[:50]), atol=1e-3)


if __name__ == "__main__":
    main()
