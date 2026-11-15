"""Analytic response derivatives and QR nuisance projection, without Gram inversion.
This is a finite-design check, not a proof of a global inverse inequality.
"""
from pathlib import Path
import json
import mpmath as mp
import numpy as np

HERE = Path(__file__).resolve().parent
CENTRE = {'power': '2.5', 'hump': '.5', 'window': '8'}
SCALE = {'power': '1', 'hump': '.2', 'window': '3'}

def pair(k):
    if k == 2:
        g = [-1/mp.sqrt(3), 1/mp.sqrt(3)]
        r = [mp.mpf(-1), mp.mpf(1)/3]
    else:
        g = [-mp.sqrt(mp.mpf(3)/5), mp.mpf(0), mp.sqrt(mp.mpf(3)/5)]
        r = [mp.mpf(-1), (1-mp.sqrt(6))/5, (1+mp.sqrt(6))/5]
    def weights(nodes):
        v = mp.matrix([[x**j for x in nodes] for j in range(k)])
        return list(mp.lu_solve(v, mp.matrix([mp.mpf(1)/(j+1) if j%2 == 0 else 0 for j in range(k)])))
    return g, weights(g), r, weights(r)

def tap(fam, theta, j):
    if fam == 'power':
        v = (j+1)**(-theta)
        return v, -mp.log(j+1)*v
    if fam == 'hump':
        v = (j+1)*theta**j*(1-theta)**2
        return v, v*(j/theta-2/(1-theta))
    s = 1/(1+mp.exp((j-theta)/mp.mpf('1.5')))
    return s/theta, s*(1-s)/(mp.mpf('1.5')*theta)-s/theta**2

def information(fam, k, delta, digits, horizon=96):
    with mp.workdps(digits):
        nodes, weights, _, _ = pair(k)
        theta = [mp.mpf(CENTRE[fam])+mp.mpf(SCALE[fam])*mp.mpf(delta)*x for x in nodes]
        weights = [mp.mpf('.2')*w for w in weights]
        vals = [[tap(fam, th, j) for j in range(horizon)] for th in theta]
        kernel = [sum(weights[i]*vals[i][j][0] for i in range(k)) for j in range(horizon)]
        dk = [[vals[i][j][0] for j in range(horizon)] for i in range(k)]
        dk += [[weights[i]*vals[i][j][1] for j in range(horizon)] for i in range(k)]
        h = [mp.mpf('.5')]+[mp.mpf(0)]*(horizon-1)
        jac = [[mp.mpf(0)]*horizon for _ in range(2*k)]
        for t in range(1, horizon):
            h[t] = mp.mpf('.3')*h[t-1]+mp.mpf('.5')*sum(kernel[j]*h[t-1-j] for j in range(t))
            for c in range(2*k):
                jac[c][t] = mp.mpf('.3')*jac[c][t-1]+mp.mpf('.5')*sum(
                    dk[c][j]*h[t-1-j]+kernel[j]*jac[c][t-1-j] for j in range(t))
        # h_0 is parameter-independent; remove its identically zero derivative row.
        target = mp.matrix(jac[0][1:])
        nuisance = mp.matrix([[jac[c][t] for c in range(1, 2*k)] for t in range(1, horizon)])
        coef, _ = mp.qr_solve(nuisance, target)
        residual = target-nuisance*coef
        info = mp.fdot(residual, residual)
        assert info > 0
        return mp.nstr(info, 45)

def main():
    out = {'design': '96 response observations, unit independent Gaussian measurement variance',
           'quantity': 'efficient information for first weight with all other weights and nodes nuisance',
           'rows': []}
    ds = ['.2', '.1', '.05', '.025']
    for fam in CENTRE:
        for k in (2, 3):
            vals = [information(fam, k, d, 60) for d in ds]
            repeat = information(fam, k, ds[-1], 90)
            rel = float(abs(mp.mpf(vals[-1])/mp.mpf(repeat)-1))
            slope = float(np.polyfit(np.log([float(x) for x in ds[-3:]]), np.log([float(x) for x in vals[-3:]]), 1)[0])
            row = dict(family=fam, K=k, deltas=ds, information=vals,
                       slope=slope, expected=4*k-2, precision_relative_difference=rel,
                       passed=bool(abs(slope-(4*k-2)) < .15 and rel < 1e-12))
            out['rows'].append(row)
            print(row, flush=True)
    out['passed'] = all(x['passed'] for x in out['rows'])
    (HERE/'high_precision_information_results.json').write_text(json.dumps(out, indent=2, allow_nan=False)+'\n')
    assert out['passed']

if __name__ == '__main__':
    main()
