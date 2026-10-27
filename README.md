# Plendl Hourglass Model (FRED edition)

An open, reproducible US federal fiscal runway model by Harry Plendl. It downloads public data from
[FRED](https://fred.stlouisfed.org) (Federal Reserve Bank of St. Louis), fits historic trend lines, extends them
with fixed accounting recurrences, and reports when the interest-to-revenue ratio "turns parabolic".

The goal is for anyone to **check the math and watch the trends**. Every number in a run comes from the
downloaded data, which is saved next to the report (`fred_raw.csv`).

- Full prompt (do it yourself or with any AI assistant): [PROMPT.md](PROMPT.md)
- Latest reference run: [outputs/latest/Plendl_Hourglass_Model_report.pdf](outputs/latest/Plendl_Hourglass_Model_report.pdf) ([markdown](outputs/latest/report.md), [history CSV](outputs/latest/history.csv), [projection CSV](outputs/latest/projection.csv), [raw FRED data](outputs/latest/fred_raw.csv))
- Archive of dated runs: [outputs/runs/](outputs/runs/) (refreshed weekly)

> **Not financial advice.** This is an arithmetic exercise on published series under pure status-quo inertia.
> It is not a Treasury, Federal Reserve, or CBO product and is not investment, budget, or policy advice.

## Run it

```bash
git clone https://github.com/hplendl/plendl-hourglass-model
cd plendl-hourglass-model
pip install -r requirements.txt
python -m hourglass.run --out my_run      # writes report.md, PDF, charts, CSVs
python -m pytest -q tests
```

No API key is needed (it uses FRED's public `fredgraph.csv` download). If you have a free
[FRED API key](https://fred.stlouisfed.org/docs/api/api_key.html), `export FRED_API_KEY=...` and the official API is used instead.

## Data (FRED series)

| Series | What | Units | Role |
| --- | --- | --- | --- |
| [FYFR](https://fred.stlouisfed.org/series/FYFR) | Federal receipts, fiscal year | $M | Revenue R |
| [FYONET](https://fred.stlouisfed.org/series/FYONET) | Federal net outlays, fiscal year | $M | Primary deficit |
| [FYOINT](https://fred.stlouisfed.org/series/FYOINT) | Federal outlays: interest (net interest), fiscal year | $M | Interest I |
| [FYGFD](https://fred.stlouisfed.org/series/FYGFD) | Gross federal debt, fiscal year | $B | Debt history, effective rate |
| [GFDEBTN](https://fred.stlouisfed.org/series/GFDEBTN) | Federal debt: total public debt, quarterly | $M | Starting debt D0 |
| [MTSR133FMS](https://fred.stlouisfed.org/series/MTSR133FMS) | Monthly Treasury Statement receipts | $M | Newest (preliminary) fiscal year |
| [MTSO133FMS](https://fred.stlouisfed.org/series/MTSO133FMS) | Monthly Treasury Statement outlays | $M | Newest (preliminary) fiscal year |
| [A091RC1Q027SBEA](https://fred.stlouisfed.org/series/A091RC1Q027SBEA) | Federal interest payments (NIPA), quarterly SAAR | $B | Observed check; preliminary-year interest growth |
| [FGRECPT](https://fred.stlouisfed.org/series/FGRECPT) | Federal current receipts (NIPA), quarterly SAAR | $B | Observed interest/receipts check |
| [CURRCIR](https://fred.stlouisfed.org/series/CURRCIR) | Currency in circulation | $B | Context (reported, not a recurrence input) |

## The math

Fiscal years end 30 September. History runs FY2000 to the latest fiscal year.

- Primary deficit: `P_y = outlays_y - receipts_y - net_interest_y`
- Effective rate: `r_y = net_interest_y / ((debt_{y-1} + debt_y) / 2)`
- Interest-to-revenue: `q_y = net_interest_y / receipts_y`

Trend lines (OLS over the window): receipts log-linear (`g_R = e^slope - 1`); effective rate linear (`dr` pp/yr);
primary-deficit share `s = P/R` linear (`b_s`/yr).

Recurrences, monthly, nominal:

```
I_t   = D_t * r_t
D_t+1 = D_t + (I_t + s_t * R_t) / 12
R_t+1 = R_t * (1 + g_R)^(1/12)
s_t+1 = s_t + b_s / 12
r_t+1 = r_t + dr / 12
q_t   = I_t / R_t
```

Cases: **A** all trends fitted over the full window; **B** rate held flat; **C** rate slope fitted over the last six fiscal years.

**Paradigm-shift point:** with `g_q(t) = 12 ln(q_{t+1}/q_t)` and `a(t) = g_q(t) - g_q(t-1)`, the first month from which
every remaining month of the 40-year horizon has `g_q > 0` and `a > 0`: interest growth outruns revenue growth and the
gap itself keeps widening. 25/30/40% lines are reference only.

## Approximations and known differences

- **Newest fiscal year is preliminary.** Until FRED's annual series post it, receipts and outlays are the sum of 12 monthly
  MTS values; net interest is last official FY net interest scaled by the growth of NIPA interest payments
  (latest 4 quarters vs prior 4); debt is the latest `GFDEBTN` quarter.
- **Starting debt lags.** `GFDEBTN` is quarterly, so D0 can be a few months older than Treasury's daily Debt to the Penny.
- **Rate trend.** FRED has no "average interest rate on marketable debt" series, so the rate trend is fitted on the
  effective rate (net interest / average gross debt). Earlier Treasury-data runs fitted the September average marketable
  rate, which gave a steeper negative full-window slope.
- **CURRCIR** updates with a lag and is shown as context only.

## Model history

- Early Oct 2026: annual threshold model with locked "accelerators" at 25/30/40% I/R and a displacement test (I > R - M).
- 14 Oct 2026 onward: trend-line model above (no adders); 2000+ lookback with Treasury/OMB data.
- 27 Oct 2026: this open FRED edition, same recurrences, FRED data only.

## License

MIT. See [LICENSE](LICENSE).
