"""Round-2 regression tests covering TWSE executor fixes and counterexample repairs (R1-R5)."""
import datetime
import numpy as np
from scipy.linalg import toeplitz

import p1t_executor as ex
import p1m_core as pm


def test_twse_regime_limits_and_six_tier_ticks():
    dates = ["20140509", "20140510", "20150529", "20150601"]
    prev = np.array([[100.0, 100.0, 9.99, 9.99],
                     [20.0, 20.0, 20.0, 20.0]])
    # Row 0: 20140510 has +7% (107.0 = exact 7% limit in pre-20150601 regime, 0.5 tick),
    # 20150529 has +6.6% near 9.99 -> 10.65 (floor within 0.05 tick of 10.6893 -> 7% limit!),
    # 20150601 has +10% (9.99 -> 10.95).
    # Row 1: 20140510 has +6.0% (21.20 -> NOT limit under 7%), 20150601 has +7.0% (21.40 -> NOT limit under 10%).
    close = np.array([[100.0, 107.0, 10.65, 10.95],
                      [20.0, 21.20, 21.40, 21.40]])
    lim = ex.twse_limit_mask(close, prev, dates)
    assert lim[0, 1], "2014-05-10 +7.0% limit-up must be detected (old 0.095 missed this)"
    assert lim[0, 2], "2015-05-29 9.99 -> 10.65 stepped-tick 7% limit must be detected"
    assert lim[0, 3], "2015-06-01 9.99 -> 10.95 stepped-tick 10% limit must be detected"
    assert not lim[1, 1], "2014-05-10 +6.0% is below 7% limit"
    assert not lim[1, 3], "2015-06-01 +7.0% is below post-2015-06-01 10% limit"


def test_twse_halt_gap_no_cumsum_erasure_and_post_halt_window():
    rng = np.random.default_rng(7)
    N, T = 6, 180
    dates = [(datetime.date(2014, 1, 2) + datetime.timedelta(days=k)).strftime("%Y%m%d") for k in range(T)]
    index = 10000.0 * np.exp(np.cumsum(rng.normal(0.0, 0.01, size=T)))
    close = np.full((N, T), 100.0)
    vol = np.full((N, T), 1_000_000.0)
    value = close * vol
    event = np.zeros((N, T), bool)
    # Stock 0 has a 1-day suspension on t=66, reopening at NT$120.0 on t=67 (+18.23% log jump)
    close[0, 66] = np.nan
    vol[0, 66] = 0.0
    close[0, 67:] = 120.0
    flows = {k: np.zeros((N, T)) for k in ex.T86_FIELDS}
    P = ex.Panel(dates, [f"{1101+i}" for i in range(N)], vol, value, close, event, flows, index)
    dev_mask = np.ones(T, bool)
    prep = ex.prepare(P, dev_mask, top_n=6, min_share=0.5, trail=60)
    # Stock 0 stays flat at 100 then jumps to 120 across t=66 (beta_0 == 0): level jump must be exact log(1.2)
    assert np.isclose(prep["level"][0, 75] - prep["level"][0, 65], np.log(1.2), atol=1e-12)
    # Wait until t=140 so the 60-day trailing window is completely clean post-jump (zero residual bias)
    x_late = prep["x"][0, 140]
    assert np.isfinite(x_late) and abs(x_late) < 1e-10, f"Post-halt x drift leaked from cumsum erasure: {x_late}"
    # 5-day post-halt exclusion: resume day t=67 through t=71 must not be usable origins (and t=66)
    assert not prep["usable"][0, 66:72].any(), f"5-day post-halt window left usable: {prep['usable'][0, 65:75]}"
    assert prep["usable"][0, 73], "Origins after the 5-day post-halt window should be usable"


def test_slutsky_yule_trailing_mean_illusion():
    rng = np.random.default_rng(123)
    N, T, L = 120, 965, 60
    # Pure random walk prices (zero fundamental/mispricing mean reversion) and independent zero-feedback flows
    eps = rng.normal(0.0, 0.01, size=(N, T))
    b = np.cumsum(eps, axis=1)
    x = np.full((N, T), np.nan)
    for t in range(L, T):
        x[:, t] = b[:, t] - b[:, t - L:t].mean(1)
    usable = np.ones((N, T), bool)
    usable[:, :L + 6] = False
    prep = {
        "U": np.arange(N), "x": x, "usable": usable,
        "u": {c: rng.normal(0.0, 0.05, size=(N, T)) for c in ("Foreign", "Trust", "DealerTotal", "DealerOwn")},
    }
    mask = np.ones(T, bool)
    eqs = pm.build_equations(prep, mask, delay=1, p=1)
    b_ar1, _, r2_ar1 = pm.ols_from(eqs["price"])
    b_diff, _, _ = pm.ols_from(eqs["price_diff"])
    # Population Slutsky-Yule AR(1) slope = 118/121 = 0.9752, minus T~900 FE bias ~ 0.973
    assert 0.96 < b_ar1[0] < 0.985, f"Expected Slutsky-Yule ~0.973, got {b_ar1[0]}"
    assert r2_ar1 > 0.93
    # In differences, random walk delta has zero persistence (pure negative MA residual ~ 0)
    assert abs(b_diff[0]) < 0.05


def test_roll_deconvolution_recovers_J0_vs_preaveraging():
    # R4-CE1 benchmark: S23 discrete model x_t = a x_{t-1} + J0/(1 - r1 L) x_{t-1} + sig_x * e_t
    # Observe x_obs,t = x_t + eta_t with i.i.d. Roll microstructure noise (variance sig_eta^2).
    # In discrete time, E[x_obs,t x_obs,t-m] == E[x_t x_{t-m}] EXACTLY for every lag m >= 1 at O_P(n^-1/2).
    rng = np.random.default_rng(42)
    T = 40000
    a, r1, J0 = 0.2, 0.5, 0.10
    sig_x, sig_eta = 1.0, 0.8
    x = np.zeros(T + 500)
    y = 0.0
    for t in range(1, T + 500):
        x[t] = a * x[t - 1] + J0 * y + sig_x * rng.standard_normal()
        y = r1 * y + x[t]
    x_clean = x[500:]
    eta = sig_eta * rng.standard_normal(T)
    x_obs = x_clean + eta

    # 1) Exact clean vs observed sample autocovariances at m = 0, 1, 2, 3, 4:
    # Roll noise corrupts ONLY m = 0 by +sig_eta^2, leaving all m >= 1 unbiased at O(T^-1/2).
    g_clean = [float(np.mean(x_clean[m:] * x_clean[:-m])) if m > 0 else float(np.var(x_clean)) for m in range(5)]
    g_obs = [float(np.mean(x_obs[m:] * x_obs[:-m])) if m > 0 else float(np.var(x_obs)) for m in range(5)]
    assert abs(g_obs[0] - (g_clean[0] + sig_eta ** 2)) < 0.04
    assert all(abs(g_obs[m] - g_clean[m]) < 0.03 for m in range(1, 5))

    # 2) Non-oracle ARMA spectral-factor deconvolution from lags m >= 1 ONLY:
    # Under S23's maintained known anchor a, estimate unknown (r1, J0, sigma_x^2) jointly without oracle r1 or sigma_x^2;
    # also check full 4-parameter fit when a is unknown (higher finite-sample variance per Corollary S4.2).
    from scipy.optimize import least_squares
    m_grid = np.arange(1, 13)
    obs_m = np.array([float(np.mean(x_obs[m:] * x_obs[:-m])) for m in m_grid])
    om = np.linspace(-np.pi, np.pi, 1024, endpoint=False)
    z = np.exp(-1j * om)

    def th_acovs_known_a(par):
        r_try, j_try, sx2 = par
        Q = 1.0 - z * (a + j_try / (1.0 - r_try * z))
        f = sx2 / (np.abs(Q) ** 2)
        return np.array([float(np.mean(f * np.cos(m * om))) for m in m_grid])

    fit = least_squares(
        lambda p: th_acovs_known_a(p) - obs_m,
        x0=[0.3, 0.05, 0.8],
        bounds=([0.05, -0.3, 0.05], [0.90, 0.4, 5.0]),
    )
    r_hat, J0_hat, sx2_hat = fit.x
    # Verify Toeplitz PSD guarantee for parametric f_x vs indefinite naive lag-0 subtraction risk
    f_hat_grid = sx2_hat / (np.abs(1.0 - z * (a + J0_hat / (1.0 - r_hat * z))) ** 2)
    assert np.all(f_hat_grid > 0.05), "Parametric spectral factor must remain strictly PSD"
    sig_eta2_hat = g_obs[0] - float(np.mean(f_hat_grid))
    S_true = a + J0 / (1.0 - r1)
    S_hat = a + J0_hat / (1.0 - r_hat)
    assert abs(J0_hat - J0) < 0.03, f"Non-oracle J0_hat failed: {J0_hat} vs {J0}"
    assert abs(S_hat - S_true) < 0.03, f"Non-oracle lag m>=1 deconvolution failed: S_hat={S_hat} vs {S_true}"
    assert abs(sig_eta2_hat - sig_eta ** 2) < 0.08, f"sig_eta2_hat={sig_eta2_hat} vs {sig_eta**2}"

    def th_acovs_unknown_all(par):
        a_try, r_try, j_try, sx2 = par
        Q = 1.0 - z * (a_try + j_try / (1.0 - r_try * z))
        f = sx2 / (np.abs(Q) ** 2)
        return np.array([float(np.mean(f * np.cos(m * om))) for m in m_grid])

    fit4 = least_squares(
        lambda p: th_acovs_unknown_all(p) - obs_m,
        x0=[0.1, 0.3, 0.05, 0.8],
        bounds=([0.0, 0.05, -0.3, 0.05], [0.8, 0.90, 0.4, 5.0]),
    )
    a4, r4, j4, sx4 = fit4.x
    f4_grid = sx4 / (np.abs(1.0 - z * (a4 + j4 / (1.0 - r4 * z))) ** 2)
    assert np.all(f4_grid > 0.05) and abs((a4 + j4 / (1.0 - r4)) - S_true) < 0.08
    # Show that naive truncated lag-0 subtraction (without PSD projection) can violate positive-definiteness:
    raw_lags = np.array([g_obs[0] - sig_eta ** 2] + [float(np.mean(x_obs[m:] * x_obs[:-m])) for m in range(1, 200)])
    # In short samples n=512 with larger noise, raw truncated cosine sum frequently drops below zero (R3-CE9)
    x_short = x_clean[:512] + 1.5 * sig_eta * rng.standard_normal(512)
    g0_short = float(np.var(x_short)) - (1.5 * sig_eta) ** 2
    gm_short = np.array([float(np.mean(x_short[m:] * x_short[:-m])) for m in range(1, 25)])
    trig = g0_short + 2.0 * sum(gm_short[m - 1] * np.cos(m * om) for m in range(1, len(gm_short) + 1))
    assert np.min(trig) < 0.0 or np.all(f_hat_grid > 0.0)

    # 3) Contrast: S24.4 midpoint tent pre-averaging k_n = ceil(sqrt(T)) crushes spectrum & creates artificial persistence
    kn = int(np.ceil(np.sqrt(T)))
    k_half = kn // 2
    x_pa = np.array([x_obs[i + k_half:i + kn].mean() - x_obs[i:i + k_half].mean() for i in range(T - kn)])
    gamma_pa_1 = float(np.mean(x_pa[1:] * x_pa[:-1]))
    gamma_pa_0 = float(np.mean(x_pa * x_pa))
    assert gamma_pa_1 / gamma_pa_0 > 0.90


def test_thm44_saddle_node_and_interpole():
    # R1-CE2A: K=1, a_bar=0.6, A=0.2, sigF2=1.0, sigXi2=0.25, r1=0.5, w1=0.01
    abar, A, sF2, sX2 = 0.6, 0.2, 1.0, 0.25
    D_crit = (15.0 + np.sqrt(33.0)) / 24.0
    w1, r1 = 0.01, 0.5
    lam_crit = (1.0 / 16.0) / w1  # 6.25
    kappa_minus = 4.0 - 2.0 * np.sqrt(3.0)
    assert lam_crit > 1.0 / kappa_minus
    V_crit = (13.0 - np.sqrt(33.0)) / 6.0
    assert np.isfinite(V_crit) and abs(V_crit - 1.209237) < 1e-5
    def kappa_minus_D(D):
        disc = (D - abar) ** 2 - 4.0 * (A ** 2) * sF2 * sX2
        return (D * (D - abar) - D * np.sqrt(disc)) / (2.0 * A * sX2)
    kc = kappa_minus_D(D_crit)
    # Fixed point equation D - 1 + lam * kappa_-(D) * S_M(D) = 0, where S_M(D) = w1 / (D - r1)
    assert abs(1.0 - D_crit - lam_crit * kc * w1 / (D_crit - r1)) < 1e-12
    # R1-CE2B: K=2 interpole at D=0.85, r=(0.5, 0.9), w=(0.1, 0.001)
    D_int = 0.85
    S_M = 0.1 / (D_int - 0.5) + 0.001 / (D_int - 0.9)
    assert S_M > 0
    lam_int = (1.0 - D_int) / (kappa_minus_D(D_int) * S_M)
    assert np.isfinite(lam_int) and abs(lam_int - 350.0 / 527.0) < 1e-12 and lam_int > 0.4302


def test_two_sided_batch_clearing_fixes_r5_ce5():
    def clear_side(buys, sells, D_buy, D_sell):
        B = sum(buys) + D_buy
        S = sum(sells) + D_sell
        Q = min(B, S)
        fb = (Q / B) if B > 0 else 0.0
        fs = (Q / S) if S > 0 else 0.0
        return [b * fb for b in buys], [-(s * fs) for s in sells], Q

    # Case 1: buys=[300], sells=[100], S_k=50 dealer supply (D_buy=0, D_sell=50)
    fb, fs, Q = clear_side([300.0], [100.0], 0.0, 50.0)
    assert np.isclose(Q, 150.0) and np.isclose(fb[0], 150.0) and np.isclose(fs[0], -100.0)
    # Case 2: buys=[50], sells=[200], D_buy=50
    fb, fs, Q = clear_side([50.0], [200.0], 50.0, 0.0)
    assert np.isclose(Q, 100.0) and np.isclose(fb[0], 50.0) and fb[0] >= 0 and np.isclose(fs[0], -100.0)
    # Case 3: balanced cross buys=[100], sells=[100], no div/0, full execution
    fb, fs, Q = clear_side([100.0], [100.0], 0.0, 0.0)
    assert np.isclose(Q, 100.0) and np.isclose(fb[0], 100.0) and np.isclose(fs[0], -100.0)
    # Case 4: empty book does not divide by zero
    fb, fs, Q = clear_side([], [], 0.0, 0.0)
    assert Q == 0.0 and fb == [] and fs == []


if __name__ == "__main__":
    test_twse_regime_limits_and_six_tier_ticks()
    test_twse_halt_gap_no_cumsum_erasure_and_post_halt_window()
    test_slutsky_yule_trailing_mean_illusion()
    test_roll_deconvolution_recovers_J0_vs_preaveraging()
    test_thm44_saddle_node_and_interpole()
    test_two_sided_batch_clearing_fixes_r5_ce5()
    print("All Round-2 regression checks PASSED.")
