"""
test_eligibility_form.py

Data-driven Selenium test: reads every row of test_data/eligibility_test_cases.csv
(the synthetic "grid" of demographic/income/family-size data) and, for each
row, drives the eligibility intake form exactly the way a real applicant
would -- filling in first name, last name, family size, and income -- then
asserts the displayed result matches the expected_eligibility column from
the CSV.

This is the automated equivalent of the manual process of filling in a
two-line grid with made-up applicant data row by row to validate an
income-based eligibility determination: same underlying QA pattern
(boundary-focused, data-driven test design), but driven by pytest +
Selenium instead of manual data entry, and with results logged to a
report file instead of eyeballed one row at a time.

Run with:
    python generate_test_data.py        # (re)generate the CSV grid first
    pytest test_eligibility_form.py -v

Requires Chrome + chromedriver (webdriver-manager handles the driver).
"""

import csv
import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

HERE = os.path.dirname(os.path.abspath(__file__))
FORM_URL = "file://" + os.path.join(HERE, "eligibility_form.html")
CSV_PATH = os.path.join(HERE, "test_data", "eligibility_test_cases.csv")
RESULTS_LOG = os.path.join(HERE, "test_results.csv")


def load_test_cases():
    with open(CSV_PATH, newline="") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=options)
    yield drv
    drv.quit()


@pytest.fixture(scope="module")
def results_logger():
    """Collects pass/fail results across the whole data-driven run and
    writes them to a CSV report at the end -- gives you a single
    artifact summarizing every row's outcome, similar to a QA test
    execution log you'd hand off or attach to a ticket."""
    rows = []
    yield rows
    if rows:
        with open(RESULTS_LOG, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nTest execution log written to: {RESULTS_LOG}")


@pytest.mark.parametrize("case", load_test_cases(), ids=lambda c: c["test_id"])
def test_eligibility_case(driver, results_logger, case):
    """
    Fills the eligibility form with one synthetic applicant's data and
    asserts the displayed eligibility result matches the expected outcome
    computed by the rules engine when the test data was generated.
    """
    driver.get(FORM_URL)

    driver.find_element(By.ID, "first-name-input").send_keys(case["first_name"])
    driver.find_element(By.ID, "last-name-input").send_keys(case["last_name"])
    driver.find_element(By.ID, "family-size-input").send_keys(case["family_size"])
    driver.find_element(By.ID, "income-input").send_keys(case["annual_income"])
    driver.find_element(By.ID, "submit-eligibility-btn").click()

    result_text = driver.find_element(By.ID, "eligibility-result").text
    actual = result_text.replace("Eligibility Result: ", "").strip()
    expected = case["expected_eligibility"]

    passed = actual == expected
    results_logger.append({
        "test_id": case["test_id"],
        "scenario": case["scenario"],
        "family_size": case["family_size"],
        "annual_income": case["annual_income"],
        "expected": expected,
        "actual": actual,
        "result": "PASS" if passed else "FAIL",
    })

    assert passed, (
        f"{case['test_id']} ({case['scenario']}): expected {expected}, got {actual}"
    )
