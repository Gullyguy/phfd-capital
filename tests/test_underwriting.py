from underwriting import assess


def test_partner_ready_profile():
    result = assess({
        "years_in_business": 4,
        "monthly_revenue": 30000,
        "monthly_expenses": 15000,
        "cash_balance": 50000,
        "avg_daily_balance": 25000,
        "existing_monthly_debt": 1000,
        "requested_amount": 25000,
        "requested_term_months": 24,
        "nsf_count_90d": 0,
        "revenue_volatility": "low",
        "documents_ready": 1,
        "training_completed": 1,
    })
    assert result.score >= 75
    assert result.band == "Partner-ready"
    assert result.recommended_amount > 0


def test_low_readiness_profile_has_specific_reasons():
    result = assess({
        "years_in_business": 0.1,
        "monthly_revenue": 2500,
        "monthly_expenses": 3500,
        "cash_balance": 100,
        "existing_monthly_debt": 500,
        "requested_amount": 50000,
        "requested_term_months": 12,
        "nsf_count_90d": 4,
        "revenue_volatility": "high",
        "documents_ready": 0,
        "training_completed": 0,
    })
    codes = {reason["code"] for reason in result.reasons}
    assert result.band == "Capital readiness"
    assert "NEGATIVE_OPERATING_MARGIN" in codes
    assert "FREQUENT_NSFS" in codes
