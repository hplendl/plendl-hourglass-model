---
name: hourglass-fred-run
description: Run the Plendl Hourglass Model (FRED edition) from this repo, check the output against the last run, and publish the weekly refresh.
---
# Plendl Hourglass Model: FRED run and weekly refresh

Use this when asked to run, refresh, or check the Plendl Hourglass Model with FRED data.

## Steps
1. `pip install -r requirements.txt` (once).
2. `python -m pytest -q tests` must pass.
3. `python -m hourglass.run --out outputs/latest`. No key is needed. Set `FRED_API_KEY` to use the FRED API instead of `fredgraph.csv`.
   - Note: FRED's CDN stalls some default Python user agents, so the code sends a curl-style header. Keep it.
4. Sanity-check `outputs/latest/summary.json` against the previous `outputs/runs/<date>/summary.json`:
   - Receipts and interest should move only a few percent per year.
   - I/R for the newest FY should be near the observed NIPA ratio (within ~2 pp).
   - A paradigm-shift month that jumps more than about a year needs an explanation (usually a data revision).
5. To publish: `./update.sh`. It runs the tests, reruns the model, refreshes `outputs/latest`, archives the run under `outputs/runs/YYYY-MM-DD/`, then commits and pushes.

## Rules
- Report only calculated values. No narrative, no adjectives like crisis or collapse.
- Keep the disclaimer: not a Treasury, Federal Reserve, or CBO product; not financial, investment, budget, or policy advice.
- State every approximation, especially the estimated newest-year interest (marked `*`).
