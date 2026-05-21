#!/usr/bin/env python3
"""
wall_clock_mle_vs_closed_form.py
=================================
Compares median wall-clock time (milliseconds) between:
  (A) Maximum Likelihood Estimation (MLE) via scipy's iterative optimizer
  (B) Closed-form PWM / L-moment inversion (non-iterative, rank-based)

for the Weibull distribution with shape alpha=2, scale beta=1.

This script supplements Table 9 in the paper:
  "Elementary and Robust Distribution Shape Analysis via Mean Absolute
   Deviations and Quantile-Based Quadrature Approximations"
   Pinsky, Kundu, Kaur — JETA 2026.

Machine metadata is printed to stdout and saved in wall_clock_mle_vs_closed_form.csv.

USAGE
    python wall_clock_mle_vs_closed_form.py

REQUIREMENTS
    pip install numpy scipy pandas
"""

import time
import platform
import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import gamma as Gamma
from math import comb


# ── Experiment parameters (match paper Table 9) ────────────────────────
ALPHA_TRUE  = 2.0          # Weibull shape
BETA_TRUE   = 1.0          # Weibull scale
N_TRIALS    = 30           # number of independent samples per n
SEED        = 0            # random seed
N_VALUES    = [100, 200, 500, 1000, 2000, 5000]


# ── PWM / L-moment closed-form Weibull inversion ───────────────────────
def pwm_b_r(x: np.ndarray, r: int) -> float:
    """Unbiased probability weighted moment b_r (Hosking 1990)."""
    x_sorted = np.sort(x)
    n = len(x_sorted)
    s = sum(comb(j, r) / comb(n - 1, r) * x_sorted[j] for j in range(r, n))
    return s / n


def lmom_weibull_fit(x: np.ndarray):
    """
    Closed-form Weibull parameter estimation via L-moments.
    Returns (alpha_hat, beta_hat).

    Formulas (Hosking 1990):
      l1 = b0 = mean(x)
      l2 = 2*b1 - b0
      tau2 = l2 / l1
      alpha_hat = -ln(2) / ln(1 - tau2)     [closed-form inversion]
      beta_hat  = l1 / Gamma(1 + 1/alpha_hat)
    """
    b0 = pwm_b_r(x, 0)   # = l1
    b1 = pwm_b_r(x, 1)
    l1 = b0
    l2 = 2.0 * b1 - b0
    tau2 = l2 / l1
    if tau2 <= 0 or tau2 >= 1:
        return float('nan'), float('nan')
    import math
    alpha_hat = -math.log(2) / math.log(1.0 - tau2)
    beta_hat  = l1 / Gamma(1.0 + 1.0 / alpha_hat)
    return alpha_hat, beta_hat


# ── Timing helper ──────────────────────────────────────────────────────
def time_method(fn, *args, n_reps: int = 5) -> float:
    """Return median wall-clock time in milliseconds over n_reps calls."""
    times = []
    for _ in range(n_reps):
        t0 = time.perf_counter()
        fn(*args)
        times.append((time.perf_counter() - t0) * 1000.0)
    return float(np.median(times))


# ── MLE wrapper ────────────────────────────────────────────────────────
def mle_weibull_fit(x: np.ndarray):
    """MLE via scipy weibull_min.fit with fixed location = 0."""
    c, loc, scale = stats.weibull_min.fit(x, floc=0)
    return c, scale   # alpha, beta


# ── Main ───────────────────────────────────────────────────────────────
rng = np.random.default_rng(SEED)
records = []

print(f"{'n':>6}  {'MLE median (ms)':>17}  {'Closed-form median (ms)':>24}  {'Speedup':>8}")
print("-" * 65)

for n in N_VALUES:
    mle_times   = []
    lmom_times  = []

    for _ in range(N_TRIALS):
        x = rng.weibull(ALPHA_TRUE, n) * BETA_TRUE

        t_mle  = time_method(mle_weibull_fit,   x, n_reps=3)
        t_lmom = time_method(lmom_weibull_fit,  x, n_reps=3)

        mle_times.append(t_mle)
        lmom_times.append(t_lmom)

    med_mle  = float(np.median(mle_times))
    med_lmom = float(np.median(lmom_times))
    speedup  = med_mle / med_lmom if med_lmom > 0 else float('inf')

    records.append(dict(n=n, mle_ms=round(med_mle, 4),
                        lmom_ms=round(med_lmom, 4),
                        speedup=round(speedup, 2)))
    print(f"{n:>6}  {med_mle:>17.4f}  {med_lmom:>24.4f}  {speedup:>8.2f}x")

# ── Machine metadata ───────────────────────────────────────────────────
meta = dict(
    python_version = platform.python_version(),
    platform       = platform.platform(),
    processor      = platform.processor(),
    alpha_true     = ALPHA_TRUE,
    beta_true      = BETA_TRUE,
    n_trials       = N_TRIALS,
    seed           = SEED,
)
print()
print("Machine metadata:")
for k, v in meta.items():
    print(f"  {k}: {v}")

# ── Save CSV ───────────────────────────────────────────────────────────
df = pd.DataFrame(records)
for k, v in meta.items():
    df[k] = v

df.to_csv("wall_clock_mle_vs_closed_form.csv", index=False)
print("\nSaved: wall_clock_mle_vs_closed_form.csv")
print("\nNOTE: Timings are machine-specific.")
print("Re-run this script on your hardware to obtain reproducible results.")
