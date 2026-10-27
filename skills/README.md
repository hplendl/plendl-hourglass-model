# Skills used to build and run the Plendl Hourglass Model

These are the working instructions ("skills") and helper scripts used to produce, check and share the model each week.
Each folder has a `SKILL.md`: plain-markdown instructions with a short YAML header (`name`, `description`).

| Skill | What it does |
| --- | --- |
| [hourglass-fred-run](hourglass-fred-run/SKILL.md) | Runs this repo's FRED edition, sanity-checks it against the previous run and publishes the weekly refresh (`update.sh`). |
| [hourglass-treasury-run](hourglass-treasury-run/SKILL.md) | The original Treasury Fiscal Data + OMB data path with cached source files, the trend-line build, the PDF step and the weekly wrapper (`hourglass_run.py`). It reproduces the 20 Oct 2026 run. |
| [hourglass-x-thread](hourglass-x-thread/SKILL.md) | Turns a run into a 5-post X thread, chart and table images, and an optional article. Covers the weekly prep, post and record routine and the wording checks. |

The model math itself lives in [../PROMPT.md](../PROMPT.md) and [../README.md](../README.md).

## Using them with any AI agent
- **Agents that support skills** (folders with `SKILL.md`, e.g. Claude Code `.claude/skills/`, Cursor and similar): copy a folder into the agent's skills directory. The `description` line tells the agent when to load it.
- **Any chat assistant**: paste the `SKILL.md` text (plus PROMPT.md for the math) into the conversation and attach or point to the scripts.
- **No agent**: every step is a plain shell or Python command. Follow `SKILL.md` by hand.
- **Scheduling**: a weekly cron job, e.g. `0 6 * * 2 cd /path/to/plendl-hourglass-model && ./update.sh`, does what the weekly routine does.

Posting to social media is never automatic in these scripts. They only build and validate drafts. Posting is a separate, human-approved step.

Account names, private paths and other personal or project details were removed from these copies.
