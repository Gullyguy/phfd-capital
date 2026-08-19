from __future__ import annotations

from typing import Any


RETAIL_TYPES = {"grocery_store", "food_coop", "mobile_market", "healthy_food_retail"}
ENTERPRISE_TYPES = {"food_hub", "distributor", "aggregator", "processor", "manufacturer", "cold_storage"}


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    project_type = str(payload.get("hffi_project_type") or "").strip()
    underserved = bool(int(payload.get("hffi_underserved_area") or 0))
    snap_status = str(payload.get("hffi_snap_status") or "none")
    categories = payload.get("hffi_staple_categories") or []
    if isinstance(categories, str):
        categories = [x for x in categories.split(",") if x]
    perishable = bool(int(payload.get("hffi_perishable_food") or 0))
    downstream_snap = bool(int(payload.get("hffi_downstream_snap_retail") or 0))
    prepared_primary = bool(int(payload.get("hffi_prepared_food_primary") or 0))
    charitable = bool(int(payload.get("hffi_charitable_free_food") or 0))
    preharvest = bool(int(payload.get("hffi_preharvest_primary") or 0))
    standalone_kitchen = bool(int(payload.get("hffi_standalone_kitchen") or 0))
    integrated_kitchen = bool(int(payload.get("hffi_kitchen_integrated_grocery") or 0))
    few_packaged_goods = bool(int(payload.get("hffi_few_packaged_goods_only") or 0))

    blockers: list[str] = []
    conditions: list[str] = []
    positives: list[str] = []

    if charitable:
        blockers.append("Primary model is free charitable food distribution, which sits outside the HFFI Partnerships project lane.")
    if preharvest:
        blockers.append("Primary model is pre-harvest agriculture or gardening, which is not an eligible HFFI project use.")
    if prepared_primary:
        blockers.append("Primary model centers on prepared meals, beverages, or snacks rather than staple and perishable food access.")
    if standalone_kitchen and not integrated_kitchen:
        blockers.append("Standalone kitchen/incubator model is not eligible unless the kitchen is necessary to a larger eligible retail or supply-chain business.")
    if few_packaged_goods:
        blockers.append("Business produces only one or a few consumer packaged goods without a broader staple/perishable retail or distribution model.")

    if project_type in RETAIL_TYPES:
        if not underserved:
            conditions.append("Confirm that the physical retail location is in an eligible underserved area.")
        else:
            positives.append("Retail location is identified as serving an underserved area.")
        if snap_status not in {"authorized", "will_apply"}:
            conditions.append("Direct-to-consumer retail must accept SNAP; add a documented SNAP authorization plan.")
        else:
            positives.append("SNAP requirement is addressed or planned.")
        if len(categories) < 2:
            conditions.append("Document a meaningful assortment across staple-food categories, not a narrow product mix.")
        else:
            positives.append("Multiple staple-food categories are included.")
        if not perishable:
            conditions.append("Add fresh, refrigerated, or frozen perishable staple foods.")
        else:
            positives.append("Perishable foods are included.")

    elif project_type in ENTERPRISE_TYPES:
        if not downstream_snap:
            conditions.append("Supply-chain enterprise must distribute staple/perishable foods to SNAP-authorized retailers in underserved areas.")
        else:
            positives.append("Downstream distribution to eligible SNAP retailers is identified.")
        if not perishable:
            conditions.append("Document how the enterprise increases availability of perishable staple foods.")
        else:
            positives.append("Perishable-food distribution is part of the model.")
    elif project_type in {"ghost_kitchen", "food_pantry", "urban_farm", "restaurant"}:
        if project_type == "ghost_kitchen" and integrated_kitchen:
            conditions.append("Frame the kitchen as a necessary component of an eligible grocery or supply-chain operation, not as a standalone incubator.")
        else:
            blockers.append("Selected project type is not independently aligned with the HFFI Partnerships eligible-project definition.")
    else:
        status = "Not screened"
        return {
            "status": status,
            "project_type": project_type,
            "positives": [],
            "conditions": [],
            "blockers": [],
            "disclaimer": "No HFFI food-retail or post-harvest supply-chain project type was selected.",
        }

    if blockers:
        status = "Not aligned"
    elif conditions:
        status = "Potentially eligible"
    else:
        status = "Eligible profile"

    return {
        "status": status,
        "project_type": project_type,
        "positives": positives,
        "conditions": conditions,
        "blockers": blockers,
        "disclaimer": "Program staff and counsel must verify final HFFI project and location eligibility before funding or technical assistance.",
    }
