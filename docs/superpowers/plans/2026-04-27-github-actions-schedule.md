# GitHub Actions Scheduled Weather Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a GitHub Actions workflow that runs `weather.py` daily at 6 AM UTC and commits the updated `weather_data.csv` back to `main`.

**Architecture:** A single workflow file at `.github/workflows/weather.yml` handles scheduling, dependency installation, script execution, and committing the output CSV back to the repo. The commit step uses `git diff --cached --quiet` to skip the commit when the CSV hasn't changed, and includes `[skip ci]` in the commit message to prevent re-triggering the workflow.

**Tech Stack:** GitHub Actions, Python 3.13, pip, ubuntu-latest runner

---

### Task 1: Create the GitHub Actions workflow file

**Files:**
- Create: `.github/workflows/weather.yml`

> **Note:** There are no unit tests to write for a GitHub Actions YAML file. Verification is done by triggering the workflow manually via `workflow_dispatch` after the file is merged. Steps below walk through creation and manual verification.

- [ ] **Step 1: Create the workflows directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Create `.github/workflows/weather.yml` with this exact content**

```yaml
name: Weather Pipeline

on:
  schedule:
    - cron: "0 6 * * *"
  workflow_dispatch:

jobs:
  run-pipeline:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run weather pipeline
        run: python weather.py

      - name: Commit updated weather data
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add weather_data.csv
          git diff --cached --quiet && echo "No changes to commit" && exit 0
          git commit -m "chore: update weather data [skip ci]"
          git push
```

**Why each decision:**
- `name: Weather Pipeline` — appears in the Actions tab; clear and descriptive
- `cron: "0 6 * * *"` — 6:00 AM UTC daily
- `workflow_dispatch` — enables a manual "Run workflow" button in the Actions UI for testing
- `actions/checkout@v4` — current stable major version
- `actions/setup-python@v5` — current stable major version; `python-version: "3.13"` matches the local venv
- `github-actions[bot]` user — standard bot identity for automated commits; shows clearly in git log
- `git diff --cached --quiet && ... && exit 0` — skips the commit cleanly if the CSV didn't change; `exit 0` ensures the step succeeds rather than failing
- `[skip ci]` in commit message — prevents the push from re-triggering this workflow (GitHub Actions honors this tag)

- [ ] **Step 3: Verify the YAML is valid**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/weather.yml'))" && echo "YAML valid"
```

Expected output:
```
YAML valid
```

- [ ] **Step 4: Commit the workflow file**

```bash
git add .github/workflows/weather.yml
git commit -m "feat: add daily weather pipeline GitHub Actions workflow"
git push
```

- [ ] **Step 5: Verify the workflow appears in GitHub Actions**

- Go to your repo on GitHub
- Click the **Actions** tab
- You should see **Weather Pipeline** listed under "All workflows"

- [ ] **Step 6: Trigger a manual test run**

- In the **Actions** tab, click **Weather Pipeline**
- Click **Run workflow** → **Run workflow**
- Watch the run complete — all steps should show green checkmarks
- After the run, go to the repo's **Code** tab and confirm `weather_data.csv` has a new commit from `github-actions[bot]`
