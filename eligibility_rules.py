"""
eligibility_rules.py

A SIMPLIFIED, ILLUSTRATIVE income-based eligibility rule engine, modeled
loosely on how subsidized health coverage programs (e.g. Medicaid expansion /
marketplace subsidy programs) determine eligibility using household size and
income relative to the Federal Poverty Level (FPL).

IMPORTANT: This is NOT the actual business logic of any real government
or client system. It exists purely to give the test automation demo
something realistic to test against. Real eligibility systems incorporate
many more factors (immigration status, existing coverage, state-specific
rules, age, disability status, etc.) that are intentionally omitted here.

2024 federal poverty guidelines (48 contiguous states), used here only as
realistic example numbers:
    Household of 1: $15,060
    Each additional person: +$5,380
"""

from __future__ import annotations

FPL_BASE = 15060
FPL_PER_ADDITIONAL_PERSON = 5380

# Simplified eligibility bands, expressed as % of FPL
MEDICAID_EXPANSION_CEILING_PCT = 138   # <=138% FPL -> Medicaid-style eligible
SUBSIDY_CEILING_PCT = 400              # <=400% FPL -> subsidy-eligible
# above 400% FPL -> not eligible for income-based subsidy in this simplified model


def fpl_for_household(family_size: int) -> int:
    """Returns the FPL dollar amount for a given household size."""
    if family_size < 1:
        raise ValueError("family_size must be at least 1")
    return FPL_BASE + FPL_PER_ADDITIONAL_PERSON * (family_size - 1)


def income_as_pct_of_fpl(annual_income: float, family_size: int) -> float:
    fpl = fpl_for_household(family_size)
    return round((annual_income / fpl) * 100, 1)


def determine_eligibility(annual_income: float, family_size: int) -> str:
    """
    Returns one of: "MEDICAID_ELIGIBLE", "SUBSIDY_ELIGIBLE", "NOT_ELIGIBLE"

    This mirrors the shape of a real income-based eligibility determination
    (tiered bands based on % of FPL) without claiming to be any specific
    real program's actual rule set.
    """
    pct = income_as_pct_of_fpl(annual_income, family_size)

    if pct <= MEDICAID_EXPANSION_CEILING_PCT:
        return "MEDICAID_ELIGIBLE"
    elif pct <= SUBSIDY_CEILING_PCT:
        return "SUBSIDY_ELIGIBLE"
    else:
        return "NOT_ELIGIBLE"
