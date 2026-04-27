# GitHub Actions Scheduled Weather Pipeline — Design Spec

**Date:** 2026-04-27
**Status:** Approved

---

## Overview

Schedule `weather.py` to run automatically once per day using GitHub Actions. The updated `weather_data.csv` is committed back to `main` after each successful run. The API key is moved out of source code and into GitHub Actions Secrets.

---

## Goals

- Run the weather pipeline daily without manual intervention
- Persist accumulated forecast data in the repo via git history
- Keep the WeatherAPI key out of source code (repo is public)
- Get notified of failures via GitHub's default email notification

---

## Architecture

### Files Changed or Added

| File | Change |
|------|--------|
| `weather.py` | Replace hardcoded API key with `os.getenv("WEATHER_API_KEY")` |
| `.github/workflows/weather.yml` | New file — defines the scheduled workflow |

### GitHub Secret

A secret named `WEATHER_API_KEY` must be added to the repo under:
**Settings → Secrets and variables → Actions → New repository secret**

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
4. **Run pipeline** — `python weather.py` with `WEATHER_API_KEY` injected from secrets as an environment variable
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

## Security

- The API key is removed from `weather.py` source code going forward
- The key remains in git history (prior commits cannot be rewritten without force-push), but will no longer be used in future runs
- The secret is only accessible to the workflow runner — not exposed in logs

---

## Implementation Approach

Subagent-driven development. Tasks are independent and can be parallelized:

1. Patch `weather.py` to use `os.getenv("WEATHER_API_KEY")`
2. Create `.github/workflows/weather.yml`
3. Document the secret setup step for the user

---

## Success Criteria

- Workflow appears in the Actions tab and runs successfully on manual trigger
- `weather_data.csv` is updated and a new commit appears on `main` after each run
- No API key visible in `weather.py` source
