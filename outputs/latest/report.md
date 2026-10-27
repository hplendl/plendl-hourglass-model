# Plendl Hourglass Model - FRED edition, run 27 October 2026

Model version 1.0.0. Data: FRED (Federal Reserve Bank of St. Louis), downloaded 2026-10-27. Trend lines fitted over FY2000-FY2026. Projection starts 01 October 2026, monthly, 40 years.

Not a Treasury, Federal Reserve, or CBO product. Not financial, investment, budget, or policy advice.

## Headline

- Starting debt D0: $39.462 T (GFDEBTN, 2026-04-01)
- FY2026 receipts: $5.403 T; net interest: $1.044 T; primary deficit: $+0.948 T
- FY2026 interest-to-revenue (I/R): 19.3%; effective rate r0: 2.718%
- Currency in circulation: $2.416 T (2025-10-01), +2.6% year on year
- Observed NIPA interest / receipts (2026-04-01): 21.1% ($1.280 T / $6.056 T SAAR)

## Calculated paradigm-shift point

| Case | Paradigm-shift point | First month I/R >= 30% | First month I/R >= 40% |
| --- | --- | --- | --- |
| Case A: all trend lines fitted 2000-2026 | None through September 2066 | none | none |
| Case B: rate held at FY2026 level (dr = 0) | None through September 2066 | Oct 2047 | Apr 2059 |
| Case C: rate slope fitted 2021-2026 only (+0.312 pp/yr) | June 2036 (I/R 55.5%) | Jun 2030 | Mar 2033 |

Test: g_q(t) = 12 ln(q_t+1/q_t) and a(t) = g_q(t) - g_q(t-1). The paradigm-shift point is the first month from which, for every remaining month of the horizon, both g_q > 0 and a > 0. 30%/40% are reference lines only.

## Fitted trend lines (OLS)

| Series | Fit | Parameter | R^2 |
| --- | --- | --- | --- |
| Receipts | log-linear | g_R = 4.21% / yr | 0.917 |
| Gross debt (reference) | log-linear | 8.07% / yr | 0.991 |
| Effective rate (net interest / avg debt) | linear | dr = -0.0447 pp / yr | 0.221 |
| Primary deficit / receipts | linear | b_s = +1.221 pp / yr (start s0 = 17.6%) | 0.174 |

## Calculated values, yearly points (Case A; I/R for all cases)

| Point | Debt $T | Interest $T | Revenue $T | Primary deficit $T | Rate % | I/R A % | I/R B % | I/R C % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Oct 2026 | 39.46 | 1.07 | 5.40 | +0.95 | 2.72 | 19.8 | 19.8 | 19.8 |
| Oct 2027 | 41.55 | 1.11 | 5.63 | +1.06 | 2.67 | 19.7 | 20.1 | 22.4 |
| Oct 2028 | 43.79 | 1.15 | 5.87 | +1.17 | 2.63 | 19.6 | 20.3 | 25.1 |
| Oct 2029 | 46.19 | 1.19 | 6.11 | +1.30 | 2.58 | 19.5 | 20.6 | 28.0 |
| Oct 2030 | 48.76 | 1.24 | 6.37 | +1.43 | 2.54 | 19.4 | 20.9 | 31.2 |
| Oct 2031 | 51.51 | 1.28 | 6.64 | +1.57 | 2.49 | 19.3 | 21.2 | 34.6 |
| Oct 2032 | 54.46 | 1.33 | 6.92 | +1.72 | 2.45 | 19.3 | 21.6 | 38.4 |
| Oct 2033 | 57.61 | 1.39 | 7.21 | +1.88 | 2.40 | 19.2 | 21.9 | 42.5 |
| Oct 2034 | 60.98 | 1.44 | 7.51 | +2.05 | 2.36 | 19.2 | 22.3 | 47.0 |
| Oct 2035 | 64.58 | 1.49 | 7.83 | +2.23 | 2.31 | 19.1 | 22.8 | 51.9 |
| Oct 2036 | 68.42 | 1.55 | 8.16 | +2.43 | 2.27 | 19.0 | 23.2 | 57.4 |
| Oct 2037 | 72.52 | 1.61 | 8.50 | +2.63 | 2.23 | 19.0 | 23.7 | 63.5 |
| Oct 2038 | 76.90 | 1.68 | 8.86 | +2.85 | 2.18 | 18.9 | 24.3 | 70.2 |
| Oct 2039 | 81.57 | 1.74 | 9.23 | +3.09 | 2.14 | 18.9 | 24.8 | 77.7 |
| Oct 2040 | 86.54 | 1.81 | 9.62 | +3.33 | 2.09 | 18.8 | 25.4 | 86.0 |
| Oct 2041 | 91.83 | 1.88 | 10.02 | +3.60 | 2.05 | 18.7 | 26.0 | 95.2 |
| Oct 2042 | 97.47 | 1.95 | 10.45 | +3.88 | 2.00 | 18.7 | 26.6 | 105.5 |
| Oct 2043 | 103.46 | 2.02 | 10.89 | +4.17 | 1.96 | 18.6 | 27.2 | 117.0 |
| Oct 2044 | 109.83 | 2.10 | 11.34 | +4.49 | 1.91 | 18.5 | 27.9 | 129.9 |
| Oct 2045 | 116.61 | 2.18 | 11.82 | +4.82 | 1.87 | 18.4 | 28.6 | 144.2 |
| Oct 2046 | 123.80 | 2.26 | 12.32 | +5.17 | 1.82 | 18.3 | 29.3 | 160.3 |

## Historic data (FRED)

| FY | Receipts $T | Outlays $T | Net interest $T | Primary deficit $T | Gross debt $T | Eff. rate % | I/R % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2000 | 2.025 | 1.789 | 0.223 | -0.459 | 5.63 | 3.969 | 11.0 |
| 2001 | 1.991 | 1.863 | 0.206 | -0.334 | 5.77 | 3.617 | 10.4 |
| 2002 | 1.853 | 2.011 | 0.171 | -0.013 | 6.20 | 2.857 | 9.2 |
| 2003 | 1.782 | 2.160 | 0.153 | +0.225 | 6.76 | 2.363 | 8.6 |
| 2004 | 1.880 | 2.293 | 0.160 | +0.252 | 7.35 | 2.271 | 8.5 |
| 2005 | 2.154 | 2.472 | 0.184 | +0.134 | 7.91 | 2.411 | 8.5 |
| 2006 | 2.407 | 2.655 | 0.227 | +0.022 | 8.45 | 2.771 | 9.4 |
| 2007 | 2.568 | 2.729 | 0.237 | -0.076 | 8.95 | 2.725 | 9.2 |
| 2008 | 2.524 | 2.983 | 0.253 | +0.206 | 9.99 | 2.669 | 10.0 |
| 2009 | 2.105 | 3.518 | 0.187 | +1.226 | 11.88 | 1.710 | 8.9 |
| 2010 | 2.163 | 3.457 | 0.196 | +1.098 | 13.53 | 1.545 | 9.1 |
| 2011 | 2.303 | 3.603 | 0.230 | +1.070 | 14.76 | 1.626 | 10.0 |
| 2012 | 2.450 | 3.527 | 0.220 | +0.856 | 16.05 | 1.431 | 9.0 |
| 2013 | 2.775 | 3.455 | 0.221 | +0.459 | 16.72 | 1.348 | 8.0 |
| 2014 | 3.021 | 3.506 | 0.229 | +0.256 | 17.79 | 1.327 | 7.6 |
| 2015 | 3.250 | 3.692 | 0.223 | +0.219 | 18.12 | 1.243 | 6.9 |
| 2016 | 3.268 | 3.853 | 0.240 | +0.345 | 19.54 | 1.275 | 7.3 |
| 2017 | 3.316 | 3.982 | 0.263 | +0.403 | 20.21 | 1.321 | 7.9 |
| 2018 | 3.330 | 4.109 | 0.325 | +0.454 | 21.46 | 1.560 | 9.8 |
| 2019 | 3.463 | 4.447 | 0.375 | +0.608 | 22.67 | 1.700 | 10.8 |
| 2020 | 3.421 | 6.517 | 0.345 | +2.750 | 26.90 | 1.394 | 10.1 |
| 2021 | 4.047 | 6.821 | 0.352 | +2.421 | 28.39 | 1.275 | 8.7 |
| 2022 | 4.897 | 6.272 | 0.476 | +0.898 | 30.84 | 1.607 | 9.7 |
| 2023 | 4.441 | 6.128 | 0.658 | +1.029 | 32.99 | 2.063 | 14.8 |
| 2024 | 4.920 | 6.735 | 0.880 | +0.935 | 35.23 | 2.580 | 17.9 |
| 2025 | 5.236 | 7.011 | 0.970 | +0.805 | 37.38 | 2.672 | 18.5 |
| 2026p | 5.403 | 7.396 | 1.044 | +0.948 | 39.46 | 2.718 | 19.3 |

Note: FY2026 is preliminary: receipts/outlays = sum of MTS Oct 2025-Sep 2026; net interest = FY2025 x 1.0763 (NIPA interest growth, last 4 vs prior 4 quarters, through 2026-04-01); debt = GFDEBTN 2026-04-01.

![I/R chart](chart_interest_to_revenue.png)

![Context](chart_observed_context.png)

## FRED series

- `FYFR`: Federal Receipts, fiscal year (millions $, annual FY) - https://fred.stlouisfed.org/series/FYFR
- `FYONET`: Federal Net Outlays, fiscal year (millions $, annual FY) - https://fred.stlouisfed.org/series/FYONET
- `FYOINT`: Federal Outlays: Interest (net interest), fiscal year (millions $, annual FY) - https://fred.stlouisfed.org/series/FYOINT
- `FYGFD`: Gross Federal Debt, fiscal year end (billions $, annual FY) - https://fred.stlouisfed.org/series/FYGFD
- `GFDEBTN`: Federal Debt: Total Public Debt (millions $, quarterly) - https://fred.stlouisfed.org/series/GFDEBTN
- `MTSR133FMS`: Monthly Treasury Statement: Total Receipts (millions $, monthly) - https://fred.stlouisfed.org/series/MTSR133FMS
- `MTSO133FMS`: Monthly Treasury Statement: Total Outlays (millions $, monthly) - https://fred.stlouisfed.org/series/MTSO133FMS
- `A091RC1Q027SBEA`: Federal government current expenditures: Interest payments (billions $ SAAR, quarterly) - https://fred.stlouisfed.org/series/A091RC1Q027SBEA
- `FGRECPT`: Federal government current receipts (billions $ SAAR, quarterly) - https://fred.stlouisfed.org/series/FGRECPT
- `CURRCIR`: Currency in Circulation (billions $, monthly) - https://fred.stlouisfed.org/series/CURRCIR
