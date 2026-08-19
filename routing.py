from __future__ import annotations

from typing import Any


def match_partners(payload: dict[str, Any], underwriting: dict[str, Any]) -> list[dict[str, Any]]:
    amount = float(payload.get("requested_amount") or 0)
    revenue = float(payload.get("monthly_revenue") or 0)
    years = float(payload.get("years_in_business") or 0)
    bank_consent = bool(int(payload.get("bank_data_consent") or 0))
    partner_consent = bool(int(payload.get("partner_data_consent") or 0))
    band = underwriting.get("band")

    matches: list[dict[str, Any]] = []

    def add(slug: str, name: str, fit: int, route: str, reason: str, live_ready: bool) -> None:
        matches.append({
            "slug": slug,
            "name": name,
            "fit": max(0, min(100, fit)),
            "route": route,
            "reason": reason,
            "live_ready": live_ready and partner_consent,
        })

    lendflow_fit = 70
    if amount <= 500_000:
        lendflow_fit += 10
    if partner_consent:
        lendflow_fit += 5
    add(
        "lendflow",
        "Lendflow",
        lendflow_fit,
        "Multi-lender marketplace",
        "Broad product routing and white-label borrower journey make this the best general fallback and second-look path.",
        live_ready=True,
    )

    youlend_fit = 45
    if revenue >= 5_000:
        youlend_fit += 20
    if bank_consent:
        youlend_fit += 15
    if 1_000 <= amount <= 1_000_000:
        youlend_fit += 10
    if years >= 0.5:
        youlend_fit += 5
    add(
        "youlend",
        "YouLend",
        youlend_fit,
        "Managed revenue-based capital",
        "Strong immediate pilot candidate when bank or payment data can support a revenue-based offer.",
        live_ready=bank_consent,
    )

    kanmon_fit = 35
    if years >= 1:
        kanmon_fit += 15
    if revenue >= 10_000:
        kanmon_fit += 15
    if bank_consent:
        kanmon_fit += 10
    if payload.get("business_type") in {"distributor", "logistics", "food_hub", "retail", "service"}:
        kanmon_fit += 10
    add(
        "kanmon",
        "Kanmon",
        kanmon_fit,
        "Full-stack embedded working capital",
        "Best fit as PHFD captures recurring transaction, invoice, order, or supply-chain data across its business network.",
        live_ready=False,
    )

    parafin_fit = 30
    if years >= 1:
        parafin_fit += 15
    if revenue >= 15_000:
        parafin_fit += 20
    if bank_consent:
        parafin_fit += 15
    if band == "Partner-ready":
        parafin_fit += 10
    add(
        "parafin",
        "Parafin",
        parafin_fit,
        "Turnkey term or revenue-based capital",
        "Strong managed-program fit after PHFD establishes recurring merchant data and sufficient platform scale.",
        live_ready=False,
    )

    loanwell_fit = 40
    if amount <= 50_000:
        loanwell_fit += 20
    if payload.get("hffi_project_type"):
        loanwell_fit += 10
    if band in {"Partner-ready", "Manual review"}:
        loanwell_fit += 10
    add(
        "loanwell",
        "LoanWell",
        loanwell_fit,
        "PHFD-owned microfund operating system",
        "Use when PHFD has legal authority, capital, credit policy, and servicing responsibility for its own business-purpose loans.",
        live_ready=False,
    )

    matches.sort(key=lambda x: (-x["fit"], x["name"]))
    return matches
