# Data-Driven Eligibility Testing (Income-Based, Boundary-Focused)

A demo built to translate a real QA workflow into automated form: manually
filling a spreadsheet grid with synthetic applicant data (demographics,
income, family size) to test an income-based eligibility determination,
the kind of work done validating subsidized health coverage applications
against income/household-size rules.

**Important:** This demo uses a simplified, illustrative eligibility rule
set based on publicly available Federal Poverty Level figures. It does not
reproduce the actual business logic of any real government or client
system — that logic is proprietary, more complex, and was never exported
or reused here. This project demonstrates the *testing methodology*
(data-driven, boundary-focused QA), not any specific employer's system.

---

## The workflow this automates

The original manual process: open a grid (spreadsheet), fill in a row of
made-up data — name, family size, income — for a synthetic applicant, then
check whether the system correctly determines their eligibility tier.
Repeat for enough rows to cover the range of real-world scenarios,
especially the edge cases right around each income threshold, since that's
where eligibility logic bugs are most likely to surface.

This demo automates every part of that:

1. **`eligibility_rules.py`** — A simplified eligibility rules engine
   (Medicaid-style ceiling at 138% of the Federal Poverty Level, subsidy
   ceiling at 400%), used both to compute the *expected* answer when
   generating test data, and as the reference implementation the web
   form's JavaScript logic mirrors. Includes a deliberately broken variant
   (`determine_eligibility_broken`) with an off-by-one regression (`<`
   instead of `<=`) used to validate that boundary-focused test data
   catches real defects.

2. **`generate_test_data.py`** — Generates the synthetic test data "grid"
   programmatically instead of by hand. For every family size tested (1,
   2, 4, 6), it generates cases **just below, exactly at, and just above**
   each eligibility tier boundary, plus typical in-band cases and a suite
   of invalid-input validation scenarios. This is deliberate boundary-value
   test design, not random data — it's where eligibility bugs actually
   hide. Output: `test_data/eligibility_test_cases.csv` (directory
   auto-created if it does not exist).

3. **`eligibility_form.html`** — A small standalone web form (first name,
   last name, family size, income) representing the kind of intake form a
   real eligibility application would use, with the same simplified rule
   logic implemented in JavaScript so the page is self-contained and
   testable without a backend. Supports URL query parameters to
   parameterize rule thresholds (`?medicaid=130&subsidy=350`) and to
   toggle a broken rules engine (`?broken=true`) for regression testing.

4. **`test_eligibility_form.py`** — A data-driven Selenium + pytest test.
   It reads every row from the CSV grid, fills the web form exactly the
   way a real applicant would, submits it, and asserts the displayed
   result matches the expected eligibility tier from the CSV. Every test
   case becomes its own pytest parametrized test (`TC001`, `TC002`, ...),
   so a single failing row shows up as a single named test failure rather
   than a vague overall pass/fail. Includes smart path resolution — handles
   both flat and `test_pages/` subdirectory layouts automatically, and
   auto-generates the CSV if it is missing on first run.

---

## Requirements implemented

**Requirement 1 — Input validation testing.** Five invalid-input scenarios
are injected into the test data grid: negative income, zero family size,
negative family size, non-numeric income string, and non-numeric family
size string. Both the Python rules engine and the JavaScript form correctly
return `INVALID_INPUT` for all of these, and the Selenium suite asserts
each one.

**Requirement 2 — Parameterized rule thresholds.** The eligibility form
accepts URL query parameters (`?medicaid=130&subsidy=350`) to override the
default FPL ceiling percentages at runtime, simulating policy changes
without modifying any code. A dedicated Selenium test
(`test_parameterized_policy_change`) proves that an applicant at 135% FPL
— Medicaid-eligible under standard rules — correctly shifts to
`SUBSIDY_ELIGIBLE` when the Medicaid ceiling is lowered to 130%.

**Requirement 3 — Regression catching with a broken rules engine.** A
data-driven parametrized test suite (41 cases) with CI/CD via GitHub Actions demonstrates that boundary-focused test data
catches real defects:

- **Layer 1 (unit):** `test_broken_rules_engine_regression_caught` calls
  the Python broken engine directly, proving the off-by-one (`<` vs `<=`)
  misclassifies the exact boundary case.
- **Layer 2 (E2E):** `test_broken_rules_engine_regression_caught_via_ui`
  drives the actual form with `?broken=true` via Selenium, proving the
  same regression surfaces in the live UI — not just in the Python logic.

---

## Why this design

**Boundary-focused, not random, test data.** Generating data points exactly
at, just below, and just above each threshold is intentional — it catches
off-by-one errors and incorrect `<=` vs `<` comparisons in eligibility
logic, which is where real bugs in this kind of system tend to live.

**A results log, not just pass/fail.** The test run writes
`test_results.csv` at the end, logging every test ID, scenario
description, expected vs. actual result, and pass/fail status in one
place — similar to a test execution report you'd hand off or attach to a
ticket, rather than relying solely on pytest's console output.

**Separation of rules logic and test logic.** The eligibility rules live
in one place (`eligibility_rules.py`) and are used both to *generate* the
expected answers and as the reference the UI's JS logic mirrors. If the
rule set changes, regenerating the test data is one command
(`python generate_test_data.py`), not a manual re-entry of every row.

---

## Setup

### Option A — One-Click Launch (Windows)

Double-click `start.bat` in the project folder. It will:
- Check Python is installed
- Check Chrome is installed (required for Selenium)
- Verify `test_pages/eligibility_form.html` is present
- Create a virtual environment automatically if one doesn't exist
- Install all dependencies from `requirements.txt`
- Generate the synthetic test data grid automatically
- Run the full pytest suite with verbose output

> **Note:** `webdriver-manager` handles ChromeDriver download automatically on first run.

### Option B — Manual Setup

```bash
pip install -r requirements.txt
```

Requires Chrome installed locally; `webdriver-manager` handles the
matching chromedriver automatically.

---

## Running it

### Option A — Double-click `start.bat` (handles everything automatically)

### Option B — Manual

```bash
# 1. Generate the synthetic test data grid (41 test cases)
python generate_test_data.py

# 2. Run the full data-driven Selenium test suite
pytest test_eligibility_form.py -v
```

After the run, check `test_results.csv` for the full execution log across
all 41 test cases: 36 boundary/typical happy-path cases across 4 family
sizes, plus 5 invalid-input validation scenarios.

---

## Continuous Integration (CI/CD)

This repository includes a GitHub Actions workflow that automatically runs the full 41-case Selenium test suite on every push to `main` — demonstrating
continuous integration practices standard in enterprise QA environments.

- Workflow file: `.github/workflows/test.yml`
- Runs on: `ubuntu-latest`
- Steps: checkout → Python 3.11 setup → install dependencies → install Chrome → generate test data → run pytest suite
- Test results uploaded as a downloadable artifact after every run

[![Selenium Eligibility Test Suite](https://github.com/robertciceroson/selenium-eligibility-automation/actions/workflows/test.yml/badge.svg)](https://github.com/robertciceroson/selenium-eligibility-automation/actions/workflows/test.yml)

---

## Repository structure

```
selenium-eligibility-automation/
├── eligibility_rules.py               # Rules engine (normal + deliberately broken variant)
├── eligibility_form.html              # Standalone intake form (no backend required)
├── generate_test_data.py              # Synthetic CSV grid generator
├── test_eligibility_form.py           # Data-driven Selenium + pytest test suite
├── requirements.txt                   # selenium, webdriver-manager, pytest
├── start.bat                          # One-click local test runner for Windows
├── test_pages/
│   └── eligibility_form.html          # Form served during test execution
├── test_data/
│   └── eligibility_test_cases.csv     # Auto-generated; committed for reference
└── test_results.csv                   # Written after each test run
```

---

## Author

**Robert Cicero Son**
Scrum Master · Process Engineer · Prompt Engineer · Data Analyst · AI/ML Practitioner · CSM · CSPO · AI-Empowered SAFe Agilist

- GitHub: [github.com/robertciceroson](https://github.com/robertciceroson)
- LinkedIn: [linkedin.com/in/robert-son-0b33b3bb](https://linkedin.com/in/robert-son-0b33b3bb)
