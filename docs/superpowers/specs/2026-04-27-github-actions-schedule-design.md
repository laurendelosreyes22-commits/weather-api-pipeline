# GitHub Actions Scheduled Weather Pipeline — Design Spec

**Date:** 2026-04-27
**Status:** Approved

---

## Overview

Schedule `weather.py` to run automatically once per day using GitHub Actions. The updated `weather_data.csv` is committed back to `main` after each successful run. The API key remains hardcoded in `weather.py`.

---

## Goals

- Run the weather pipeline daily without manual intervention
- Persist accumulated forecast data in the repo via git history
- Get notified of failures via GitHub's default email notification

---

## Architecture

### Files Changed or Added

| File | Change |
|------|--------|
| `.github/workflows/weather.yml` | New file — defines the scheduled workflow |

`weather.py` is unchanged.

---

## Workflow Design (`.github/workflows/weather.yml`)

### Triggers

- **`schedule`:** `0 6 * * *` — runs at 6:00 AM UTC every day
- **`workflow_dispatch`:** allows manual runs from the Actions UI (useful for testing)

### Runner

`ubuntu-latest`

### Steps

1. **Checkout repo** — `actions/checkout@v4`
2. **Set up Python 3.13** — `actions/setup-python@v5`
3. **Install dependencies** — `pip install -r requirements.txt`
4. **Run pipeline** — `python weather.py`
5. **Commit and push CSV** — only if `weather_data.csv` changed:
   - `git config` to set bot user name/email
   - `git add weather_data.csv`
   - `git diff --cached --quiet` check — skip commit if no changes
   - `git commit -m "chore: update weather data [skip ci]"`
   - `git push`

The `[skip ci]` tag in the commit message prevents the push from re-triggering the workflow.

---

## Error Handling

- If `weather.py` exits non-zero (API failure, network error, bad response), the workflow step fails
- GitHub marks the run as failed and sends an email notification to the repo owner
- No retry logic — acceptable for a daily data pipeline at this scale
- If the CSV is unchanged after a run, the commit step is skipped cleanly (no empty commits)

---

## Implementation Approach

Subagent-driven development. Only one code task:

1. Create `.github/workflows/weather.yml`

---

## Success Criteria

- Workflow appears in the Actions tab and runs successfully on manual trigger
- `weather_data.csv` is updated and a new commit appears on `main` after each run
