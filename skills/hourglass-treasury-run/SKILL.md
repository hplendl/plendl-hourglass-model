---
name: hourglass-treasury-run
description: Weekly Predictive/Plendl Hourglass trend-line run on Treasury Fiscal Data + OMB Historical Tables (the data path used for the weekly X thread before the FRED edition).
---
# Hourglass run on Treasury and OMB data

This is the original data path: OMB Historical Tables 1.1 and 3.1, Treasury Fiscal Data (Historical Debt Outstanding, Average Interest Rates, Debt to the Penny, MTS Tables 1 and 9) and a CBO Monthly Budget Review cross-check. The math is the same trend-line model as the FRED edition. The one difference is the rate trend, which is fitted on the September average interest rate on total marketable debt.

## Files (scripts/)
- `model.py`: the recurrences.
  - `run_trend2` and `paradigm_shift2` drive current runs.
  - `run_trend` and `run` (the early-October threshold-accelerator model) are kept so older runs can be reproduced.
- `hist_2000.py`: loads `data/` and fits trend lines over FY2000 to the latest fiscal year.
- `build_md_template.py`: writes the report .md, the chart and a 5-post thread draft. The run date comes from `HG_RUN_DATE`.
- `make_pdf.py`: turns the markdown into HTML. Print it with headless Chrome:
  `google-chrome --headless --no-sandbox --no-pdf-header-footer --print-to-pdf=X.pdf file://$PWD/.X.html`
- `hourglass_run.py`: the weekly wrapper.
  - `--mode prep` refreshes Debt to the Penny and Historical Debt Outstanding, builds into `$HG_OUT_DIR/<date>/` and validates. It prints `READY: <path>` or `ERROR`.
  - `--mode post` prints `SKIP` if this ISO week is already in the posted log.
  - `--record <url>` logs a posted thread.
- `data/`: cached public source files as of 20 Oct 2026, which reproduce the Oct 20 run (Case C shift Aug 2036, I/R 71.5%).

## Refreshing data
Use the Fiscal Data API with `curl -g`, because it takes `page[size]`. For example:
`https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_outstanding?filter=record_fiscal_year:gte:1999&sort=record_date&page[size]=100`
Download OMB tables from https://www.govinfo.gov/app/collection/budget/ (Historical Tables).

## Run
```bash
cd skills/hourglass-treasury-run/scripts
HG_OUT_DIR=./out python3 hourglass_run.py --mode prep            # add --no-refresh to use cached data only
```
The trend parts of `hist_2000.py` have the FY2026 year hard-coded. Bump them when FY2027 data lands.
