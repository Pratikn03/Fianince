"""Test B1's market with language-model trading desks (exploratory pilot for a future Test B2; not a registered test).

The market, the vendor model, the adoption ramp, the public-data estimators and the warning rules are those of Test B1
(ailoop_sim.py, b1_ailoop.py; imported, not changed). What changes is who the independent agents are:

* B1: each independent agent learned its response online with a normalized-LMS rule.
* Here: each independent agent is a language-model trading desk. Once a simulated day it reads a short report (recent
  daily closes, yesterday's five-minute statistics, its own stance and profit over the last five days) and replies with a
  stance k in {-5,...,5}. The agent then trades every bar through the B1 rule u = L tanh(theta y / L) with
  theta = k * theta_unit and its own exponential-memory signal y. Positive k follows moves, negative k trades against them.
  Desks differ by persona (8 personas), memory rate and sampling seed; they all run the same small open model, as real
  desks built on one foundation model would, but with their own prompts.
* Vendor model: as in B1, a fixed momentum product (theta_D per user) adopted along a ramp ("fixed"), or, in the
  exploratory "llm" arm, a single shared language model that sets one stance per day for every user (temperature 0).

The true linearized margin stays computable, M(t) = 1 - a - kappa * sum_i theta_i(t), which is what makes the
evaluation of the public-data certificate possible.

Backends: "mock" (a rule that reacts to its own profit; for self-tests without a GPU), "hf" (transformers, batched) and
"vllm". The simulation runs many markets in lockstep so every simulated day is one batch of model calls.
"""
import json
import math
import pickle
import re
import sys
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ailoop_sim as A  # noqa: E402
import b1_ailoop as B  # noqa: E402

BARS = A.BARS
KMAX = 5

COMMON = ("You trade one market automatically every five minutes. Once a day you set your stance, an integer from -5 to 5. "
          "A positive stance means you buy when the price is above its recent average and sell when it is below "
          "(you bet that moves continue). A negative stance means the opposite (you bet that moves reverse). "
          "0 means you do not trade. A larger absolute stance means larger trades, larger profits and larger losses. "
          "Your goal is to make money. Reply with the integer only.")
PERSONAS = [
    "You are a cautious trader who dislikes large losses.",
    "You are an aggressive quantitative trader who sizes up when a strategy is working.",
    "You are a patient trader who changes positions slowly.",
    "You are a data-driven trader who relies on recent statistics.",
    "You are a discretionary trader who reads recent price action.",
    "You are a trader who tends to think that moves reverse, but you change your mind when the evidence says so.",
    "You are a trader who tends to think that trends persist, but you change your mind when the evidence says so.",
    "You are a market-neutral trader who prefers steady small profits.",
]
VENDOR_SYSTEM = ("You are the decision model of a widely used AI trading product. Every user of the product trades with the "
                 "stance you set. " + COMMON)


@dataclass
class LConfig:
    days: int = 120
    n_agents: int = 50
    a: float = 0.9
    kappa: float = 1.0
    s_eps: float = 0.5
    L: float = 2.0
    theta_unit: float = 0.004       # independent desks: theta = k * theta_unit, |k| <= 5
    k0: int = -1                    # desks start mildly contrarian (B1 learners start at theta = -0.002)
    r_lo: float = 0.3
    r_hi: float = 0.95
    theta_D: float = 0.007          # vendor theta per user (the B1 value); LLM vendor: theta = kD * theta_D / 5
    kD0: int = 5                    # LLM vendor starts as the B1 momentum product
    ramp_start: float = 0.2
    ramp_end: float = 0.8
    window: int = 10
    lags: int = 12
    boot: int = 100
    temperature: float = 0.7
    prompt: str = "v1"              # v1: pilot 1 (ends with the current stance); v2: evidence last, no stance echo


@dataclass
class Market:
    scenario: str                   # control | fast | slow | llmvendor
    seed: int
    s_max: float = 0.8
    r_D: float = 0.9
    vendor: str = "fixed"           # fixed | llm


SCENARIOS = {"control": dict(s_max=0.0), "fast": dict(r_D=0.9), "slow": dict(r_D=0.995),
             "llmvendor": dict(r_D=0.9, vendor="llm")}


def make_markets(scenarios, seeds):
    return [Market(scenario=s, seed=sd, **SCENARIOS[s]) for sd in seeds for s in scenarios]


def user_text(variant, d, closes, vol, ac, ks, pnls, k, header=""):
    """The daily report. v1 (pilot 1) ends with "Your current stance is k", which a small model simply copies; v2 puts
    the desk's own record first and the market evidence last and does not restate the current stance."""
    mk = ("Daily closing prices, oldest first: " + ", ".join(f"{c:.1f}" for c in closes) + ".\n"
          f"Yesterday's five-minute price changes: volatility {vol:.2f}, correlation of each change with the next {ac:+.2f}.")
    if variant == "v1":
        own = ("Your stance and profit on each of the last days, oldest first: "
               + ", ".join(f"{int(a):+d} ({1000 * b:+.0f} dollars)" for a, b in zip(ks, pnls)) + ".")
        return (f"Day {d} has closed. {header}".rstrip() + f"\n{mk}\n{own}"
                + f"\nYour current stance is {int(k):+d}. What is your stance for tomorrow?")
    if variant == "v2":
        n = len(ks)
        own = "\n".join(f"- day {d - n + 1 + i}: stance {int(a):+d}, profit {1000 * b:+.0f} dollars" for i, (a, b) in enumerate(zip(ks, pnls)))
        return (f"Day {d} has closed. {header}".rstrip() + f"\nYour recent results, oldest first:\n{own}\n"
                f"Market:\n{mk}\nChoose your stance for tomorrow.")
    raise ValueError(variant)


# --------------------------------------------------------------------------------------------------------------- backends
class MockBackend:
    """No model: a desk keeps its stance after a profit and moves one step toward the other sign after a loss, with
    occasional random steps. It answers in text so that the parser is exercised."""
    name = "mock"

    def decide(self, reqs):
        out = []
        for q in reqs:
            rng = np.random.default_rng(q["seed"])
            k, pnl = q["obs"]["k"], q["obs"]["pnl_last"]
            if pnl < 0:
                k = k - 1 if k > 0 else (k + 1 if k < 0 else int(rng.choice([-1, 1])))
                if k == 0 and pnl < 0:
                    k = int(rng.choice([-1, 1]))
            if rng.random() < 0.15:
                k += int(rng.choice([-1, 1]))
            out.append(f"{int(np.clip(k, -KMAX, KMAX))}")
        return out


class HFBackend:
    """transformers, batched greedy or sampled generation (left padding). Requests are grouped by temperature."""
    name = "hf"

    def __init__(self, model, batch_size=96, max_new_tokens=4, dtype="float16", quant4=False):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(model)
        self.tok.padding_side = "left"
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        if dtype == "auto":
            dtype = "bfloat16" if torch.cuda.is_bf16_supported() else "float16"
        kw = dict(torch_dtype=getattr(torch, dtype), device_map="cuda")
        if quant4:                                              # 4-bit weights (bitsandbytes) so a 14B model fits on an L4
            from transformers import BitsAndBytesConfig
            kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                           bnb_4bit_compute_dtype=getattr(torch, dtype))
        self.model = AutoModelForCausalLM.from_pretrained(model, **kw)
        self.model.eval()
        self.bs, self.mnt = batch_size, max_new_tokens

    def _text(self, q):
        msgs = [{"role": "system", "content": q["system"]}, {"role": "user", "content": q["user"]}]
        # enable_thinking=False switches off Qwen3's reasoning block; other templates ignore the argument
        return self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)

    def decide(self, reqs):
        out = [None] * len(reqs)
        groups = {}
        for i, q in enumerate(reqs):
            groups.setdefault(float(q["temperature"]), []).append(i)
        for temp, idx in groups.items():
            s = 0
            while s < len(idx):
                chunk = idx[s:s + self.bs]
                self.torch.manual_seed(int(reqs[chunk[0]]["seed"]) % (2 ** 31))
                enc = self.tok([self._text(reqs[i]) for i in chunk], return_tensors="pt", padding=True).to("cuda")
                kw = dict(max_new_tokens=self.mnt, pad_token_id=self.tok.pad_token_id)
                kw.update(dict(do_sample=True, temperature=temp, top_p=0.95) if temp > 0 else dict(do_sample=False))
                try:
                    with self.torch.no_grad():
                        gen = self.model.generate(**enc, **kw)
                except self.torch.cuda.OutOfMemoryError:
                    # a large model leaves little room for the batch: halve the batch for good and retry this chunk
                    del enc; self.torch.cuda.empty_cache()
                    if self.bs == 1:
                        raise
                    self.bs = max(1, self.bs // 2)
                    print(f"[HFBackend] out of GPU memory: batch size now {self.bs}")
                    continue
                texts = self.tok.batch_decode(gen[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
                for i, t in zip(chunk, texts):
                    out[i] = t
                s += len(chunk)
        return out


class VLLMBackend:
    name = "vllm"

    def __init__(self, model, max_new_tokens=4, dtype="half", gpu_memory_utilization=0.85):
        from vllm import LLM, SamplingParams
        self.SP = SamplingParams
        self.llm = LLM(model=model, dtype=dtype, gpu_memory_utilization=gpu_memory_utilization, max_model_len=1024,
                       enable_prefix_caching=True, enforce_eager=True, seed=0)
        self.mnt = max_new_tokens

    def decide(self, reqs):
        msgs = [[{"role": "system", "content": q["system"]}, {"role": "user", "content": q["user"]}] for q in reqs]
        sps = [self.SP(temperature=float(q["temperature"]), top_p=0.95 if q["temperature"] > 0 else 1.0,
                       max_tokens=self.mnt, seed=int(q["seed"]) % (2 ** 31)) for q in reqs]
        res = self.llm.chat(msgs, sampling_params=sps, use_tqdm=False, chat_template_kwargs={"enable_thinking": False})
        return [r.outputs[0].text for r in res]


def make_backend(kind, model=None, **kw):
    if kind == "mock":
        return MockBackend()
    if kind == "hf":
        return HFBackend(model, **kw)
    if kind == "vllm":
        return VLLMBackend(model, **kw)
    raise ValueError(kind)


_INT = re.compile(r"[-+−]?\s*\d+")


def parse_stance(text):
    """First integer in the reply, clipped to [-5, 5]; None if there is none."""
    m = _INT.search(text or "")
    if not m:
        return None
    return int(np.clip(int(m.group(0).replace("−", "-").replace(" ", "")), -KMAX, KMAX))


# ------------------------------------------------------------------------------------------------------------- simulation
class Sim:
    """K markets in lockstep. Arrays are (K, N) for agents and (K, T) for time series."""

    def __init__(self, cfg: LConfig, markets):
        self.cfg, self.markets = cfg, markets
        K, N, D = len(markets), cfg.n_agents, cfg.days
        T = D * BARS
        self.K, self.N, self.T = K, N, T
        self.rngs = [np.random.default_rng(m.seed) for m in markets]
        self.r = np.stack([g.uniform(cfg.r_lo, cfg.r_hi, N) for g in self.rngs])
        self.t_adopt = np.full((K, N), np.inf)
        t0, t1 = cfg.ramp_start * T, cfg.ramp_end * T
        for j, (m, g) in enumerate(zip(markets, self.rngs)):
            order = g.permutation(N); n = int(round(m.s_max * N))
            self.t_adopt[j, order[:n]] = np.sort(g.uniform(t0, t1, n))
        self.t0 = int(math.ceil(t0))
        self.rD = np.array([m.r_D for m in markets])
        self.vendor_llm = np.array([m.vendor == "llm" for m in markets])
        self.k = np.full((K, N), cfg.k0, dtype=np.int64)
        self.kD = np.full(K, cfg.kD0, dtype=np.int64)
        self.y = np.zeros((K, N)); self.yD = np.zeros(K)
        self.x = np.zeros((K, T + 1)); self.f = np.zeros((K, T + 1))
        self.M_true = np.zeros((K, T)); self.share = np.zeros((K, T))
        self.k_hist = np.zeros((K, N, D), dtype=np.int8); self.kD_hist = np.zeros((K, D), dtype=np.int8)
        self.pnl_hist = np.zeros((K, N, D)); self.vendor_pnl = np.zeros((K, D))
        self.theta_at_ramp = None
        self.day = 0
        self.parse_fail = 0; self.calls = 0; self.raw_examples = []
        self.timing = []

    def theta_vendor(self):
        return np.where(self.vendor_llm, self.kD * self.cfg.theta_D / KMAX, self.cfg.theta_D)

    def step_day(self):
        cfg, d = self.cfg, self.day
        K = self.K
        noise = np.stack([g.normal(size=(BARS, 2)) for g in self.rngs])          # (K, BARS, 2)
        th_ind = self.k * cfg.theta_unit
        thD = self.theta_vendor()[:, None]
        pnl = np.zeros((K, self.N)); vpnl = np.zeros(K)
        self.k_hist[:, :, d] = self.k; self.kD_hist[:, d] = self.kD
        for b in range(BARS):
            t = d * BARS + b
            adopted = t >= self.t_adopt
            theta = np.where(adopted, thD, th_ind)
            if self.theta_at_ramp is None and t >= self.t0:
                self.theta_at_ramp = theta.mean(1).copy()
            sig = np.where(adopted, self.yD[:, None], self.y)
            u = cfg.L * np.tanh(theta * sig / cfg.L)
            self.M_true[:, t] = 1 - cfg.a - cfg.kappa * theta.sum(1); self.share[:, t] = adopted.mean(1)
            ft = u.sum(1) + noise[:, b, 0]
            xt = self.x[:, t]
            xn = cfg.a * xt + cfg.kappa * ft + cfg.s_eps * noise[:, b, 1]
            self.f[:, t + 1] = ft; self.x[:, t + 1] = xn
            dx = (xn - xt)[:, None]
            pnl += np.where(adopted, 0.0, u * dx)
            uD = cfg.L * np.tanh(thD[:, 0] * self.yD / cfg.L)
            vpnl += uD * dx[:, 0]
            self.y = self.r * self.y + (1 - self.r) * xn[:, None]
            self.yD = self.rD * self.yD + (1 - self.rD) * xn
        self.pnl_hist[:, :, d] = pnl; self.vendor_pnl[:, d] = vpnl
        self.day += 1

    # ---- reports the desks read
    def _market(self, j):
        d = self.day                                            # days completed
        closes = [100 + self.x[j, (dd + 1) * BARS] for dd in range(max(0, d - 10), d)]
        dx = np.diff(self.x[j, (d - 1) * BARS:d * BARS + 1])
        ac = float(np.corrcoef(dx[:-1], dx[1:])[0, 1]) if dx.std() > 0 else 0.0
        return closes, float(dx.std()), ac

    def requests(self):
        """One request per desk that has not adopted the vendor model by the end of the day just completed, and one per
        market with an LLM vendor once adoption has started."""
        cfg, d = self.cfg, self.day
        tend = d * BARS
        reqs = []
        for j, m in enumerate(self.markets):
            closes, vol, ac = self._market(j)
            pv = getattr(cfg, "prompt", "v1")
            lo = max(0, d - 5)
            for i in range(self.N):
                if tend >= self.t_adopt[j, i]:
                    continue
                sysm = PERSONAS[i % len(PERSONAS)] + " " + COMMON
                user = user_text(pv, d, closes, vol, ac, self.k_hist[j, i, lo:d], self.pnl_hist[j, i, lo:d], self.k[j, i])
                reqs.append({"who": ("desk", j, i), "system": sysm, "user": user, "temperature": cfg.temperature,
                             "seed": (m.seed * 1000003 + d * 1009 + i) % (2 ** 31),
                             "obs": {"k": int(self.k[j, i]), "pnl_last": float(self.pnl_hist[j, i, d - 1])}})
            if m.vendor == "llm" and tend >= self.t0:
                users = int((self.t_adopt[j] <= tend).sum())
                per_user = self.vendor_pnl[j, lo:d]                     # the profit of one user of the product
                user = user_text(pv, d, closes, vol, ac, self.kD_hist[j, lo:d], per_user, self.kD[j],
                                 header=f"{users} of {self.N} trading desks in this market now use your product.")
                reqs.append({"who": ("vendor", j, -1), "system": VENDOR_SYSTEM, "user": user, "temperature": 0.0,
                             "seed": (m.seed * 1000003 + d * 1009 + 999) % (2 ** 31),
                             "obs": {"k": int(self.kD[j]), "pnl_last": float(per_user[-1]) if len(per_user) else 0.0}})
        return reqs

    def apply(self, reqs, texts):
        for q, t in zip(reqs, texts):
            kind, j, i = q["who"]
            k = parse_stance(t)
            self.calls += 1
            if k is None:
                self.parse_fail += 1
                if len(self.raw_examples) < 20:
                    self.raw_examples.append(t)
                continue
            if kind == "desk":
                self.k[j, i] = k
            else:
                self.kD[j] = k

    def run(self, backend, checkpoint=None, every=5, log=print):
        while self.day < self.cfg.days:
            t_a = time.time()
            self.step_day()
            t_b = time.time()
            n = 0
            if self.day < self.cfg.days:
                reqs = self.requests(); n = len(reqs)
                if reqs:
                    self.apply(reqs, backend.decide(reqs))
            t_c = time.time()
            self.timing.append((t_b - t_a, t_c - t_b, n))
            if checkpoint and (self.day % every == 0 or self.day == self.cfg.days):
                save(self, checkpoint)
            left = self.cfg.days - self.day
            per = np.mean([a + b for a, b, _ in self.timing[-5:]])
            log(f"day {self.day:3d}/{self.cfg.days}  calls {n:5d}  market {t_b - t_a:5.1f}s  model {t_c - t_b:5.1f}s  "
                f"mean desk stance {self.k.mean():+.2f}  min true margin {self.M_true[:, (self.day - 1) * BARS:self.day * BARS].mean(1).min():+.3f}  "
                f"parse failures {self.parse_fail}/{self.calls}  ETA {left * per / 60:5.1f} min")
        return self


def save(sim, path):
    path = Path(path); tmp = path.with_suffix(".tmp")
    with open(tmp, "wb") as fh:
        pickle.dump(sim, fh, protocol=pickle.HIGHEST_PROTOCOL)
    tmp.replace(path)


def load(path):
    with open(path, "rb") as fh:
        return pickle.load(fh)


# ------------------------------------------------------------------------------------------------------------- evaluation
def static_threshold(cfg, theta_bar, theta_D):
    M0 = 1 - cfg.a - cfg.kappa * cfg.n_agents * theta_bar
    c = cfg.kappa * cfg.n_agents * (theta_D - theta_bar)
    return float(M0 / c) if c > 0 else None


def summarize_market(sim, j, rbar=B.RBAR):
    cfg, m = sim.cfg, sim.markets[j]
    acfg = A.Config(days=cfg.days, window=cfg.window, lags=cfg.lags, boot=cfg.boot, seed=m.seed)
    x, f = sim.x[j], sim.f[j]
    est = A.rolling_margin(x, f, acfg, seed=m.seed)
    est_d = A.rolling_margin(x, f, acfg, rbar_series=A.ema_series(x, rbar), seed=m.seed)
    D = cfg.days
    Mday = sim.M_true[j].reshape(D, BARS).mean(1); sday = sim.share[j].reshape(D, BARS).mean(1)
    mx = np.array([np.abs(x[d * BARS:(d + 1) * BARS]).max() for d in range(D)])
    nb = max(int(cfg.ramp_start * D), cfg.window)
    sd0 = np.std(x[:nb * BARS])
    crisis = next((d for d in range(D) if mx[d] > 10 * sd0), None)
    track = [{"day": r["day"] - 1, "M_true": float(Mday[r["day"] - 1]), "share": float(sday[r["day"] - 1]),
              "M_hat": r["M_hat"], "lo": r["lo"], "hi": r["hi"], "M_hat_disc": est_d[i]["M_hat"], "lo_disc": est_d[i]["lo"]}
             for i, r in enumerate(est)]
    thD = cfg.theta_D if m.vendor == "fixed" else float(sim.kD_hist[j, int(cfg.ramp_start * D)]) * cfg.theta_D / KMAX
    err = [abs(t["M_hat"] - t["M_true"]) for t in track if t["M_true"] > 0.2]
    ks = sim.k_hist[j].astype(float)                                       # (N, D) stance used on each day
    indep = np.isinf(sim.t_adopt[j])[:, None] | (np.arange(D)[None, :] * BARS < sim.t_adopt[j][:, None])
    mean_stance = [float(ks[indep[:, d], d].mean()) if indep[:, d].any() else None for d in range(D)]
    # does a desk respond to its own profit? change in stance after a loss vs after a profit, in the direction of |k|
    dk, after_loss = [], []
    for i in range(cfg.n_agents):
        for d in range(1, D - 1):
            if indep[i, d] and indep[i, d + 1]:
                dk.append(abs(ks[i, d + 1]) - abs(ks[i, d])); after_loss.append(sim.pnl_hist[j, i, d] < 0)
    dk, after_loss = np.array(dk), np.array(after_loss)
    return {"scenario": m.scenario, "seed": m.seed, "vendor": m.vendor, "crisis": crisis,
            "true0": next((d for d in range(D) if Mday[d] <= 0), None),
            "share_at_crisis": float(sday[crisis]) if crisis is not None else None,
            "s_star_static": static_threshold(cfg, float(sim.theta_at_ramp[j]), thD) if m.s_max > 0 else None,
            "std": B.warnings(track), "disc": B.warnings(track, True),
            "tracking_error_median": float(np.median(err)) if err else None,
            "llm": {"mean_desk_stance_by_day": mean_stance,
                    "vendor_stance_by_day": sim.kD_hist[j].tolist() if m.vendor == "llm" else None,
                    "abs_stance_change_after_loss": float(dk[after_loss].mean()) if after_loss.any() else None,
                    "abs_stance_change_after_profit": float(dk[~after_loss].mean()) if (~after_loss).any() else None,
                    "stance_change_rate": float(np.mean(np.abs(np.diff(ks, axis=1)) > 0))},
            "M_true_by_day": Mday.tolist(), "share_by_day": sday.tolist(),
            "track": track}


def evaluate_pilot(runs):
    """B1's quantities on the pilot (exploratory, no tests). Controls, then the fixed-vendor runs, then the LLM vendor."""
    ctrl = [r for r in runs if r["scenario"] == "control"]
    fixed = [r for r in runs if r["scenario"] in ("fast", "slow")]
    llmv = [r for r in runs if r["scenario"] == "llmvendor"]

    def block(rs):
        cr = [r for r in rs if r["crisis"] is not None]
        lead = lambda r, e, k: B.lead(r, e, k)
        below = [r for r in cr if r["s_star_static"] is not None]
        return {"n": len(rs), "crises": len(cr),
                "crisis_days": [r["crisis"] for r in rs],
                "t2z_early": sum(lead(r, "std", "t2z") > 0 for r in cr),
                "t2z_leads": [lead(r, "std", "t2z") for r in cr],
                "buffer_gain_disc": [lead(r, "disc", "buffer") - lead(r, "std", "buffer") for r in cr],
                "share_at_crisis": [r["share_at_crisis"] for r in cr],
                "static_threshold": [r["s_star_static"] for r in rs],
                "below_static": sum(r["share_at_crisis"] < r["s_star_static"] for r in below), "n_below_eval": len(below)}
    fa = {f"{e}_{k}": sum(r[e][k] is not None for r in ctrl) for e in ("std", "disc") for k in ("lost", "buffer", "t2z")}
    return {"controls": {"n": len(ctrl), "false_alarms": fa, "crises": sum(r["crisis"] is not None for r in ctrl)},
            "fixed_vendor": block(fixed), "llm_vendor": block(llmv),
            "desk_behaviour": {
                "abs_change_after_loss": _nanmean([r["llm"]["abs_stance_change_after_loss"] for r in runs]),
                "abs_change_after_profit": _nanmean([r["llm"]["abs_stance_change_after_profit"] for r in runs]),
                "stance_change_rate": _nanmean([r["llm"]["stance_change_rate"] for r in runs])}}


def _nanmean(v):
    v = [x for x in v if x is not None]
    return float(np.mean(v)) if v else None


def results(sim, backend_name, model, extra=None):
    runs = [summarize_market(sim, j) for j in range(sim.K)]
    tm = np.array(sim.timing) if sim.timing else np.zeros((1, 3))
    return {"what": "exploratory pilot for Test B2 (language-model desks in Test B1's market); not a registered test",
            "backend": backend_name, "model": model, "config": asdict(sim.cfg),
            "markets": [asdict(m) for m in sim.markets],
            "llm_calls": sim.calls, "parse_failures": sim.parse_fail, "unparsed_examples": sim.raw_examples,
            "seconds_market": float(tm[:, 0].sum()), "seconds_model": float(tm[:, 1].sum()),
            "calls_per_second": float(tm[:, 2].sum() / max(tm[:, 1].sum(), 1e-9)),
            "evaluation": evaluate_pilot(runs), "runs": runs, **(extra or {})}


_CALM = dict(closes=[100.2, 99.8, 100.1, 100.0, 99.9], vol=0.60, ac=-0.30)
_TREND = dict(closes=[100.5, 102.0, 104.1, 107.3, 111.8], vol=1.40, ac=+0.25)
# expected: "down" / "up" = the stance should move strictly that way (a losing desk); "not_up" / "not_down" = a winning
# desk should not move against the evidence. In every probe the right move differs from simply copying the stance.
PROBES = [
    dict(label="losing while following moves in a reverting market", ks=[2, 2, 2], pnls=[-.15, -.12, -.17], expected="down", **_CALM),
    dict(label="losing big while following moves in a reverting market", ks=[4, 4, 4], pnls=[-.35, -.30, -.41], expected="down", **_CALM),
    dict(label="losing against a strong trend", ks=[-2, -2, -2], pnls=[-.30, -.45, -.70], expected="up", **_TREND),
    dict(label="losing big against a strong trend", ks=[-4, -4, -4], pnls=[-.60, -.90, -1.4], expected="up", **_TREND),
    dict(label="winning while trading against moves", ks=[-2, -2, -2], pnls=[.14, .16, .12], expected="not_up", **_CALM),
    dict(label="winning with a strong trend", ks=[3, 3, 3], pnls=[.40, .60, .90], expected="not_down", **_TREND),
]


def _moved(expected, k0, k):
    return {"down": k < k0, "up": k > k0, "not_up": k <= k0, "not_down": k >= k0}[expected]


def probe(backend, temperature=0.0, variant="v1", samples=1):
    """Canned reports: does the model answer with an integer, and does its answer move with the evidence?
    Score per probe: the share of replies that move the way the evidence says (see PROBES)."""
    out = []
    for p, pb in enumerate(PROBES):
        user = user_text(variant, 30, pb["closes"], pb["vol"], pb["ac"], pb["ks"], pb["pnls"], pb["ks"][-1])
        for i, persona in enumerate(PERSONAS):
            for s_ in range(samples):
                out.append({"probe": pb["label"], "persona": i, "system": persona + " " + COMMON, "user": user,
                            "temperature": temperature, "seed": 17 + p * 31 + i * 7 + s_ * 1013, "obs": {"k": 0, "pnl_last": 0.0}})
    texts = backend.decide(out)
    for q, t in zip(out, texts):
        q["reply"] = t; q["stance"] = parse_stance(t)
        del q["system"], q["user"], q["obs"]
    summary = {}
    for pb in PROBES:
        st = [q["stance"] for q in out if q["probe"] == pb["label"]]
        ok = [s_ for s_ in st if s_ is not None]
        summary[pb["label"]] = {"current": pb["ks"][-1], "expected": pb["expected"], "stances": st,
                                "parsed": len(ok), "n": len(st),
                                "right_way": float(np.mean([_moved(pb["expected"], pb["ks"][-1], k) for k in ok])) if ok else 0.0,
                                "copied": float(np.mean([k == pb["ks"][-1] for k in ok])) if ok else 0.0}
    n = sum(v["n"] for v in summary.values()); parsed = sum(v["parsed"] for v in summary.values())
    passes = parsed / n >= 0.95 and all(v["right_way"] >= 0.6 for v in summary.values())
    return {"variant": variant, "temperature": temperature, "summary": summary, "parse_rate": parsed / n,
            "min_right_way": min(v["right_way"] for v in summary.values()), "passes": bool(passes), "replies": out}


def pilot(backend, model, seeds=(301, 302, 303), scenarios=("control", "fast", "slow", "llmvendor"), days=120,
          checkpoint=None, resume=False, cfg_kw=None, log=print):
    cfg = LConfig(days=days, **(cfg_kw or {}))
    if resume and checkpoint and Path(checkpoint).exists():
        sim = load(checkpoint); log(f"resumed at day {sim.day}")
    else:
        sim = Sim(cfg, make_markets(scenarios, seeds))
    sim.run(backend, checkpoint=checkpoint, log=log)
    return sim


def selftest():
    import tempfile
    be = MockBackend()
    assert parse_stance(" -3\n") == -3 and parse_stance("+7") == 5 and parse_stance("stance: 2") == 2 and parse_stance("no") is None
    with tempfile.TemporaryDirectory() as td:
        ck = Path(td) / "ck.pkl"
        sim = pilot(be, "mock", seeds=(1,), days=30, checkpoint=ck, cfg_kw=dict(window=5), log=lambda s: None)
        assert sim.day == 30 and sim.calls > 0 and sim.parse_fail == 0
        # resume from a mid-run checkpoint reproduces the same path
        sim2 = Sim(LConfig(days=30, window=5), make_markets(("control", "fast", "slow", "llmvendor"), (1,)))
        for _ in range(10):
            sim2.step_day(); r = sim2.requests(); sim2.apply(r, be.decide(r))
        save(sim2, ck); sim3 = load(ck).run(be, log=lambda s: None)
        assert np.allclose(sim3.x, sim.x), "resume does not reproduce the uninterrupted run"
        res = results(sim, "mock", "mock")
        json.dumps(res, default=float)
        print(json.dumps(res["evaluation"], indent=1, default=float)[:1500])
        for v in ("v1", "v2"):
            pr = probe(be, variant=v, temperature=0.7, samples=2)
            assert pr["parse_rate"] == 1.0, pr
        sim4 = pilot(be, "mock", seeds=(2,), days=25, cfg_kw=dict(window=5, prompt="v2"), log=lambda s: None)
        print(sim4.requests()[0]["user"])
    print("llm_ailoop selftest: PASS")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
