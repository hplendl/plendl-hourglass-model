#!/usr/bin/env python3
"""Predictive Hourglass Model - reconstructed recurrences.

Annual steps; each row = fiscal-year end (30 Sep). Row 0 = initialization.
  I_t   = D_t * r_t
  D_t+1 = D_t + I_t + P_t                 (P = primary deficit)
  R_t+1 = R_t * (1 + g_R_eff)
  M_t+1 = M_t * (1 + g_M_eff)
  P_t+1 = P_t * (1 + g_P_eff)
  r_t+1 = r_t + dr_eff
Accelerators are tested on year-t values and, once tripped, lock permanently and
apply to the step t -> t+1 and every later step:
  I/R > 25%          : +0.20 pp g_P, +0.20 pp g_M, +3 bp dr
  I > R - M (displ.) : +1.50 pp g_P, +15 bp dr, -0.50 pp g_R
  I/R > 30%          : +0.50 pp g_P, +0.50 pp g_M, +5 bp dr
  I/R > 40%          : +1.00 pp g_P, +1.00 pp g_M, +10 bp dr
  I/R > 50% & D>$60T : marker only (severe block already on from 40%)
  I > R              : marker only
"""
from dataclasses import dataclass, field, replace

@dataclass
class Params:
    D0: float; r0: float; R0: float; P0: float; M0: float   # $T, r0 in percent
    gR: float = 4.5; gP: float = 6.0; gM: float = 6.1          # percent
    dr: float = 0.18                                         # pp per year
    M_displ0: float = None      # alt mandatory base for displacement test only
    acc: dict = field(default_factory=lambda: {
        "25": (0.20, 0.20, 0.03, 0.0),     # (gP, gM, dr, gR) adders
        "displ": (1.50, 0.0, 0.15, -0.50),
        "30": (0.50, 0.50, 0.05, 0.0),
        "40": (1.00, 1.00, 0.10, 0.0),
    })
    first: int = 2026; last: int = 2045

def run(p: Params):
    D, r, R, P, M = p.D0, p.r0, p.R0, p.P0, p.M0
    Md = p.M_displ0 if p.M_displ0 is not None else None
    locked, rows, cross = set(), [], {}
    for yr in range(p.first, p.last + 1):
        I = D * r / 100
        Mtest = Md if Md is not None else M
        ir = I / R * 100
        tests = {"25": ir > 25, "displ": I > R - Mtest, "30": ir > 30, "40": ir > 40,
                 "50": ir > 50, "60T": D > 60, "50&60": ir > 50 and D > 60,
                 "MgtR": M > R, "IgtR": I > R}
        flags = []
        for k, hit in tests.items():
            if hit and k not in cross:
                cross[k] = yr
                flags.append(k)
            if hit and k in p.acc:
                locked.add(k)
        rows.append(dict(year=yr, D=D, I=I, R=R, M=M, P=P, r=r, ir=ir,
                         displ=I - (R - M), flags=flags))
        gP, gM, gR, dr = p.gP, p.gM, p.gR, p.dr
        for k in locked:
            a = p.acc[k]
            gP += a[0]; gM += a[1]; dr += a[2]; gR += a[3]
        D = D + I + P
        R *= 1 + gR / 100; M *= 1 + gM / 100; P *= 1 + gP / 100; r += dr
        if Md is not None:
            Md *= 1 + gM / 100
    return rows, cross

def interp_cross(rows, key):
    """Fractional crossing between fiscal-year-end rows (linear). Returns (year, frac)."""
    f = {"40": lambda x: x["ir"] - 40, "50": lambda x: x["ir"] - 50, "30": lambda x: x["ir"] - 30,
         "60T": lambda x: x["D"] - 60, "IgtR": lambda x: x["I"] - x["R"]}[key]
    for a, b in zip(rows, rows[1:]):
        if f(a) <= 0 < f(b):
            return a["year"], -f(a) / (f(b) - f(a))
    return None

def frac_to_month(year, frac):
    import datetime as dt
    d0 = dt.date(year, 9, 30)
    d = d0 + dt.timedelta(days=round(frac * 365.25))
    return d

OCT5 = Params(D0=40.24244661920933, r0=3.490, R0=5.40, P0=1.10, M0=4.90, dr=0.18)

if __name__ == "__main__":
    rows, cross = run(OCT5)
    for x in rows:
        print(x["year"], *[f"{x[k]:.2f}" for k in "D I R M P r".split()], f"{x['ir']:.1f}", f"{x['displ']:.2f}", x["flags"])
    print(cross)


# ---------------------------------------------------------------------------
# Trend-line model (14 Oct 2026 onward). Replaces the accelerator/threshold
# logic above for reporting. The functions above are kept only so older run
# scripts still reproduce their outputs.
#
# The model runs the values. Historic trend lines are measured, then extended
# by fixed recurrences under pure status-quo inertia, in nominal
# (inflation-inclusive) terms, at monthly steps:
#   I_t     = D_t * r_t                      (annualized interest flow)
#   D_t+1   = D_t + (I_t + P_t) / 12
#   R_t+1   = R_t * (1 + g_R)^(1/12)
#   P_t+1   = P_t * (1 + g_P)^(1/12)
#   r_t+1   = r_t + dr / 12
#   q_t     = I_t / R_t                      (interest-to-revenue ratio)
#
# Paradigm-shift test ("the trend line turns parabolic"):
#   g_q(t)  = ln q_t+1 - ln q_t  = growth of interest minus growth of revenue
#   a(t)    = g_q(t) - g_q(t-1)  (acceleration of the ratio's growth)
#   The shift is the first month t* such that, for every month from t* to
#   the end of the computation horizon, BOTH
#     (1) g_q(t) > 0   : interest grows faster than revenue, and
#     (2) a(t)  > 0    : that excess growth is itself accelerating
#                        (d^2 ln q / dt^2 > 0, i.e. faster than exponential).
#   Before t*, the ratio rises but its growth rate is fading; from t* on the
#   ratio compounds at a rising rate. Reference lines (25/30/40%) play no part.
# ---------------------------------------------------------------------------
import math, datetime as _dt

@dataclass
class Trend:
    D0: float; r0: float; R0: float; P0: float    # $T and percent
    gR: float; gP: float; dr: float               # annual: fraction, fraction, pp/yr
    start: _dt.date = _dt.date(2026, 10, 1)
    months: int = 12 * 40                         # computation horizon

def _add_months(d, m):
    y, mo = divmod(d.month - 1 + m, 12)
    return _dt.date(d.year + y, mo + 1, 1)

def run_trend(t: Trend):
    D, r, R, P = t.D0, t.r0, t.R0, t.P0
    mR, mP = (1 + t.gR) ** (1 / 12), (1 + t.gP) ** (1 / 12)
    rows = []
    for m in range(t.months):
        I = D * r / 100
        rows.append(dict(month=_add_months(t.start, m), D=D, I=I, R=R, P=P, r=r, q=I / R * 100))
        D += (I + P) / 12; R *= mR; P *= mP; r += t.dr / 12
    for i, x in enumerate(rows):
        x["gq"] = math.log(rows[i + 1]["q"] / x["q"]) * 12 if i + 1 < len(rows) else None  # annualized
        x["acc"] = (x["gq"] - rows[i - 1]["gq"]) if (i > 0 and x["gq"] is not None) else None
    return rows

def paradigm_shift(rows):
    ev = [x for x in rows if x["acc"] is not None]
    for i, x in enumerate(ev):
        if all(y["gq"] > 0 and y["acc"] > 0 for y in ev[i:]):
            return x
    return None


# ---------------------------------------------------------------------------
# 2000+ lookback variant (sample2): primary deficit carried as a share of
# revenue, s_t, which moves along its fitted linear trend (handles the sign
# changes in FY2000-FY2026); P_t = s_t * R_t. Interest on a net-interest basis.
#   I_t = D_t * r_t ; D_t+1 = D_t + (I_t + s_t R_t)/12 ; R_t+1 = R_t (1+g_R)^(1/12)
#   s_t+1 = s_t + b_s/12 ; r_t+1 = r_t + dr/12
# ---------------------------------------------------------------------------
@dataclass
class Trend2:
    D0: float; r0: float; R0: float; s0: float
    gR: float; bs: float; dr: float
    start: _dt.date = _dt.date(2026, 10, 1)
    months: int = 12 * 40

def run_trend2(t: Trend2):
    D, r, R, s = t.D0, t.r0, t.R0, t.s0
    mR = (1 + t.gR) ** (1 / 12)
    rows = []
    for m in range(t.months):
        I = D * r / 100
        rows.append(dict(month=_add_months(t.start, m), D=D, I=I, R=R, P=s * R, s=s, r=r, q=I / R * 100))
        D += (I + s * R) / 12; R *= mR; s += t.bs / 12; r += t.dr / 12
    for i, x in enumerate(rows):
        ok = i + 1 < len(rows) and x["q"] > 0 and rows[i + 1]["q"] > 0
        x["gq"] = math.log(rows[i + 1]["q"] / x["q"]) * 12 if ok else None
        x["acc"] = (x["gq"] - rows[i - 1]["gq"]) if (i > 0 and x["gq"] is not None and rows[i - 1]["gq"] is not None) else None
    return rows

def paradigm_shift2(rows):
    """Same test as paradigm_shift; months where q <= 0 (no defined growth) count as failing."""
    tail = rows[1:-1]
    for i, x in enumerate(tail):
        if all(y["acc"] is not None and y["gq"] > 0 and y["acc"] > 0 for y in tail[i:]):
            return x
    return None
