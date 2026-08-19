from routing import match_partners


def test_youlend_scores_higher_with_revenue_and_bank_consent():
    base = {
        "requested_amount": 25000,
        "monthly_revenue": 15000,
        "years_in_business": 2,
        "bank_data_consent": 1,
        "partner_data_consent": 1,
        "business_type": "retail",
        "hffi_project_type": "grocery_store",
    }
    matches = match_partners(base, {"band": "Partner-ready"})
    youlend = next(item for item in matches if item["slug"] == "youlend")
    assert youlend["fit"] >= 80
    assert youlend["live_ready"] is True
