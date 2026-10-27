"""Assemble the fiscal-year history used by the model from raw FRED observations."""
import math, datetime as dt
from statistics import mean

def _byyear(obs, scale):
    return {int(d[:4]): v * scale for d, v in obs}

def build_history(raw, first=2000):
    """Return dict of yearly series ($T) and metadata. Fiscal year ends 30 Sep."""
    REC = _byyear(raw["FYFR"], 1e-6); OUT = _byyear(raw["FYONET"], 1e-6)
    NI = _byyear(raw["FYOINT"], 1e-6); FYGFD = _byyear(raw["FYGFD"], 1e-3)
    # Debt: one consistent concept for every year = Treasury Debt to the Penny, last record of each
    # fiscal year (on or before 30 Sep). FYGFD (OMB gross federal debt) is kept for reference only.
    DEBT, DEBT_DATE = {}, {}
    for d, v in raw["DEBT_TO_PENNY"]:
        if d[5:7] == "09":
            DEBT[int(d[:4])] = v * 1e-12; DEBT_DATE[int(d[:4])] = d
    last = max(y for y in REC if y in OUT and y in NI and y in DEBT)
    est = set()
    notes = []
    # Preliminary next FY from 12 months of Monthly Treasury Statement data, if complete.
    fy = last + 1
    months = [f"{fy-1}-{m:02d}-01" for m in (10, 11, 12)] + [f"{fy}-{m:02d}-01" for m in range(1, 10)]
    mr, mo = dict(raw["MTSR133FMS"]), dict(raw["MTSO133FMS"])
    if all(m in mr and m in mo for m in months):
        REC[fy] = sum(mr[m] for m in months) * 1e-6
        OUT[fy] = sum(mo[m] for m in months) * 1e-6
        # Net interest FY(prelim): scale last official FY by growth of NIPA interest payments
        # (latest 4 quarters vs the 4 quarters before). Approximation; documented in README.
        q = raw["A091RC1Q027SBEA"]
        g = mean(v for _, v in q[-4:]) / mean(v for _, v in q[-8:-4])
        NI[fy] = NI[last] * g; est.add(fy)
        notes.append(f"FY{fy} receipts and outlays are actuals (sum of the 12 monthly MTS values, Oct {fy-1}-Sep {fy}). "
                     f"FY{fy} net interest (*) is an ESTIMATE until FRED's FYOINT posts FY{fy}: FY{last} x {g:.4f} "
                     f"(growth of NIPA interest payments, last 4 vs prior 4 quarters, through {q[-1][0]}).")
        last = fy
    years = list(range(first, last + 1))
    PRIM = {y: OUT[y] - REC[y] - NI[y] for y in years}
    RATE = {y: NI[y] / ((DEBT[y - 1] + DEBT[y]) / 2) * 100 for y in years if y - 1 in DEBT}
    IR = {y: NI[y] / REC[y] * 100 for y in years}
    dtp = raw["DEBT_TO_PENNY"][-1]
    notes.append(f"Debt (all years) = Treasury Debt to the Penny at fiscal-year end; FY{last}: ${DEBT[last]:.3f} T ({DEBT_DATE[last]}). "
                 f"Starting debt D0 = latest Debt to the Penny, ${dtp[1]*1e-12:.3f} T ({dtp[0]}). "
                 f"For reference, FRED GFDEBTN latest = ${raw['GFDEBTN'][-1][1]*1e-6:.3f} T ({raw['GFDEBTN'][-1][0]}, quarter start date) "
                 f"and FYGFD FY{max(FYGFD)} = ${FYGFD[max(FYGFD)]:.3f} T (OMB concept).")
    return dict(years=years, REC=REC, OUT=OUT, NI=NI, DEBT=DEBT, PRIM=PRIM, RATE=RATE, IR=IR, FYGFD=FYGFD,
                last=last, est=est, notes=notes, D0=dtp[1] * 1e-12, D0_date=dtp[0])

def context(raw):
    """Observed context series (not inputs to the recurrence)."""
    cur = raw["CURRCIR"]; nipa_i = dict(raw["A091RC1Q027SBEA"]); nipa_r = dict(raw["FGRECPT"])
    qs = sorted(set(nipa_i) & set(nipa_r))
    yoy = (cur[-1][1] / next(v for d, v in reversed(cur) if d <= f"{int(cur[-1][0][:4])-1}{cur[-1][0][4:]}") - 1) * 100
    return dict(currcir=cur, currcir_last=cur[-1], currcir_yoy=yoy,
                nipa_ratio=[(d, nipa_i[d] / nipa_r[d] * 100) for d in qs],
                nipa_last=(qs[-1], nipa_i[qs[-1]], nipa_r[qs[-1]]))
