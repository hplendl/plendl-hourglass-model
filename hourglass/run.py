"""CLI: python -m hourglass.run --out outputs/latest"""
import argparse, csv, datetime as dt, json, math, os
from dataclasses import replace
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from . import fred, __version__
from .data import build_history, context
from .model import Trend, run, paradigm_shift, ols, first_cross
from .report import write_pdf

def main(argv=None):
    ap = argparse.ArgumentParser(description="Plendl Hourglass Model (FRED edition)")
    ap.add_argument("--out", default="outputs/latest"); ap.add_argument("--first", type=int, default=2000)
    ap.add_argument("--years", type=int, default=40)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    today = dt.date.today()
    raw = fred.fetch_all()
    H = build_history(raw, a.first); C = context(raw)
    Y = H["years"]; L = H["last"]
    with open(os.path.join(a.out, "fred_raw.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["series_id", "date", "value"])
        for s, obs in raw.items():
            for d, v in obs:
                w.writerow([s, d, v])
    # --- fits
    _, bR, r2R = ols(Y, [math.log(H["REC"][y]) for y in Y]); gR = math.exp(bR) - 1
    _, bD, r2D = ols(Y, [math.log(H["DEBT"][y]) for y in Y])
    ry = [y for y in Y if y in H["RATE"]]; _, dr, r2r = ols(ry, [H["RATE"][y] for y in ry])
    rc = [y for y in ry if y >= L - 5]; _, drC, _ = ols(rc, [H["RATE"][y] for y in rc])
    _, bS, r2S = ols(Y, [H["PRIM"][y] / H["REC"][y] for y in Y])
    s0 = H["PRIM"][L] / H["REC"][L]; r0 = H["RATE"][L]
    base = Trend(D0=H["D0"], r0=r0, R0=H["REC"][L], s0=s0, gR=gR, bs=bS, dr=dr,
                 start=dt.date(L, 10, 1), months=12 * a.years)
    cases = {f"Case A: all trend lines fitted {Y[0]}-{L}": base,
             f"Case B: rate held at FY{L} level (dr = 0)": replace(base, dr=0.0),
             f"Case C: rate slope fitted {rc[0]}-{L} only ({drC:+.3f} pp/yr)": replace(base, dr=drC)}
    R = {k: run(v) for k, v in cases.items()}; S = {k: paradigm_shift(v) for k, v in R.items()}
    keys = list(R)
    end = R[keys[0]][-1]["month"]
    # --- csv projection
    with open(os.path.join(a.out, "projection.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["case", "month", "debt_T", "interest_T", "revenue_T", "primary_deficit_T", "rate_pct", "I_over_R_pct"])
        for k, rows in R.items():
            for x in rows:
                w.writerow([k[:6], x["month"], f"{x['D']:.4f}", f"{x['I']:.4f}", f"{x['R']:.4f}", f"{x['P']:.4f}", f"{x['r']:.4f}", f"{x['q']:.3f}"])
    with open(os.path.join(a.out, "history.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["FY", "receipts_T", "outlays_T", "net_interest_T", "primary_deficit_T", "gross_debt_T", "effective_rate_pct", "I_over_R_pct"])
        for y in Y:
            w.writerow([y, f"{H['REC'][y]:.4f}", f"{H['OUT'][y]:.4f}", f"{H['NI'][y]:.4f}", f"{H['PRIM'][y]:.4f}", f"{H['DEBT'][y]:.4f}",
                        f"{H['RATE'].get(y, float('nan')):.4f}", f"{H['IR'][y]:.3f}"])
    # --- charts
    ch1 = os.path.join(a.out, "chart_interest_to_revenue.png")
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=120)
    ax.plot([dt.date(y, 9, 30) for y in Y], [H["IR"][y] for y in Y], color="#444", lw=2.2, marker="o", ms=3, label=f"Historic, FY{Y[0]}-FY{L} (net interest / receipts)")
    for (k, rows), c in zip(R.items(), ("#1f2a44", "#2e7d32", "#b03a2e")):
        cut = [x for x in rows if x["month"].year <= L + 20]
        ax.plot([x["month"] for x in cut], [x["q"] for x in cut], color=c, lw=1.8, label=f"Projected: {k}")
        s = S[k]
        if s and s["month"].year <= L + 20:
            ax.axvline(s["month"], color=c, lw=1, alpha=.6)
            ax.annotate(f"Paradigm-shift point: {s['month']:%b %Y}, I/R {s['q']:.1f}%", (s["month"], s["q"]), xytext=(-300, 30),
                        textcoords="offset points", fontsize=9, color=c, arrowprops=dict(arrowstyle="->", color=c))
    for lv in (25, 30, 40):
        ax.axhline(lv, ls=":", lw=1, color="#777"); ax.text(dt.date(Y[0], 6, 1), lv + 1, f"{lv}% reference line", fontsize=8, color="#666")
    ax.set_ylim(0, 160); ax.set_ylabel("Interest / revenue, % (nominal)"); ax.grid(alpha=.3); ax.legend(loc="upper left", fontsize=8.5)
    ax.set_title(f"Plendl Hourglass Model - FRED data, trend lines FY{Y[0]}-FY{L}, projected to {L+20}")
    fig.tight_layout(); fig.savefig(ch1); plt.close(fig)
    ch2 = os.path.join(a.out, "chart_observed_context.png")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=120)
    cc = [(dt.date.fromisoformat(d), v / 1000) for d, v in C["currcir"] if d >= f"{Y[0]}"]
    a1.plot(*zip(*cc), color="#1f2a44"); a1.set_title("Currency in circulation (CURRCIR), $T"); a1.grid(alpha=.3)
    nr = [(dt.date.fromisoformat(d), v) for d, v in C["nipa_ratio"] if d >= f"{Y[0]}"]
    a2.plot(*zip(*nr), color="#b03a2e"); a2.set_title("NIPA interest payments / federal current receipts, %"); a2.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(ch2); plt.close(fig)
    # --- markdown
    def fmt(s): return f"{s['month']:%B %Y} (I/R {s['q']:.1f}%)" if s else f"None through {end:%B %Y}"
    md = [f"# Plendl Hourglass Model - FRED edition, run {today:%d %B %Y}", "",
          f"Model version {__version__}. Data: FRED (Federal Reserve Bank of St. Louis), downloaded {today.isoformat()}. "
          f"Trend lines fitted over FY{Y[0]}-FY{L}. Projection starts {base.start:%d %B %Y}, monthly, {a.years} years.", "",
          "Not a Treasury, Federal Reserve, or CBO product. Not financial, investment, budget, or policy advice.", "",
          "## Headline", "",
          f"- Starting debt D0: ${H['D0']:.3f} T (GFDEBTN, {H['D0_date']})",
          f"- FY{L} receipts: ${H['REC'][L]:.3f} T; net interest: ${H['NI'][L]:.3f} T; primary deficit: ${H['PRIM'][L]:+.3f} T",
          f"- FY{L} interest-to-revenue (I/R): {H['IR'][L]:.1f}%; effective rate r0: {r0:.3f}%",
          f"- Currency in circulation: ${C['currcir_last'][1]/1000:.3f} T ({C['currcir_last'][0]}), {C['currcir_yoy']:+.1f}% year on year",
          f"- Observed NIPA interest / receipts ({C['nipa_last'][0]}): {C['nipa_last'][1]/C['nipa_last'][2]*100:.1f}% "
          f"(${C['nipa_last'][1]/1000:.3f} T / ${C['nipa_last'][2]/1000:.3f} T SAAR)", ""]
    md += ["## Calculated paradigm-shift point", "", "| Case | Paradigm-shift point | First month I/R >= 30% | First month I/R >= 40% |", "| --- | --- | --- | --- |"]
    for k in keys:
        c30, c40 = first_cross(R[k], 30), first_cross(R[k], 40)
        md.append(f"| {k} | {fmt(S[k])} | {c30['month']:%b %Y} |" if c30 else f"| {k} | {fmt(S[k])} | none |")
        md[-1] += f" {c40['month']:%b %Y} |" if c40 else " none |"
    md += ["", "Test: g_q(t) = 12 ln(q_t+1/q_t) and a(t) = g_q(t) - g_q(t-1). The paradigm-shift point is the first month from which, "
           "for every remaining month of the horizon, both g_q > 0 and a > 0. 30%/40% are reference lines only.", "",
           "## Fitted trend lines (OLS)", "", "| Series | Fit | Parameter | R^2 |", "| --- | --- | --- | --- |",
           f"| Receipts | log-linear | g_R = {gR*100:.2f}% / yr | {r2R:.3f} |",
           f"| Gross debt (reference) | log-linear | {(math.exp(bD)-1)*100:.2f}% / yr | {r2D:.3f} |",
           f"| Effective rate (net interest / avg debt) | linear | dr = {dr:+.4f} pp / yr | {r2r:.3f} |",
           f"| Primary deficit / receipts | linear | b_s = {bS*100:+.3f} pp / yr (start s0 = {s0*100:.1f}%) | {r2S:.3f} |", "",
           "## Calculated values, yearly points (Case A; I/R for all cases)", "",
           "| Point | Debt $T | Interest $T | Revenue $T | Primary deficit $T | Rate % | I/R A % | I/R B % | I/R C % |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    yearly = []
    for i in range(0, min(len(R[keys[0]]), 12 * 21), 12):
        x = R[keys[0]][i]; qs = [R[k][i]["q"] for k in keys]
        yearly.append([x["month"].strftime("%b %Y"), f"{x['D']:.2f}", f"{x['I']:.2f}", f"{x['R']:.2f}", f"{x['P']:+.2f}", f"{x['r']:.2f}"] + [f"{q:.1f}" for q in qs])
        md.append("| " + " | ".join(yearly[-1]) + " |")
    md += ["", "## Historic data (FRED)", "", "| FY | Receipts $T | Outlays $T | Net interest $T | Primary deficit $T | Gross debt $T | Eff. rate % | I/R % |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    hist = []
    for y in Y:
        hist.append([f"{y}{'p' if H['prelim'] and y == L else ''}", f"{H['REC'][y]:.3f}", f"{H['OUT'][y]:.3f}", f"{H['NI'][y]:.3f}", f"{H['PRIM'][y]:+.3f}",
                     f"{H['DEBT'][y]:.2f}", f"{H['RATE'][y]:.3f}" if y in H["RATE"] else "n/a", f"{H['IR'][y]:.1f}"])
        md.append("| " + " | ".join(hist[-1]) + " |")
    md += [""] + [f"Note: {n}" for n in H["notes"]] + ["", "![I/R chart](chart_interest_to_revenue.png)", "", "![Context](chart_observed_context.png)", "",
           "## FRED series", ""] + [f"- `{s}`: {d[0]} ({d[1]}, {d[2]}) - https://fred.stlouisfed.org/series/{s}" for s, d in fred.SERIES.items()]
    open(os.path.join(a.out, "report.md"), "w").write("\n".join(md) + "\n")
    summary = dict(run_date=today.isoformat(), D0=H["D0"], D0_date=H["D0_date"], last_fy=L, receipts=H["REC"][L], net_interest=H["NI"][L],
                   IR=H["IR"][L], r0=r0, gR=gR, dr=dr, drC=drC, bS=bS, s0=s0, currcir=C["currcir_last"],
                   shift={k: (S[k]["month"].isoformat(), S[k]["q"]) if S[k] else None for k in keys})
    json.dump(summary, open(os.path.join(a.out, "summary.json"), "w"), indent=2, default=str)
    write_pdf(os.path.join(a.out, "Plendl_Hourglass_Model_report.pdf"), md, yearly, hist, [ch1, ch2])
    print(json.dumps(summary, indent=2, default=str))

if __name__ == "__main__":
    main()
