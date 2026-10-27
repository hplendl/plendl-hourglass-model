---
name: hourglass-x-thread
description: Turn a Hourglass Model run into a weekly X (Twitter) thread draft, table/chart images and an optional X Article; schedule and posting rules of the weekly routine.
---
# Hourglass run to X thread

## Weekly routine (as it ran in Oct 2026)
- Monday: prep and preview.
  - Build the run (hourglass-treasury-run `--mode prep`, or the FRED edition).
  - Send the draft thread and chart to the model owner for review twice during the day.
- Tuesday early morning: post.
  - Run `--mode post`. Stop silently on `SKIP` (already posted this ISO week, or no new run).
  - Otherwise post the 5 posts as one thread with the chart on post 3.
  - Then `--record <url of post 1>`.
- Post only with the owner's standing approval. Any request for changes or a hold stops the week's post.

## Thread format (5 posts, current)
1. Run date, the starting debt and its source date, and I/R for the newest fiscal year.
2. The identity I = D x r, with the opening rate and interest measured against revenue.
3. The fitted trend lines (g_R, dr, b_s). **Attach the chart.**
4. The calculated paradigm-shift point for each case (A/B/C), or "None through <month>".
5. Fixed closing sentence: "5/5 The model runs the values: historic trend lines are measured, extended by calculation into future projected trends, and the resulting figures at each point and moment in time are reported without narrative."

## Checks (hourglass_run.py `validate` enforces these)
- Exactly 5 posts, each numbered `n/5 `. ASCII only (write "x" not "×" and "to" not arrows), so X's weighted count equals `len()`. Each post is 280 characters or fewer.
- Banned words: crisis, collapse, hyperinflation, breaks, breach, runaway, educated guess, dramatic, catastroph*, doom, explode, skyrocket, spiral, death, bankrupt, shocking, alarming, unsustainable.
- Copy numbers verbatim from the run file. Never re-round. 25/30/40% are "reference lines" only.
- Tone: plain, factual, non-partisan, no emoji, at most 1-2 hashtags.
- Flag any inconsistency in the source rather than resolving it silently.

## Helpers (scripts/)
- `make_table_png.py RUN.md --out table.png [--thresholds-out thresholds.png] [--last-year 2040]` renders the projection table at 1200x1200 and repairs mis-encoded dashes and minus signs.
- `posts_template.py` is the legacy 8-post template from 5 Oct 2026 (threshold model), kept for reference. Check character counts with:
  `python3 -c "from posts_template import posts; [print(i+1, len(p)) for i,p in enumerate(posts)]"`

## X Article (optional)
Write 400-700 words with a title and markdown tables (central projection, cases), drawn from the same run file.
