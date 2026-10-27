"""Load cached FY2000-FY2026 history (data/) and fit trend lines over 2000-2026."""
import json, math, openpyxl
import numpy as np

def _omb_row(path, label, col0_year=True):
    rows = list(openpyxl.load_workbook(path, data_only=True).active.iter_rows(values_only=True))
    return rows
r11 = _omb_row("data/omb_hist01z1_fy2027.xlsx", None)
REC, OUT = {}, {}
for r in r11:
    if r[0] and str(r[0]).isdigit() and 2000 <= int(r[0]) <= 2025:
        REC[int(r[0])] = r[1] / 1e6; OUT[int(r[0])] = r[2] / 1e6       # $T
r31 = _omb_row("data/omb_hist03z1_fy2027.xlsx", None)
hdr = r31[1]; ni_row = next(r for r in r31 if r[0] == "Net interest")
NI = {int(hdr[i]): ni_row[i] / 1e6 for i in range(1, len(hdr)) if hdr[i] and str(hdr[i]).isdigit() and 2000 <= int(hdr[i]) <= 2025}

# FY2026 (preliminary): CBO Monthly Budget Review Sep 2026 (~$5.4T receipts, ~$2.0T deficit);
# MTS Table 1 Year-to-Date through Sep 2026 and MTS Table 9 Net Interest FYTD used for the dollar series.
mts1 = json.load(open("data/mts1_sep.json"))["data"]
ytd = [x for x in mts1 if x["record_date"] == "2026-09-30" and x["classification_desc"] == "Year-to-Date"]
# Second Year-to-Date row is FY2026 (first is FY2025).
fy26 = ytd[1]
REC[2026] = float(fy26["current_month_gross_rcpt_amt"]) / 1e12
OUT[2026] = float(fy26["current_month_gross_outly_amt"]) / 1e12
mts9 = json.load(open("data/mts9_latest.json"))["data"]
ni26 = float(next(x for x in mts9 if x["classification_desc"] == "Net Interest" and x["record_date"] == "2026-09-30")["current_fytd_rcpt_outly_amt"]) / 1e12
NI[2026] = ni26
PRIM = {y: OUT[y] - REC[y] - NI[y] for y in REC}          # + = primary deficit, - = primary surplus

DEBT = {int(x["record_date"][:4]): float(x["debt_outstanding_amt"]) / 1e12
        for x in json.load(open("data/hist_debt_outstanding.json"))["data"] if 2000 <= int(x["record_date"][:4]) <= 2026}
RATE = {int(x["record_date"][:4]): float(x["avg_interest_rate_amt"])
        for x in json.load(open("data/hist_avg_rates_sep.json"))["data"]}   # Sep, Total Marketable, FY2001+
YEARS = list(range(2000, 2027))
IR = {y: NI[y] / REC[y] * 100 for y in YEARS}                              # historic net interest / receipts

def ols(x, y):
    x, y = np.array(x, float), np.array(y, float)
    b, a = np.polyfit(x, y, 1); yh = a + b * x
    r2 = 1 - ((y - yh) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return a, b, r2

aR, bR, r2R = ols(YEARS, [math.log(REC[y]) for y in YEARS]); gR = math.exp(bR) - 1
aD, bD, r2D = ols(YEARS, [math.log(DEBT[y]) for y in YEARS]); gD = math.exp(bD) - 1
aN, bN, r2N = ols(YEARS, [math.log(NI[y]) for y in YEARS]); gN = math.exp(bN) - 1
ry = sorted(RATE); ar, dr, r2r = ols(ry, [RATE[y] for y in ry])
sh = [PRIM[y] / REC[y] for y in YEARS]; aS, bS, r2S = ols(YEARS, sh)
FIT = dict(gR=gR, r2R=r2R, gD=gD, r2D=r2D, gN=gN, r2N=r2N, dr=dr, r2r=r2r, aS=aS, bS=bS, r2S=r2S,
           s2026_fit=aS + bS * 2026, s2026_act=PRIM[2026] / REC[2026],
           prim_sd=float(np.std([PRIM[y] for y in YEARS])), prim_min=min(PRIM.values()), prim_max=max(PRIM.values()),
           n_surplus=sum(1 for y in YEARS if PRIM[y] < 0))

if __name__ == "__main__":
    for y in YEARS:
        print(y, f"R {REC[y]:.3f} NI {NI[y]:.3f} P {PRIM[y]:+.3f} D {DEBT[y]:.2f} r {RATE.get(y,'-')} IR {IR[y]:.1f}")
    print(FIT)
