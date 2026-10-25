"""Test B3: does diversity of AI models protect a market? One shared language-model product against three different ones.

The Bank for International Settlements' concern (Chapter "AI agents in the loop") is that institutions using similar
models act at the same time. B3 asks it directly in Test B1's market (ailoop_sim.py, b1_ailoop.py, llm_ailoop.py, all
imported unchanged). The independent desks are held at their starting stance; the only adaptive agents are AI trading
products that adopting desks follow. Each product is a language model that reads the daily report of llm_ailoop (prompt
v2, temperature 0) and sets one stance from -5 to 5 for every desk that uses it; each starts as Test B1's momentum product
(stance +5, memory 0.9 per bar). Adoption ramps from none to 80% of the 50 desks between days 24 and 96, as in Test B1.

Models (fixed by rule inside the registered run): candidates in this order, Qwen/Qwen2.5-14B-Instruct, microsoft/phi-4,
allenai/OLMo-2-1124-13B-Instruct, Qwen/Qwen3-14B, mistralai/Mistral-Nemo-Instruct-2407, each loaded with 4-bit weights
and screened with Test B2's rule (probe of llm_ailoop, prompt v2, temperature 0.7, 6 samples: at least 95% readable and a
right-way share of at least 0.6 in each of the six reports); the first three that pass, at most one per family (Qwen,
Phi, OLMo, Mistral), are used. Fewer than three passing: B3 is void.

Markets: seeds 3001-3030, for each seed
  control   nobody adopts;
  mono_j    (j = 1, 2, 3) one product run by model j, used by every adopter;
  diverse   three products, one per model; adopters are assigned to them in turn in order of adoption.
Daily decision shock: dF_d = sum over products v of (users of v at the end of day d-1) * (theta_v(d) - theta_v(d-1)), the
change in total feedback caused by the products' decisions with users held fixed; S = variance of dF over days 25-119.

Primaries (Holm across P1-P2 at 0.05; P3 pass/fail):
  P1  diversity decorrelates decisions: S(diverse) < mean of S(mono_1..3) on the same seed, exact one-sided sign test
      over seeds (ties dropped) p < 0.05, and the median ratio S(diverse)/mean S(mono) at most 0.5 (if the three products
      decided on the same days by the same amounts the ratio would be 1; if two of three did, about 0.56);
  P2  diversity keeps the market further from the boundary: the lowest daily true margin of the diverse market exceeds
      the mean of the three mono markets' lowest margins on the same seed, exact one-sided sign test p < 0.05;
  P3  the public-data certificate stays specific: the standard estimator's time-to-zero rule fires in at most 3 of the
      30 control markets.
Validity: more than 5% unreadable replies, or fewer than three screened models, makes every primary fail.
Secondary: share of days on which two products of a diverse market change stance on the same day; correlation of the
three products' stance paths; first day each model leaves +5 and its final stance, in mono and diverse markets; crises
and warning leads by arm; false alarms of every rule in the controls.
"""
import argparse
import hashlib
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import llm_ailoop as L  # noqa: E402

A, B = L.A, L.B
THESIS = HERE.parent
ROOT = THESIS.parent
SPEC = THESIS / "checks/prereg/B3_diversity.json"
COUNTER = THESIS / "checks/prereg/B3_unlock.json"
RESULT = HERE / "B3_results.json"
NUMBERS = THESIS / "checks/B3_numbers.tex"
CANDIDATES = [("Qwen/Qwen2.5-14B-Instruct", "qwen"), ("microsoft/phi-4", "phi"), ("allenai/OLMo-2-1124-13B-Instruct", "olmo"),
              ("Qwen/Qwen3-14B", "qwen"), ("mistralai/Mistral-Nemo-Instruct-2407", "mistral")]
N_MODELS, SEEDS, DAYS, ALPHA = 3, range(3001, 3031), 120, 0.05
PIPELINE = (("b3_sha256", "b3_diversity.py"), ("llm_sha256", "llm_ailoop.py"), ("sim_sha256", "ailoop_sim.py"),
            ("b1_sha256", "b1_ailoop.py"))


# --------------------------------------------------------------------------------------------------------------- backends
class Backend4(L.HFBackend):
    """llm_ailoop's transformers backend with 4-bit weights; if a model's chat template has no system role, the system
    text is put in front of the user text."""

    def __init__(self, model, batch_size=64):
        super().__init__(model, batch_size=batch_size, dtype="auto", quant4=True)
        self.name_or_path = model

    def _text(self, q):
        try:
            return super()._text(q)
        except Exception:
            msgs = [{"role": "user", "content": q["system"] + "\n\n" + q["user"]}]
            return self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


class MultiBackend:
    """Dispatches each request to the backend of its model (q["model"])."""
    name = "multi"

    def __init__(self, backends):
        self.backends = backends

    def decide(self, reqs):
        out = [None] * len(reqs)
        for m, be in self.backends.items():
            idx = [i for i, q in enumerate(reqs) if q["model"] == m]
            if idx:
                for i, t in zip(idx, be.decide([reqs[i] for i in idx])):
                    out[i] = t
        return out


def screen(load, log=print, drop=None):
    """The registered model rule: candidates in order, first three passing B2's screen, one per family.
    `load(model)` returns a backend; passing backends stay loaded and are returned; `drop(model, backend)` frees a
    failing model (GPU memory and disk cache)."""
    chosen, results, families = {}, [], set()
    for m, fam in CANDIDATES:
        if len(chosen) == N_MODELS:
            break
        if fam in families:
            results.append({"model": m, "skipped": "family already chosen"}); continue
        be = load(m)
        pr = L.probe(be, temperature=0.7, variant="v2", samples=6)
        results.append({"model": m, "family": fam, **{k: pr[k] for k in ("parse_rate", "min_right_way", "passes", "summary")}})
        log(f"{m}: passes={pr['passes']} parse={pr['parse_rate']:.2f} worst={pr['min_right_way']:.2f}")
        if pr["passes"]:
            chosen[m] = be; families.add(fam)
        elif drop is not None:
            drop(m, be)
    return chosen, results


# ------------------------------------------------------------------------------------------------------------- simulation
@dataclass
class DMarket:
    scenario: str
    seed: int
    models: tuple = ()          # products' models; () for the control
    s_max: float = 0.8
    r_D: float = 0.9
    vendor: str = "llm"


def make_markets(models, seeds):
    out = []
    for sd in seeds:
        out.append(DMarket("control", sd, (), s_max=0.0))
        for j, m in enumerate(models):
            out.append(DMarket(f"mono_{j + 1}", sd, (m,)))
        out.append(DMarket("diverse", sd, tuple(models)))
    return out


class DivSim(L.Sim):
    """Test B1's market with frozen desks and V language-model products per market (V = 1 or 3)."""

    def __init__(self, cfg, markets):
        super().__init__(cfg, markets)
        K, N, D = self.K, self.N, cfg.days
        self.V = max(1, max(len(m.models) for m in markets))
        self.vend = np.zeros((K, N), dtype=np.int64)          # product used by each desk once it adopts
        for j, m in enumerate(markets):
            if len(m.models) > 1:
                order = np.argsort(self.t_adopt[j])          # adopters in order of adoption, then non-adopters
                self.vend[j, order] = np.arange(N) % len(m.models)
        self.kDv = np.full((K, self.V), cfg.kD0, dtype=np.int64)
        self.kDv_hist = np.zeros((K, self.V, D), dtype=np.int8)
        self.vpnl = np.zeros((K, self.V, D))
        self.users_hist = np.zeros((K, self.V, D), dtype=np.int64)

    def theta_v(self):
        return self.kDv * self.cfg.theta_D / L.KMAX                                  # (K, V)

    def step_day(self):
        cfg, d, K = self.cfg, self.day, self.K
        noise = np.stack([g.normal(size=(L.BARS, 2)) for g in self.rngs])
        th_ind = self.k * cfg.theta_unit
        thv = self.theta_v()
        th_ad = np.take_along_axis(thv, self.vend, 1)                                 # (K, N) theta if adopted
        self.k_hist[:, :, d] = self.k; self.kDv_hist[:, :, d] = self.kDv
        vp = np.zeros((K, self.V))
        for b in range(L.BARS):
            t = d * L.BARS + b
            adopted = t >= self.t_adopt
            theta = np.where(adopted, th_ad, th_ind)
            if self.theta_at_ramp is None and t >= self.t0:
                self.theta_at_ramp = theta.mean(1).copy()
            sig = np.where(adopted, self.yD[:, None], self.y)
            u = cfg.L * np.tanh(theta * sig / cfg.L)
            self.M_true[:, t] = 1 - cfg.a - cfg.kappa * theta.sum(1); self.share[:, t] = adopted.mean(1)
            ft = u.sum(1) + noise[:, b, 0]
            xt = self.x[:, t]
            xn = cfg.a * xt + cfg.kappa * ft + cfg.s_eps * noise[:, b, 1]
            self.f[:, t + 1] = ft; self.x[:, t + 1] = xn
            dx = xn - xt
            vp += cfg.L * np.tanh(thv * self.yD[:, None] / cfg.L) * dx[:, None]      # one user of each product
            self.y = self.r * self.y + (1 - self.r) * xn[:, None]
            self.yD = self.rD * self.yD + (1 - self.rD) * xn
        tend = (d + 1) * L.BARS
        for v in range(self.V):
            self.users_hist[:, v, d] = ((self.t_adopt <= tend) & (self.vend == v)).sum(1)
        self.vpnl[:, :, d] = vp
        self.day += 1

    def requests(self):
        d, tend, reqs = self.day, self.day * L.BARS, []
        if tend < self.t0:
            return reqs
        lo = max(0, d - 5)
        for j, m in enumerate(self.markets):
            if not m.models:
                continue
            closes, vol, ac = self._market(j)
            for v, model in enumerate(m.models):
                users = int(self.users_hist[j, v, d - 1])
                user = L.user_text("v2", d, closes, vol, ac, self.kDv_hist[j, v, lo:d], self.vpnl[j, v, lo:d], self.kDv[j, v],
                                   header=f"{users} of {self.N} trading desks in this market now use your product.")
                reqs.append({"who": ("product", j, v), "model": model, "system": L.VENDOR_SYSTEM, "user": user,
                             "temperature": 0.0, "seed": (m.seed * 1000003 + d * 1009 + 17 * v) % (2 ** 31),
                             "obs": {"k": int(self.kDv[j, v]), "pnl_last": float(self.vpnl[j, v, d - 1])}})
        return reqs

    def apply(self, reqs, texts):
        for q, t in zip(reqs, texts):
            _, j, v = q["who"]
            k = L.parse_stance(t); self.calls += 1
            if k is None:
                self.parse_fail += 1
                if len(self.raw_examples) < 20:
                    self.raw_examples.append(t)
                continue
            self.kDv[j, v] = k


# ------------------------------------------------------------------------------------------------------------- evaluation
def market_summary(sim, j):
    cfg, m = sim.cfg, sim.markets[j]
    D, nv, ramp = cfg.days, max(1, len(m.models)), int(cfg.ramp_start * cfg.days)
    acfg = A.Config(days=D, window=cfg.window, lags=cfg.lags, boot=cfg.boot, seed=m.seed)
    x, f = sim.x[j], sim.f[j]
    est = A.rolling_margin(x, f, acfg, seed=m.seed)
    Mday = sim.M_true[j].reshape(D, L.BARS).mean(1)
    mx = np.array([np.abs(x[d * L.BARS:(d + 1) * L.BARS]).max() for d in range(D)])
    sd0 = np.std(x[:max(ramp, cfg.window) * L.BARS])
    crisis = next((d for d in range(D) if mx[d] > 10 * sd0), None)
    track = [{"day": r["day"] - 1, "M_hat": r["M_hat"], "lo": r["lo"]} for r in est]
    th = sim.kDv_hist[j, :nv].astype(float) * cfg.theta_D / L.KMAX                    # (nv, D) stance in force on day d
    users = sim.users_hist[j, :nv].astype(float)
    dF = [(users[:, d - 1] * (th[:, d] - th[:, d - 1])).sum() for d in range(ramp + 1, D)]
    k = sim.kDv_hist[j, :nv]
    same_day = None
    if nv > 1:
        ch = np.diff(k[:, ramp:].astype(int), axis=1) != 0
        any2 = [(ch[a] & ch[b]).sum() for a in range(nv) for b in range(a + 1, nv)]
        same_day = float(np.sum(any2) / max(ch.any(0).sum(), 1))
    first_leave = [next((d for d in range(ramp, D) if k[v, d] != cfg.kD0), None) for v in range(nv)]
    return {"scenario": m.scenario, "seed": m.seed, "models": list(m.models), "crisis": crisis,
            "true0": next((d for d in range(D) if Mday[d] <= 0), None), "min_margin": float(Mday[ramp:].min()),
            "S": float(np.var(dF)) if dF else 0.0, "std": B.warnings(track), "same_day_change_share": same_day,
            "first_leave_day": first_leave, "final_stance": [int(v) for v in k[:, -1]],
            "stance_paths": k[:, ramp:].tolist()}


def _holm(p):
    order = np.argsort(p); mm = len(p); adj = np.empty(mm); run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (mm - rank) * p[i])); adj[i] = run
    return adj.tolist()


def evaluate(runs, n_models_ok, parse_bad):
    valid = n_models_ok >= N_MODELS and not parse_bad
    by = {(r["scenario"], r["seed"]): r for r in runs}
    seeds = sorted({r["seed"] for r in runs})
    monos = [f"mono_{j + 1}" for j in range(N_MODELS)]
    ratio, wins1, loss1, wins2, loss2, diff2 = [], 0, 0, 0, 0, []
    for s in seeds:
        dv = by[("diverse", s)]; ms = [by[(m, s)] for m in monos if (m, s) in by]
        mS = float(np.mean([r["S"] for r in ms])); mM = float(np.mean([r["min_margin"] for r in ms]))
        ratio.append(dv["S"] / mS if mS > 0 else (1.0 if dv["S"] == 0 else np.inf))
        wins1 += dv["S"] < mS; loss1 += dv["S"] > mS
        wins2 += dv["min_margin"] > mM; loss2 += dv["min_margin"] < mM; diff2.append(dv["min_margin"] - mM)
    p1 = float(stats.binom.sf(wins1 - 1, wins1 + loss1, 0.5)) if wins1 + loss1 else 1.0
    p2 = float(stats.binom.sf(wins2 - 1, wins2 + loss2, 0.5)) if wins2 + loss2 else 1.0
    adj = _holm([p1, p2])
    ctrl = [r for r in runs if r["scenario"] == "control"]
    fa = sum(r["std"]["t2z"] is not None for r in ctrl)
    out = {"valid": valid, "n_seeds": len(seeds),
           "P1": {"lower": wins1, "higher": loss1, "median_ratio": float(np.median(ratio)), "p": p1, "p_holm": adj[0],
                  "pass": bool(valid and adj[0] < ALPHA and np.median(ratio) <= 0.5)},
           "P2": {"higher": wins2, "lower": loss2, "median_diff": float(np.median(diff2)), "p": p2, "p_holm": adj[1],
                  "pass": bool(valid and adj[1] < ALPHA)},
           "P3": {"false_alarms": fa, "n": len(ctrl), "pass": bool(valid and fa <= 3)}}
    arms = ["control", "diverse"] + monos
    out["secondary"] = {
        "same_day_change_share_median": float(np.nanmedian([r["same_day_change_share"] for r in runs
                                                            if r["same_day_change_share"] is not None] or [np.nan])),
        "crises_by_arm": {a: sum(r["crisis"] is not None for r in runs if r["scenario"] == a) for a in arms},
        "true_cross_by_arm": {a: sum(r["true0"] is not None for r in runs if r["scenario"] == a) for a in arms},
        "median_min_margin_by_arm": {a: float(np.median([r["min_margin"] for r in runs if r["scenario"] == a])) for a in arms},
        "false_alarms_controls": {k: sum(r["std"][k] is not None for r in ctrl) for k in ("lost", "buffer", "t2z")},
        "warning_leads": {a: [r["crisis"] - r["std"]["t2z"] if (r["crisis"] is not None and r["std"]["t2z"] is not None
                                                                and r["std"]["t2z"] < r["crisis"]) else 0
                              for r in runs if r["scenario"] == a and r["crisis"] is not None] for a in arms},
        "first_leave_day_mono": {m: [r["first_leave_day"][0] for r in runs if r["scenario"] == m] for m in monos},
        "final_stance_mono": {m: [r["final_stance"][0] for r in runs if r["scenario"] == m] for m in monos}}
    return out


def numbers_tex(e, meta):
    v = lambda k: "passed" if e[k]["pass"] else "failed"
    return "\n".join(["% generated by b3_diversity.py; do not edit",
                      "\\newcommand{\\BthreeSeeds}{%d}\\newcommand{\\BthreeRatio}{%.2f}" % (e["n_seeds"], e["P1"]["median_ratio"]),
                      "\\newcommand{\\BthreeLower}{%d}\\newcommand{\\BthreeHigher}{%d}" % (e["P1"]["lower"], e["P1"]["higher"]),
                      "\\newcommand{\\BthreeMarginWins}{%d}\\newcommand{\\BthreeMarginLosses}{%d}" % (e["P2"]["higher"], e["P2"]["lower"]),
                      "\\newcommand{\\BthreeFA}{%d}\\newcommand{\\BthreeModels}{%s}" % (e["P3"]["false_alarms"], ", ".join(meta["models"]).replace("_", "\\_")),
                      f"\\newcommand{{\\BthreePone}}{{{v('P1')}}}\\newcommand{{\\BthreePtwo}}{{{v('P2')}}}\\newcommand{{\\BthreePthree}}{{{v('P3')}}}"]) + "\n"


# ------------------------------------------------------------------------------------------------------------- the run
def gate(skip=False):
    if skip:
        return None, None, None
    assert SPEC.exists(), "Test B3 is a draft and is not registered"
    sha = hashlib.sha256(SPEC.read_bytes()).hexdigest()
    assert sha == SPEC.with_suffix(".sha256").read_text().strip(), "specification hash mismatch"
    spec = json.loads(SPEC.read_text())
    for key, f in PIPELINE:
        assert hashlib.sha256((HERE / f).read_bytes()).hexdigest() == spec[key], f"{f} changed after registration"
    reg = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", str(SPEC.relative_to(ROOT))], cwd=ROOT, text=True).strip()
    assert reg, "the specification is not committed"
    return spec, sha, reg


def run(load, out_dir, counter=COUNTER, resume=False, skip_gate=False, seeds=SEEDS, days=DAYS, cfg_kw=None, meta=None,
        log=print, drop=None):
    """`load(model)` returns a backend (Backend4 in the registered run). Opens the counter, screens the candidates,
    simulates, evaluates. After a disconnect, resume=True reuses the saved screen and the checkpoint."""
    spec, sha, reg = gate(skip_gate)
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    ck, scr = out_dir / "B3_checkpoint.pkl", out_dir / "B3_screen.json"
    if resume:
        assert skip_gate or json.loads(Path(counter).read_text())["opens"] == 1, "nothing to resume: the test was not opened"
        saved = json.loads(scr.read_text())
        models = saved["chosen"]; backends = {m: load(m) for m in models}
    else:
        if not skip_gate:
            c = json.loads(Path(counter).read_text()); assert c["opens"] == 0, "Test B3 was already opened; it runs once"
            Path(counter).write_text(json.dumps({"opens": 1, "spec_sha256": sha, "registration_commit": reg,
                                                 "opened_utc": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
        backends, results = screen(load, log, drop)
        models = list(backends)
        scr.write_text(json.dumps({"chosen": models, "results": results}, indent=1, default=float))
    if len(models) < N_MODELS:
        res = {"test": "B3", "void": True, "screen": json.loads(scr.read_text()), "spec_sha256": sha, "registration_commit": reg}
        for p in ([out_dir / RESULT.name] + ([] if skip_gate else [RESULT])):
            p.write_text(json.dumps(res, indent=1, default=float) + "\n")
        log(f"B3 is void: only {len(models)} models passed the screen")
        return res
    cfg = L.LConfig(days=days, prompt="v2", **(cfg_kw or {}))
    sim = L.load(ck) if (resume and ck.exists()) else DivSim(cfg, make_markets(models, seeds))
    if resume and ck.exists():
        log(f"resumed at day {sim.day}")
    sim.run(MultiBackend(backends), checkpoint=ck, every=4, log=log)
    runs = [market_summary(sim, j) for j in range(sim.K)]
    tm = np.array(sim.timing)
    meta = {**(meta or {}), "models": models, "llm_calls": sim.calls, "parse_failures": sim.parse_fail,
            "unparsed_examples": sim.raw_examples, "seconds_model": float(tm[:, 1].sum())}
    res = {"test": "B3", "void": False, "spec_sha256": sha, "registration_commit": reg,
           "run_utc": datetime.now(timezone.utc).isoformat(), "meta": meta, "screen": json.loads(scr.read_text()),
           "evaluation": evaluate(runs, len(models), sim.parse_fail > 0.05 * max(sim.calls, 1)), "runs": runs}
    for p in ([out_dir / RESULT.name, out_dir / NUMBERS.name] + ([] if skip_gate else [RESULT, NUMBERS])):
        p.write_text(json.dumps(res, indent=1, default=float) + "\n" if p.suffix == ".json" else numbers_tex(res["evaluation"], meta))
    log(json.dumps({k: v for k, v in res["evaluation"].items() if k != "secondary"}, indent=1, default=float))
    return res


def selftest():
    import tempfile

    class Mock(L.MockBackend):
        def __init__(self, m, passes=True):
            self.m, self.passes = m, passes

        def decide(self, reqs):
            out = super().decide(reqs)
            if self.m.startswith("allenai"):                 # a model that never changes its stance
                return [str(q["obs"]["k"]) for q in reqs]
            return out

    def load(m):
        return Mock(m)
    # the screen: mock probes never pass B2's rule, so force passes to exercise the family rule
    orig = L.probe
    L.probe = lambda be, **kw: {**orig(be, **kw), "passes": not be.m.startswith("Qwen/Qwen3")}
    try:
        with tempfile.TemporaryDirectory() as td:
            res = run(load, td, skip_gate=True, seeds=range(1, 4), days=40, cfg_kw={"window": 5}, log=lambda s: None)
            assert res["meta"]["models"] == [c for c, _ in CANDIDATES[:3]], res["meta"]["models"]
            e = res["evaluation"]
            assert e["n_seeds"] == 3 and len(res["runs"]) == 15 and numbers_tex(e, res["meta"]).startswith("%")
            dv = [r for r in res["runs"] if r["scenario"] == "diverse"][0]
            assert len(dv["stance_paths"]) == 3 and len(dv["final_stance"]) == 3
            print(json.dumps({k: v for k, v in e.items() if k != "secondary"}, default=float)[:600])
            res2 = run(load, td, skip_gate=True, resume=True, seeds=range(1, 4), days=40, cfg_kw={"window": 5}, log=lambda s: None)
            assert res2["evaluation"]["P1"] == e["P1"]
        L.probe = lambda be, **kw: {**orig(be, **kw), "passes": be.m.startswith("Qwen/Qwen2.5")}
        with tempfile.TemporaryDirectory() as td:
            assert run(load, td, skip_gate=True, seeds=range(1, 2), days=30, cfg_kw={"window": 5}, log=lambda s: None)["void"]
    finally:
        L.probe = orig
    try:
        gate(); raise SystemExit("gate should refuse an unregistered draft")
    except AssertionError as err:
        print("gate refuses as expected:", err)
    print("b3 selftest: PASS")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
