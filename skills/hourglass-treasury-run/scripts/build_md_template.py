"""Sample2: trend lines fitted over FY2000-FY2026; projection, parabolic test, chart, report, thread."""
import datetime as dt
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dataclasses import replace
from hist_2000 import *
from model import Trend2, run_trend2, paradigm_shift2
METHOD = ("This exercise calculates values from measured historic trend lines and extends them into new projected "
          "trends under pure status-quo inertia. Using the fixed recurrence relations, future values of every variable "
          "are obtained at successive points and moments in time. The moment the mathematics reveals a paradigm shift is "
          "the moment the calculated trend lines become parabolic - the location at which interest growth outruns "
          "revenue growth, even in nominal terms that already include inflation. Threshold markers are reference lines "
          "only; the shift is defined solely by the calculated trajectory.")
CAPTION = ("Values are calculated from historic trend lines extended into projected trends. The paradigm-shift point "
           "is the calculated moment at which the trend lines become parabolic.")

import os
RUNDATE = dt.date.fromisoformat(os.environ["HG_RUN_DATE"])
TAG = f"Predictive_Hourglass_{RUNDATE.isoformat()}"
import json as _j
_dtp = _j.load(open("data/dtp_latest.json"))["data"][0]
D0 = float(_dtp["tot_pub_debt_out_amt"]) / 1e12; DDATE = dt.date.fromisoformat(_dtp["record_date"])
r0 = NI[2026] / ((DEBT[2025] + DEBT[2026]) / 2) * 100            # effective net-interest rate FY2026
dr21 = ols(range(2021, 2027), [RATE[y] for y in range(2021, 2027)])[1]
BASE = Trend2(D0=D0, r0=r0, R0=REC[2026], s0=FIT["s2026_act"], gR=gR, bs=bS, dr=dr)
CASES = {"Case A: all trend lines fitted 2000-2026": BASE,
         "Case B: rate held at FY2026 level (dr = 0)": replace(BASE, dr=0.0),
         f"Case C: rate slope fitted 2021-2026 only (+{dr21:.3f} pp/yr)": replace(BASE, dr=dr21)}
RUN = {k: run_trend2(v) for k, v in CASES.items()}
SH = {k: paradigm_shift2(v) for k, v in RUN.items()}
rows = RUN[next(iter(RUN))]; shift = SH[next(iter(SH))]
END = rows[-1]["month"].strftime("%B %Y")
fmt = lambda s: f"{s['month']:%B %Y} (I/R {s['q']:.1f}%)" if s else f"None through {END}"

# chart
fig, ax = plt.subplots(figsize=(12, 6.75), dpi=130)
ax.plot([dt.date(y, 9, 30) for y in YEARS], [IR[y] for y in YEARS], color="#444", lw=2.2, marker="o", ms=3,
        label="Historic actual, FY2000-FY2026 (net interest / receipts)")
styles = [("#1f2a44", "-", 1.8), ("#2e7d32", "-", 1.8), ("#b03a2e", "-", 1.8)]
for (k, rw), (c, ls, lw) in zip(RUN.items(), styles):
    cut = [x for x in rw if x["month"].year <= 2045]
    ax.plot([x["month"] for x in cut], [x["q"] for x in cut], color=c, ls=ls, lw=lw, label=f"Projected: {k}")
    s = SH[k]
    if s and s["month"].year <= 2045:
        ax.axvline(s["month"], color=c, lw=1, alpha=.7)
        ax.annotate(f"Paradigm-shift point (calculated): {s['month']:%B %Y}, I/R {s['q']:.1f}%", (s["month"], s["q"]),
                    xytext=(-330, 40), textcoords="offset points", fontsize=9, color=c, arrowprops=dict(arrowstyle="->", color=c))
for lv, c, dy in ((25, "#999", -5), (30, "#777", 1), (40, "#555", 1)):
    ax.axhline(lv, ls=":", lw=1, color=c); ax.text(dt.date(2000, 6, 1), lv + dy, f"{lv}% reference line", fontsize=8.5, color=c)
ax.axvline(dt.date(2026, 10, 1), color="#999", lw=.8); ax.text(dt.date(2026, 12, 1), 145, "projection ->", fontsize=8.5, color="#777")
ax.set_ylim(0, 160); ax.set_xlim(dt.date(1999, 6, 1), dt.date(2046, 1, 1))
ax.set_ylabel("Interest / revenue, % (nominal)"); ax.grid(alpha=.3); ax.legend(loc="upper left", fontsize=8.5)
ax.set_title("Predictive Hourglass Model - trend lines fitted FY2000-FY2026, projected to 2045")
fig.text(0.5, 0.01, CAPTION, ha="center", fontsize=9.5, style="italic")
fig.subplots_adjust(bottom=0.11); fig.savefig(f"{TAG}_chart.png"); plt.close(fig)

hist = ["| FY | Receipts $T | Outlays $T | Net interest $T | Primary deficit $T | Gross debt $T | Avg marketable rate % (Sep) | I/R % |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for y in YEARS:
    hist.append(f"| {y}{' (prelim.)' if y == 2026 else ''} | {REC[y]:.3f} | {OUT[y]:.3f} | {NI[y]:.3f} | {PRIM[y]:+.3f} | {DEBT[y]:.2f} | "
                f"{RATE[y]:.3f} |".replace("| - |", "| n/a |") + f" {IR[y]:.1f} |" if y in RATE else
                f"| {y} | {REC[y]:.3f} | {OUT[y]:.3f} | {NI[y]:.3f} | {PRIM[y]:+.3f} | {DEBT[y]:.2f} | n/a | {IR[y]:.1f} |")
names = list(RUN)
proj = ["| Point in time | Debt $T | Interest $T | Revenue $T | Primary deficit $T | Rate % | I/R % Case A | I/R % Case B | I/R % Case C |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for i in range(0, 12 * 30, 12):
    x = rows[i]
    proj.append(f"| {x['month']:%b %Y} | {x['D']:.2f} | {x['I']:.2f} | {x['R']:.2f} | {x['P']:+.2f} | {x['r']:.2f} | {x['q']:.1f} | "
                f"{RUN[names[1]][i]['q']:.1f} | {RUN[names[2]][i]['q']:.1f} |")
sens = ["| Case | Calculated paradigm-shift point |", "| --- | --- |"] + [f"| {k} | {fmt(SH[k])} |" for k in names]
gq_c = [x["gq"] for x in rows if x["gq"] is not None]
first_neg = next((x for x in rows if x["q"] <= 0), None)

md = f"""# Predictive Hourglass Model - Trend-Line Run, 2000+ Lookback

Run date: {RUNDATE.day} {RUNDATE:%B %Y}. Trend lines fitted over FY2000-FY2026. Projection starts 1 October 2026.

## Methodology

{METHOD}

The model runs the values: historic trend lines are measured, extended by calculation into future projected trends, and the resulting figures at each point and moment in time are reported without narrative.

### Historic data, FY2000-FY2026

{chr(10).join(hist)}

Primary deficit = outlays - receipts - net interest (negative = primary surplus). I/R = net interest / receipts. FY2026 is marked preliminary pending final audited figures: receipts $5.403 T, outlays $7.396 T and deficit $1.992 T from the Monthly Treasury Statement Table 1 Year-to-Date through September 2026 (CBO Monthly Budget Review for September 2026 reported about $5.4 T receipts and a $2.0 T deficit); net interest $1.052 T from MTS Table 9 FYTD through September 2026. The Average Interest Rates dataset begins in FY2001, so the rate fit uses FY2001-FY2026.

### Fitted trend lines (OLS over FY2000-FY2026)

| Series | Fit | Fitted parameter | R^2 |
| --- | --- | --- | --- |
| Receipts | log-linear (CAGR) | {gR*100:.2f}% per year | {r2R:.3f} |
| Gross debt | log-linear (CAGR), reference only | {gD*100:.2f}% per year | {r2D:.3f} |
| Net interest | log-linear (CAGR), reference only | {gN*100:.2f}% per year | {r2N:.3f} |
| Average rate, total marketable (Sep) | linear OLS, FY2001-FY2026 | {dr:+.4f} pp per year | {r2r:.3f} |
| Primary deficit as share of receipts | linear OLS | {bS*100:+.3f} pp of receipts per year (fitted FY2026 level {FIT['s2026_fit']*100:.1f}%, actual {FIT['s2026_act']*100:.1f}%) | {r2S:.3f} |

Primary deficit handling: the dollar series changes sign ({FIT['n_surplus']} primary-surplus years, range {FIT['prim_min']:+.3f} to {FIT['prim_max']:+.3f} $T, standard deviation {FIT['prim_sd']:.3f} $T), so a log-linear or CAGR fit is undefined. It is fitted as a share of receipts with linear OLS, which accepts negative values and scales with the revenue trend. The projection starts from the FY2026 actual share ({FIT['s2026_act']*100:.1f}%) and moves along the fitted slope, so there is no jump to the fitted level at the start. Projected primary deficit = share x projected receipts.

Rate handling: the marketable average rate falls from 5.82% (FY2001) to 1.47% (FY2021) and rises to 3.52% (FY2026). A straight line over the full window has a negative slope and a low R^2. The three cases are reported with equal standing and differ only in the rate trend line: Case A uses the full-window slope as fitted, Case B holds the rate at its FY2026 level, Case C uses the slope fitted over FY2021-FY2026. The debt, interest, revenue and primary-deficit columns in the table are Case A.

### Recurrence relations (monthly steps, nominal, net-interest basis)

- I_t = D_t x r_t, where r_0 = FY2026 net interest / average gross debt FY2025-FY2026 = {r0:.3f}% (matches the historic I/R basis)
- D_t+1 = D_t + (I_t + s_t x R_t) / 12, with D_0 = ${D0:.3f} T (Debt to the Penny, {DDATE:%d %b %Y})
- R_t+1 = R_t x (1 + g_R)^(1/12), with R_0 = ${REC[2026]:.3f} T
- s_t+1 = s_t + b_s / 12
- r_t+1 = r_t + dr / 12
- q_t = I_t / R_t

## Calculated values (yearly points, 1 October)

{chr(10).join(proj)}

{"In Case A the calculated ratio reaches zero in " + first_neg['month'].strftime('%B %Y') + ", because the fitted rate line reaches zero." if first_neg else ""}

## Chart

![Interest-to-revenue ratio]({TAG}_chart.png)

*{CAPTION}* The 25%, 30% and 40% lines are reference lines only.

## Sources

- OMB Historical Tables, FY2027 Budget, Table 1.1 (receipts, outlays, FY2000-FY2025) and Table 3.1 (net interest): https://www.govinfo.gov/app/collection/budget/2027/BUDGET-2027-TAB
- Treasury Fiscal Data, Historical Debt Outstanding (gross debt at 30 September, FY2000-FY2026): https://fiscaldata.treasury.gov/datasets/historical-debt-outstanding/
- Treasury Fiscal Data, Average Interest Rates on U.S. Treasury Securities (Total Marketable, September, FY2001-FY2026): https://fiscaldata.treasury.gov/datasets/average-interest-rates-treasury-securities/
- Treasury Fiscal Data, Debt to the Penny ({DDATE:%d %B %Y}): https://fiscaldata.treasury.gov/datasets/debt-to-the-penny/
- Treasury Fiscal Data, Monthly Treasury Statement Table 1 and Table 9 (FY2026 through September 2026): https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/
- CBO, Monthly Budget Review: September 2026 (FY2026 receipts and deficit, preliminary cross-check): https://www.cbo.gov/publication/61985

## Status of the work

Published series at stated vintages. Recurrences are accounting identities extended along fitted trend lines; no policy change, feedback adder or overlay is applied. Values are nominal and include inflation. Not a Treasury, Federal Reserve, or CBO product. Not investment, budget, or policy advice.

## Calculated paradigm-shift point

{chr(10).join(sens)}

Run date: {RUNDATE.day} {RUNDATE:%B %Y}. Data: Debt to the Penny {DDATE:%d %b %Y}; Average Interest Rates through September 2026; MTS through September 2026.

Test used: g_q(t) = 12 x ln(q_t+1 / q_t), the annualized growth of interest minus the growth of revenue, and a(t) = g_q(t) - g_q(t-1), the second derivative of ln q. The paradigm-shift point is the first month from which, for every remaining month of the 40-year computation horizon (October 2026 to {END}), both g_q(t) > 0 and a(t) > 0. Months with a non-positive ratio fail the test.
"""
open(f"{TAG}.md", "w").write(md)

c, f_, l_ = (SH[k] for k in names)
y = lambda rw, yr: next(x for x in rw if x["month"] == dt.date(yr, 10, 1))["q"]
A, B, C = (RUN[k] for k in names)
sm = lambda s: f"{s['month']:%b %Y} (I/R {s['q']:.1f}%)" if s else "none through 2066"
posts = [
f"""1/5 Predictive Hourglass Model, run {RUNDATE.day} {RUNDATE:%b %Y}.

Gross debt: ${D0:.3f}T ({DDATE:%d %b}).
Interest-to-revenue (net interest / receipts): {IR[2000]:.1f}% in FY2000, {IR[2021]:.1f}% in FY2021, {IR[2026]:.1f}% in FY2026 (prelim.).""",
f"""2/5 Trend lines fitted FY2000-FY2026:
- Receipts {gR*100:+.2f}%/yr
- Gross debt {gD*100:+.2f}%/yr
- Primary deficit {bS*100:+.2f} pp of receipts/yr
- Avg marketable rate {dr:+.3f} pp/yr
Three cases differ only in the rate trend.""",
f"""3/5 The model projects I/R at 1 Oct 2030 / 2035 / 2045:
- A, full 2000-26 rate fit: {y(A,2030):.1f}% / {y(A,2035):.1f}% / {y(A,2045):.1f}%
- B, rate flat: {y(B,2030):.1f}% / {y(B,2035):.1f}% / {y(B,2045):.1f}%
- C, 2021-26 rate fit: {y(C,2030):.1f}% / {y(C,2035):.1f}% / {y(C,2045):.1f}%
Chart attached.""",
f"""4/5 Paradigm-shift point (I/R growth positive and accelerating every month after):
- A: {sm(c)}
- B: {sm(f_)}
- C: on this trend, {sm(l_)}
25/30/40% are reference lines only.""",
"""5/5 The model runs the values: historic trend lines are measured, extended by calculation into future projected trends, and the resulting figures at each point and moment in time are reported without narrative.""",
]
open(f"posts_{RUNDATE.isoformat()}.py", "w").write("posts = " + repr(posts) + "\n")
for i, p in enumerate(posts): assert p.isascii() and len(p) <= 280, (i, len(p), p)
assert md.isascii()
low = (md + " ".join(posts)).lower()
for w in ("crisis", "collapse", "hyperinflation", "breaks", "breach", "runaway", "educated guess", "dramatic"):
    assert w not in low, w
import json as _J
_J.dump({"run_date": RUNDATE.isoformat(), "tag": TAG, "dtp_date": DDATE.isoformat(), "D0": D0, "r0": r0,
 "fits": {k: float(v) for k, v in FIT.items()}, "dr21": dr21, "cases": {k: {"shift": (f"{v['month']:%Y-%m}" if v else None), "shift_q": (v["q"] if v else None),
 "q2030": y(RUN[k],2030), "q2035": y(RUN[k],2035), "q2045": y(RUN[k],2045)} for k, v in SH.items()}, "posts": posts}, open("build_result.json","w"), indent=1, default=str)
print({k: fmt(v) for k, v in SH.items()}, [len(p) for p in posts])
