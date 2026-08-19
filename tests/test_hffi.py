from hffi import evaluate


def test_grocery_profile_can_be_eligible():
    result = evaluate({
        "hffi_project_type": "food_coop",
        "hffi_underserved_area": 1,
        "hffi_snap_status": "will_apply",
        "hffi_staple_categories": ["fruits_vegetables", "bread_cereal", "dairy"],
        "hffi_perishable_food": 1,
    })
    assert result["status"] == "Eligible profile"
    assert not result["blockers"]


def test_food_pantry_is_not_aligned():
    result = evaluate({
        "hffi_project_type": "food_pantry",
        "hffi_charitable_free_food": 1,
    })
    assert result["status"] == "Not aligned"
    assert result["blockers"]


def test_supply_chain_requires_downstream_snap_retail():
    result = evaluate({
        "hffi_project_type": "distributor",
        "hffi_perishable_food": 1,
        "hffi_downstream_snap_retail": 0,
    })
    assert result["status"] == "Potentially eligible"
    assert any("SNAP-authorized" in item for item in result["conditions"])


def test_general_business_is_not_screened():
    result = evaluate({"hffi_project_type": ""})
    assert result["status"] == "Not screened"
