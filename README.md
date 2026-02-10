# hw1 Grader — Setup Guide

## Repository Structure

```
hw1-grader/
├── grade.py                 # CLI entry point (called by CI)
├── grader/
│   ├── __init__.py
│   ├── config.py            # Constants, weights, student parameter derivation
│   ├── reference.py         # Reference (solution) implementations
│   ├── tests.py             # Individual test functions with partial credit
│   ├── utils.py             # GradeResult container, comparison helpers
│   └── runner.py            # Test orchestration, report printing, JSON export
└── README.md                # This file
```

## Architecture

```
┌─────────────────────────────────┐
│  hw1-template  (template repo)  │ ← GitHub Classroom template
│  - starter code with stubs      │
│  - .github/workflows/           │
│  - data/price_data.csv          │
└──────────────┬──────────────────┘
               │  (GitHub Classroom creates per-student copies)
               ▼
┌─────────────────────────────────┐
│  hw1-<student>  (student repo)  │ ← Students push here
│  - same structure as template   │
│  - workflow fetches grader ──────┼──┐
└─────────────────────────────────┘  │
                                     │ (git clone using GRADER_PAT)
┌─────────────────────────────────┐  │
│  hw1-grader   (PRIVATE repo)    │◄─┘
│  - grade.py + grader/ package   │
│  - reference implementations    │
│  - This README                  │
└─────────────────────────────────┘
```

## Step-by-Step Setup

### 1. Create the Grader Repository (Private)

```bash
# In your GitHub organization:
# Create a NEW PRIVATE repository called "hw1-grader"
# Then push the full grader package:

cd hw1-grader
git init
git add grade.py grader/ README.md
git commit -m "Initial grader"
git remote add origin https://github.com/<YOUR_ORG>/hw1-grader.git
git push -u origin main
```

> **Critical:** This repository MUST remain **private**. It contains
> the reference solutions.

### 2. Create a Personal Access Token (PAT)

1. Go to **GitHub → Settings → Developer settings → Fine-grained
   personal access tokens → Generate new token**.
2. Give it a descriptive name (e.g., `hw1-grader-readonly`).
3. Set **Resource owner** to your organization.
4. Under **Repository access**, select **Only select repositories**
   and choose `hw1-grader`.
5. Under **Permissions → Repository permissions**, set **Contents**
   to **Read-only**.
6. Generate and **copy** the token.

### 3. Add the PAT as an Organization Secret

1. Go to your **GitHub Organization → Settings → Secrets and
   variables → Actions**.
2. Click **New organization secret**.
3. Name: `GRADER_PAT`
4. Value: paste the PAT from step 2.
5. Under **Repository access**, select either:
   - **All repositories** (simplest), or
   - **Selected repositories** and add all `hw1-*` student repos
     (you may need to update this after the classroom assignment
     is created).

### 4. Create the Template Repository

```bash
# Create a NEW PUBLIC (or internal) repository called "hw1-template"
# Push the template code:

cd hw1-template
git init
git add .
git commit -m "hw1 template"
git remote add origin https://github.com/<YOUR_ORG>/hw1-template.git
git push -u origin main
```

### 5. Create the GitHub Classroom Assignment

1. Go to **GitHub Classroom** (classroom.github.com).
2. Create a new **Individual Assignment**.
3. Set the **template repository** to `<YOUR_ORG>/hw1-template`.
4. Enable **auto-grading** if you want the built-in badge (optional;
   the workflow handles grading independently).
5. Share the assignment link with students.

### 6. Verify

1. Accept the assignment yourself (or use a test student account).
2. Push a trivial change.
3. Check the **Actions** tab — the workflow should:
   - Clone the private grader repo.
   - Run `grade.py`.
   - Post a score summary.

If the workflow fails at the "Fetch grader" step, double-check that:
- The `GRADER_PAT` secret is accessible to the student repo.
- The PAT has read access to `hw1-grader`.
- The repo name in the workflow matches your org name.

## Unique Look-back Parameters

Each student receives a deterministic look-back period **in trading
days** (range: 21–252, roughly 1 month to 1 year) derived from a
SHA-256 hash of their repository name:

```python
slug = "hw1-johndoe"  # from GITHUB_REPOSITORY
h = int(hashlib.sha256(slug.encode()).hexdigest(), 16)
lookback_days = (h % 232) + 21  # → integer in [21, 252]
```

Students are told to make their code work for **any** valid look-back
in trading days, so they cannot hard-code answers.

## Checking a Student's Assigned Look-back

```python
import hashlib
username = "johndoe"  # GitHub username
slug = f"hw1-{username}"
h = int(hashlib.sha256(slug.encode()).hexdigest(), 16)
print(f"{username}: lookback = {(h % 232) + 21} trading days")
```

## Modifying the Grader

To update grading logic or fix bugs:

1. Edit the relevant file under `grader/`.
2. Push to `main`.
3. All future student pushes will automatically use the updated grader.
4. Students can re-trigger grading by pushing an empty commit:
   `git commit --allow-empty -m "re-grade" && git push`

## Module Responsibilities

| Module | Role |
|--------|------|
| `config.py` | Central constants (weights, tolerances, paths, student param) |
| `reference.py` | Ground-truth implementations for all 7 functions |
| `utils.py` | `GradeResult` container, `df_close` / `series_close` helpers |
| `tests.py` | One `test_*` function per student function; awards partial credit |
| `runner.py` | Orchestrates tests, prints report, writes `grading_results.json` |
| `grade.py` | Thin CLI entry point (`python grade.py`) |
