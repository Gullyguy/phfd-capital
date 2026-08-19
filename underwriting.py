from __future__ import annotations

from dataclasses import dataclass
from math import pow
from typing import Any


@dataclass(frozen=True)
class UnderwritingResult:
    score: int
    band: str
    recommended_amount: float
    reasons: list[dict[str, str]]
    strengths: list[str]
    metrics: dict[str, float]

    def as_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "band": self.band,
            "recommended_amount": self.recommended_amount,
            "reasons": self.reasons,
            "strengths": self.strengths,
            "metrics": self.metrics,
            "disclaimer": (
                "This is a non-binding capital-readiness assessment. It is not a credit approval, "
                "offer, denial, or substitute for a licensed lender's underwriting and human review."
            ),
        }


def amortized_payment(principal: float, annual_rate: float, months: int) -> float:
    if principal <= 0 or months <= 0:
        return 0.0
    monthly_rate = annual_rate / 12.0
    if monthly_rate == 0:
        return principal / months
    factor = pow(1 + monthly_rate, months)
    return principal * monthly_rate * factor / (factor - 1)


def assess(payload: dict[str, Any]) -> UnderwritingResult:
    years = max(float(payload.get("years_in_business") or 0), 0)
    revenue = max(float(payload.get("monthly_revenue") or 0), 0)
    expenses = max(float(payload.get("monthly_expenses") or 0), 0)
    cash = max(float(payload.get("cash_balance") or 0), 0)
    avg_balance = max(float(payload.get("avg_daily_balance") or 0), 0)
    existing_debt = max(float(payload.get("existing_monthly_debt") or 0), 0)
    requested = max(float(payload.get("requested_amount") or 0), 0)
    term = min(max(int(payload.get("requested_term_months") or 24), 3), 84)
    nsf = max(int(payload.get("nsf_count_90d") or 0), 0)
    volatility = str(payload.get("revenue_volatility") or "moderate").lower()
    docs = bool(int(payload.get("documents_ready") or 0))
    training = bool(int(payload.get("training_completed") or 0))

    # Stress payment is a planning assumption, not offered pricing.
    stress_payment = amortized_payment(requested, annual_rate=0.18, months=term)
    operating_margin = revenue - expenses - existing_debt
    dscr = operating_margin / stress_payment if stress_payment > 0 else 0.0
    annual_revenue_to_request = (revenue * 12) / requested if requested > 0 else 0.0
    liquidity_months = cash / expenses if expenses > 0 else (3.0 if cash > 0 else 0.0)
    avg_balance_ratio = avg_balance / max(expenses, 1)

    score = 0
    reasons: list[dict[str, str]] = []
    strengths: list[str] = []

    # Operating history: 15 points
    if years >= 3:
        score += 15
        strengths.append("Established operating history of at least three years")
    elif years >= 2:
        score += 12
    elif years >= 1:
        score += 9
    elif years >= 0.5:
        score += 5
        reasons.append({"code": "LIMITED_OPERATING_HISTORY", "detail": "Business has less than one year of operating history."})
    else:
        score += 2
        reasons.append({"code": "STARTUP_OPERATING_HISTORY", "detail": "Business has less than six months of operating history."})

    # Cash-flow coverage: 25 points
    if dscr >= 2.0:
        score += 25
        strengths.append("Strong cash-flow coverage under the planning stress payment")
    elif dscr >= 1.5:
        score += 21
        strengths.append("Healthy cash-flow coverage")
    elif dscr >= 1.15:
        score += 17
    elif dscr >= 0.9:
        score += 10
        reasons.append({"code": "TIGHT_CASH_FLOW_COVERAGE", "detail": "Projected cash-flow coverage is below 1.15x."})
    elif dscr > 0:
        score += 4
        reasons.append({"code": "LOW_CASH_FLOW_COVERAGE", "detail": "Projected cash flow may not cover the planning payment."})
    else:
        reasons.append({"code": "NEGATIVE_OPERATING_MARGIN", "detail": "Reported monthly expenses and debt equal or exceed revenue."})

    # Requested amount relative to revenue: 15 points
    if annual_revenue_to_request >= 6:
        score += 15
        strengths.append("Requested amount is conservative relative to annual revenue")
    elif annual_revenue_to_request >= 3:
        score += 12
    elif annual_revenue_to_request >= 1.5:
        score += 8
    elif annual_revenue_to_request >= 1:
        score += 4
        reasons.append({"code": "HIGH_REQUEST_TO_REVENUE", "detail": "Requested capital is high relative to annual revenue."})
    else:
        reasons.append({"code": "REQUEST_EXCEEDS_ANNUAL_REVENUE", "detail": "Requested capital exceeds reported annual revenue."})

    # Liquidity: 15 points
    if liquidity_months >= 2:
        score += 15
        strengths.append("At least two months of reported expense liquidity")
    elif liquidity_months >= 1:
        score += 12
    elif liquidity_months >= 0.5:
        score += 8
    elif liquidity_months >= 0.25:
        score += 4
        reasons.append({"code": "LOW_LIQUIDITY", "detail": "Cash balance covers less than half a month of expenses."})
    else:
        reasons.append({"code": "MINIMAL_LIQUIDITY", "detail": "Cash balance covers less than one quarter of monthly expenses."})

    # NSF pattern: 10 points
    if nsf == 0:
        score += 10
        strengths.append("No reported insufficient-funds events in the last 90 days")
    elif nsf == 1:
        score += 7
    elif nsf == 2:
        score += 4
        reasons.append({"code": "RECENT_NSFS", "detail": "Two insufficient-funds events were reported in the last 90 days."})
    else:
        reasons.append({"code": "FREQUENT_NSFS", "detail": "Three or more insufficient-funds events were reported in the last 90 days."})

    # Revenue stability: 10 points
    if volatility == "low":
        score += 10
        strengths.append("Reported revenue is relatively stable")
    elif volatility == "moderate":
        score += 7
    else:
        score += 3
        reasons.append({"code": "HIGH_REVENUE_VOLATILITY", "detail": "Reported revenue is highly variable."})

    # Readiness: 10 points
    if docs:
        score += 5
        strengths.append("Core financial documents are ready")
    else:
        reasons.append({"code": "DOCUMENTS_INCOMPLETE", "detail": "Core financial documents are not yet ready for lender review."})
    if training:
        score += 5
        strengths.append("Capital-readiness training is complete")
    else:
        reasons.append({"code": "TRAINING_NOT_COMPLETED", "detail": "Capital-readiness curriculum has not yet been completed."})

    score = max(0, min(100, round(score)))

    if score >= 75 and dscr >= 1.15:
        band = "Partner-ready"
    elif score >= 55:
        band = "Manual review"
    else:
        band = "Capital readiness"

    # Conservative internal planning range; not an offer.
    cashflow_capacity = max(operating_margin, 0) * 10
    revenue_capacity = revenue * 4
    recommended = min(requested, cashflow_capacity if cashflow_capacity else requested * 0.25, revenue_capacity if revenue_capacity else requested * 0.25)
    recommended = max(0, round(recommended / 500) * 500)

    return UnderwritingResult(
        score=score,
        band=band,
        recommended_amount=recommended,
        reasons=reasons[:6],
        strengths=strengths[:6],
        metrics={
            "stress_payment": round(stress_payment, 2),
            "operating_margin": round(operating_margin, 2),
            "dscr": round(dscr, 2),
            "annual_revenue_to_request": round(annual_revenue_to_request, 2),
            "liquidity_months": round(liquidity_months, 2),
            "average_balance_to_expense": round(avg_balance_ratio, 2),
        },
    )
