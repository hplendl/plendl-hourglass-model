"""Plendl Hourglass Model - trend-line recurrences (pure math, no I/O).

Monthly steps, nominal dollars, net-interest basis:
  I_t   = D_t * r_t                     interest (annualized flow)
  D_t+1 = D_t + (I_t + s_t * R_t) / 12  debt grows by interest + primary deficit
  R_t+1 = R_t * (1 + g_R)^(1/12)        revenue on its fitted growth trend
  s_t+1 = s_t + b_s / 12                primary deficit as a share of revenue, linear trend
  r_t+1 = r_t + dr / 12                 effective rate, linear trend
  q_t   = I_t / R_t                     interest-to-revenue ratio (the "neck")
Paradigm-shift point: first month t* such that for every later month in the
horizon g_q = 12*ln(q_t+1/q_t) > 0 AND a = g_q(t) - g_q(t-1) > 0.
"""
import math, datetime as dt
from dataclasses import dataclass
import numpy as np

@dataclass
class Trend:
    D0: float; r0: float; R0: float; s0: float     # $T, %, $T, fraction
    gR: float; bs: float; dr: float                # fraction/yr, fraction/yr, pp/yr
    start: dt.date = dt.date(2026, 10, 1)
    months: int = 12 * 40

def add_months(d, m):
    y, mo = divmod(d.month - 1 + m, 12)
    return dt.date(d.year + y, mo + 1, 1)

def run(t: Trend):
    D, r, R, s = t.D0, t.r0, t.R0, t.s0
    mR = (1 + t.gR) ** (1 / 12)
    rows = []
    for m in range(t.months):
        I = D * r / 100
        rows.append(dict(month=add_months(t.start, m), D=D, I=I, R=R, P=s * R, s=s, r=r, q=I / R * 100))
        D += (I + s * R) / 12; R *= mR; s += t.bs / 12; r += t.dr / 12
    for i, x in enumerate(rows):
        ok = i + 1 < len(rows) and x["q"] > 0 and rows[i + 1]["q"] > 0
        x["gq"] = math.log(rows[i + 1]["q"] / x["q"]) * 12 if ok else None
        x["acc"] = (x["gq"] - rows[i - 1]["gq"]) if (i > 0 and x["gq"] is not None and rows[i - 1]["gq"] is not None) else None
    return rows

def paradigm_shift(rows):
    """Months with a non-positive ratio (undefined growth) count as failing."""
    tail = rows[1:-1]
    ok = [y["acc"] is not None and y["gq"] > 0 and y["acc"] > 0 for y in tail]
    # first index from which all remaining are True
    idx = None
    for i in range(len(ok) - 1, -1, -1):
        if ok[i]:
            idx = i
        else:
            break
    return tail[idx] if idx is not None else None

def ols(x, y):
    x, y = np.array(x, float), np.array(y, float)
    b, a = np.polyfit(x, y, 1); yh = a + b * x
    r2 = 1 - ((y - yh) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return a, b, r2

def first_cross(rows, level):
    return next((x for x in rows if x["q"] >= level), None)
