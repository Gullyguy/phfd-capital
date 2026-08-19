from __future__ import annotations

import db
import hffi
import routing
import underwriting


def add(payload):
    uw = underwriting.assess(payload).as_dict()
    analysis = {
        "underwriting": uw,
        "hffi": hffi.evaluate(payload),
        "partner_matches": routing.match_partners(payload, uw),
    }
    return db.create_application(payload, analysis)


def main():
    db.init_db()
    db.seed_partners()
    demos = [
        {
            "first_name":"Amina","last_name":"Johnson","email":"amina@example.org","phone":"303-555-0101",
            "business_name":"Northeast Community Food Co-op","legal_structure":"Cooperative","state":"CO","zip_code":"80207",
            "industry":"Healthy food retail","business_type":"retail","years_in_business":2.2,"monthly_revenue":32000,
            "monthly_expenses":18500,"cash_balance":48000,"avg_daily_balance":24000,"existing_monthly_debt":1200,
            "requested_amount":75000,"requested_term_months":36,"loan_purpose":"Refrigeration, inventory, and opening working capital",
            "nsf_count_90d":0,"revenue_volatility":"moderate","documents_ready":1,"training_completed":1,
            "bank_data_consent":1,"partner_data_consent":1,"hffi_project_type":"food_coop","hffi_underserved_area":1,
            "hffi_snap_status":"will_apply","hffi_staple_categories":"fruits_vegetables,dairy,bread_cereal,meat_fish",
            "hffi_perishable_food":1,"hffi_downstream_snap_retail":0,"hffi_prepared_food_primary":0,"hffi_charitable_free_food":0,
            "hffi_preharvest_primary":0,"hffi_standalone_kitchen":0,"hffi_kitchen_integrated_grocery":1,
            "hffi_few_packaged_goods_only":0,"hffi_notes":"Community-owned retail concept in Northeast Denver.",
        },
        {
            "first_name":"Marcus","last_name":"Lee","email":"marcus@example.org","phone":"720-555-0199",
            "business_name":"Front Range Fresh Distribution","legal_structure":"LLC","state":"CO","zip_code":"80216",
            "industry":"Food distribution","business_type":"distributor","years_in_business":4.5,"monthly_revenue":65000,
            "monthly_expenses":44000,"cash_balance":35000,"avg_daily_balance":19000,"existing_monthly_debt":3200,
            "requested_amount":120000,"requested_term_months":36,"loan_purpose":"Refrigerated vehicle and route expansion",
            "nsf_count_90d":1,"revenue_volatility":"moderate","documents_ready":1,"training_completed":0,
            "bank_data_consent":1,"partner_data_consent":1,"hffi_project_type":"distributor","hffi_underserved_area":0,
            "hffi_snap_status":"none","hffi_staple_categories":"fruits_vegetables,dairy","hffi_perishable_food":1,
            "hffi_downstream_snap_retail":1,"hffi_prepared_food_primary":0,"hffi_charitable_free_food":0,
            "hffi_preharvest_primary":0,"hffi_standalone_kitchen":0,"hffi_kitchen_integrated_grocery":0,
            "hffi_few_packaged_goods_only":0,"hffi_notes":"Supplies small SNAP-authorized retailers across Denver metro.",
        },
        {
            "first_name":"Tanya","last_name":"Reed","email":"tanya@example.org","phone":"720-555-0112",
            "business_name":"Reed Mobile Market","legal_structure":"LLC","state":"CO","zip_code":"80239",
            "industry":"Mobile food retail","business_type":"retail","years_in_business":0.7,"monthly_revenue":9000,
            "monthly_expenses":7200,"cash_balance":2500,"avg_daily_balance":1800,"existing_monthly_debt":450,
            "requested_amount":30000,"requested_term_months":24,"loan_purpose":"Vehicle equipment, refrigeration, and inventory",
            "nsf_count_90d":2,"revenue_volatility":"high","documents_ready":0,"training_completed":1,
            "bank_data_consent":1,"partner_data_consent":0,"hffi_project_type":"mobile_market","hffi_underserved_area":1,
            "hffi_snap_status":"will_apply","hffi_staple_categories":"fruits_vegetables,bread_cereal","hffi_perishable_food":1,
            "hffi_downstream_snap_retail":0,"hffi_prepared_food_primary":0,"hffi_charitable_free_food":0,
            "hffi_preharvest_primary":0,"hffi_standalone_kitchen":0,"hffi_kitchen_integrated_grocery":0,
            "hffi_few_packaged_goods_only":0,"hffi_notes":"Paid mobile market, not free pantry distribution.",
        },
        {
            "first_name":"Derrick","last_name":"Price","email":"derrick@example.org","phone":"303-555-0166",
            "business_name":"DP Neighborhood Services","legal_structure":"LLC","state":"CO","zip_code":"80205",
            "industry":"Property maintenance","business_type":"service","years_in_business":3.0,"monthly_revenue":21000,
            "monthly_expenses":12500,"cash_balance":14000,"avg_daily_balance":9500,"existing_monthly_debt":900,
            "requested_amount":20000,"requested_term_months":24,"loan_purpose":"Equipment and payroll bridge",
            "nsf_count_90d":0,"revenue_volatility":"low","documents_ready":1,"training_completed":1,
            "bank_data_consent":1,"partner_data_consent":1,"hffi_project_type":"","hffi_underserved_area":0,
            "hffi_snap_status":"none","hffi_staple_categories":"","hffi_perishable_food":0,"hffi_downstream_snap_retail":0,
            "hffi_prepared_food_primary":0,"hffi_charitable_free_food":0,"hffi_preharvest_primary":0,
            "hffi_standalone_kitchen":0,"hffi_kitchen_integrated_grocery":0,"hffi_few_packaged_goods_only":0,"hffi_notes":"",
        },
    ]
    for item in demos:
        add(item)
    print(f"Seeded {len(demos)} demo profiles into {db.DB_PATH}")


if __name__ == "__main__":
    main()
