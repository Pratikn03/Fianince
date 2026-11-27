"""Checks p1ks_power on synthetic calibration summaries (not the real calibration)."""
import p1ks_power as PW


def fake_group(sd_c, rho, sd_ds, mean=0.0):
    q = {'mean': mean, 'sd': sd_c, 'q05': mean - 1.645 * sd_c, 'q25': mean - 0.674 * sd_c, 'median': mean,
         'q75': mean + 0.674 * sd_c, 'q95': mean + 1.645 * sd_c}
    v_half = sd_c ** 2            # pretend half-window estimates have the full-window spread
    sd_dc = (2 * v_half * (1 - rho)) ** 0.5
    return {'c_full': q, 'corr_c_h1_h2': rho, 'dc_placebo': {'sd': sd_dc}, 'dS_placebo': {'sd': sd_ds},
            'days_h1': {'median': 615}, 'days_h2': {'median': 615}}


def test_size_and_power_extremes():
    PW.REPS = 300
    strong = {'large': fake_group(0.05, 0.9, 0.01), 'other': fake_group(0.05, 0.9, 0.01)}
    r = PW.run(strong)['rates']
    assert 0.01 <= r['0.0'] <= 0.10 and r['1.0'] > 0.95, r
    weak = {'large': fake_group(0.001, 0.1, 0.05), 'other': fake_group(0.001, 0.1, 0.05)}
    r = PW.run(weak)['rates']
    assert r['1.0'] < 0.3, r


if __name__ == '__main__':
    test_size_and_power_extremes()
    print('p1ks_power tests passed')
