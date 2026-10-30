"""Declared finite-class, reset-episode experiment; not a public-market certificate."""
from dataclasses import dataclass
import numpy as np
from scipy.stats import norm


@dataclass(frozen=True)
class Economy:
    name: str
    q: tuple
    eta: tuple
    a: float = .4
    kappa: float = 1.


def response(e, horizon):
    x, y, h = 0., np.zeros(len(e.q)), []
    for t in range(horizon):
        x = e.a*x + e.kappa*(np.dot(e.q, y) + (t == 0))
        y = (1-np.array(e.eta))*y + np.array(e.eta)*x
        h.append(x)
    return np.array(h)


def candidates():
    es = []
    for phi in [0., .10, .25, .40, .50, .56]:
        for eta in [.02, .05, .2, .5, .8]:
            es.append(Economy(f"single_{phi}_{eta}", (phi,), (eta,)))
        for lo, hi in [(.02,.2),(.05,.8),(.2,.8),(.45,.55)]:
            es.append(Economy(f"split_{phi}_{lo}_{hi}",(phi/2,phi/2),(lo,hi)))
        # Fine, nearby two-cohort alternatives avoid equating a coarse-grid
        # singleton with the general ability to identify a trading population.
        if phi > 0:
            for center in [.2,.5]:
                for delta in [.005,.01,.02]:
                    es.append(Economy(f"close_split_{phi}_{center}_{delta}",
                                      (phi/2,phi/2),(center-delta,center+delta)))
    return es


def cost(inventory):
    """Full round-trip execution charge in dollars: linear plus quadratic."""
    return .002*np.abs(inventory) + .0002*np.asarray(inventory)**2


def account(e, shocks, inventory, wealth=1000., p0=100.):
    """Start flat, buy once at t=0, hold H one-minute bars, close at t=H.

    Constant dollar execution charges split equally between entry and exit.
    Cash + inventory*mark reconciles every bar. No borrowing interest or futures
    funding: this is a synthetic spot-equivalent, linear price-taking account.
    Orders do NOT change the background market; price impact is a cost schedule.
    """
    u = np.asarray(shocks, float)
    if u.ndim != 2 or not np.isfinite(u).all():
        raise ValueError("shocks must be finite episode x minute arrays")
    inv = float(inventory)
    if inv < 0 or inv*p0+cost(inv)/2 > wealth+1e-10:
        raise ValueError("long-only unlevered account; entry exceeds available cash")
    x, y = np.zeros(len(u)), np.zeros((len(u),len(e.q)))
    charge = float(cost(inv))
    cash = wealth-inv*p0-charge/2
    history = [np.full(len(u),wealth-charge/2)]
    prices = []
    for t in range(u.shape[1]):
        x = e.a*x + e.kappa*(y@np.array(e.q)+u[:,t])
        y = (1-np.array(e.eta))*y + np.array(e.eta)*x[:,None]
        p = p0+x
        if (p <= 0).any():
            raise ValueError("nonpositive synthetic price: declared account invalid")
        prices.append(p)
        history.append(cash+inv*p)
    terminal = cash+inv*prices[-1]-charge/2
    history.append(terminal)
    w = np.array(history).T
    return dict(wealth=w, terminal=terminal,
                loss_from_initial=np.maximum(0.,wealth-w.min(1)),
                peak_drawdown=(np.maximum.accumulate(w,axis=1)-w).max(1),
                price_delta=np.array(prices).T-p0,
                accounting_error=float(np.max(abs(w[:,-2]-charge/2-terminal))),
                entry_cash=cash, terminal_inventory=0.)


def confidence_mask(h, mean, sigma, N, gamma=.05):
    """Simultaneous Bonferroni band; known iid Gaussian tap errors only.

    Coverage needs the true response in the declared candidate class. Correlated
    or biased readings are deliberately separate assumption-violation studies.
    """
    L = len(mean)
    radius = sigma/np.sqrt(N)*norm.ppf(1-gamma/(2*L))
    return np.max(abs(h[:,:L]-mean),axis=1) <= radius, float(radius)


def safe_mask(grid, gains, budget, shock_bound=.04):
    """Sufficient finite-horizon initial-wealth loss bound, including full costs.

    The round-trip cost is reserved even before exit, so intermediate equity is
    at least the conservative wealth used in this inequality. Not a theorem for
    peak-to-trough drawdown, leverage, fills, or endogenous policy impact.
    """
    grid = np.asarray(grid)
    if len(gains) == 0:
        return grid == 0  # abstain; no certificate for a positive position
    bound = grid*shock_bound*max(gains)+cost(grid)
    return bound <= budget+1e-12


def log_scores(grid, terminal_changes, wealth=1000.):
    w = wealth+np.asarray(terminal_changes)[:,None]*grid-cost(grid)
    scores = np.full(w.shape,-np.inf)
    np.log(w/wealth,out=scores,where=w>0)
    return scores.mean(0)


def choose(grid, scores, allowed):
    if not np.any(allowed):
        raise ValueError("cash action must be available")
    return float(grid[np.argmax(np.where(allowed,scores,-np.inf))])


def summarize_account(a, inventory, budget):
    terminal=a['terminal']; positive=terminal>0
    logs=np.full(len(terminal),-np.inf)
    logs[positive]=np.log(terminal[positive]/1000.)
    losses=a['loss_from_initial']
    # Upper-tail empirical ES: average worst ceil(5% n) losses.
    k=max(1,int(np.ceil(.05*len(losses))))
    return dict(inventory=inventory,mean_log_wealth=float(logs.mean()),
                mean_net_pnl=float((terminal-1000).mean()),
                loss_es95=float(np.sort(losses)[-k:].mean()),
                mean_peak_drawdown=float(a['peak_drawdown'].mean()),
                budget_breach_rate=float(np.mean(losses>budget+1e-9)),
                bankruptcy_rate=float(np.mean(~positive)),
                round_trip_cost=float(cost(inventory)),
                accounting_max_error=a['accounting_error'])
