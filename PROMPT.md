# The Plendl Hourglass Model - full prompt

Paste this into any capable AI assistant (or follow it by hand) to build your own Plendl Hourglass Model.
The Python in this repo implements exactly this prompt, so you can check one against the other.

> Note: this is the prompt the model runs on today (the trend-line method, adopted 14 October 2026), written out in full.
> The original early-October version used threshold "accelerators"; see README, "Model history".

---

**Role.** You are a careful quantitative analyst. Run the Plendl Hourglass Model, a fiscal runway projection
for the United States federal government. Report calculated values only. No narrative, no forecasts of policy,
no partisan language.

**Idea.** Picture an hourglass. Federal revenue is the sand that can pass through the neck. Interest on the debt
is a claim on that same sand that is paid before anything else. The model measures how fast the interest claim
grows relative to revenue and finds the calculated moment when that ratio stops merely rising and starts
compounding at a rising rate (the trend line "turns parabolic").

**Data (FRED, Federal Reserve Bank of St. Louis, https://fred.stlouisfed.org).** Fiscal years end 30 September.
- `FYFR` federal receipts, `FYONET` federal net outlays, `FYOINT` federal net interest, `FYGFD` gross federal debt (annual, fiscal year).
- `MTSR133FMS`, `MTSO133FMS` monthly Treasury receipts and outlays (to build the newest fiscal year before the annual series updates).
- `GFDEBTN` total public debt (latest quarterly value = starting debt D0).
- `A091RC1Q027SBEA` federal interest payments and `FGRECPT` federal current receipts (quarterly, SAAR): observed interest-to-receipts check, and the growth factor used to estimate net interest for a preliminary fiscal year.
- `CURRCIR` currency in circulation: reported as context (level and year-on-year change). It is not an input to the recurrences.

**Step 1 - history, FY2000 to the latest fiscal year.** For each year compute
primary deficit P = outlays - receipts - net interest (negative = primary surplus),
effective rate r = net interest / average of this and last year's gross debt (percent),
and the ratio q = net interest / receipts (percent).

**Step 2 - fit trend lines by ordinary least squares over the full window.**
- Receipts: log-linear, giving annual growth g_R = exp(slope) - 1.
- Effective rate: linear, slope dr in percentage points per year.
- Primary deficit as a share of receipts, s = P / R: linear, slope b_s per year. (The dollar series changes sign, so a log fit is undefined.)
- Report each R^2. Gross debt CAGR is reported for reference only.

**Step 3 - initialize at 1 October after the latest fiscal year.**
D0 = latest total public debt; R0 = latest fiscal-year receipts; s0 = latest actual share P/R (no jump to the fitted level);
r0 = latest effective rate.

**Step 4 - run the recurrences monthly for 40 years, in nominal dollars (inflation already included):**

    I_t   = D_t x r_t
    D_t+1 = D_t + (I_t + s_t x R_t) / 12
    R_t+1 = R_t x (1 + g_R)^(1/12)
    s_t+1 = s_t + b_s / 12
    r_t+1 = r_t + dr / 12
    q_t   = I_t / R_t

Run three cases of equal standing that differ only in the rate trend:
Case A uses dr fitted over the whole window; Case B holds the rate flat (dr = 0);
Case C uses dr fitted over the last six fiscal years only.

**Step 5 - paradigm-shift test.** g_q(t) = 12 x ln(q_t+1 / q_t) (interest growth minus revenue growth, annualized);
a(t) = g_q(t) - g_q(t-1). The paradigm-shift point is the first month from which, for every remaining month
of the horizon, both g_q > 0 and a > 0. Months with a non-positive ratio fail. If no month qualifies,
report "None through <last month>". 25%, 30% and 40% are reference lines only and play no part in the test.

**Step 6 - report.** A table of fitted parameters with R^2; a yearly table (1 October) of debt, interest, revenue,
primary deficit, rate and I/R for each case; the historic table; a chart of historic plus projected I/R with the
paradigm-shift points marked; observed context (currency in circulation, NIPA interest / receipts); the FRED series
IDs and download date. End with: "Not a Treasury, Federal Reserve, or CBO product. Not financial, investment,
budget, or policy advice."

**Rules.** Use only the downloaded data. Do not re-round numbers between steps. State every approximation.
Flag any internal inconsistency instead of resolving it silently.
