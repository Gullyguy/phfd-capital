# PHFD Capital MVP API Specification

## `GET /health`

Returns service state.

```json
{"status":"ok","service":"phfd-capital","mode":"sandbox-first"}
```

## `POST /api/v1/assess`

Produces a non-binding readiness assessment, HFFI profile, and partner matches without storing the request.

### Example request

```json
{
  "years_in_business": 3,
  "monthly_revenue": 25000,
  "monthly_expenses": 14000,
  "cash_balance": 30000,
  "avg_daily_balance": 18000,
  "existing_monthly_debt": 900,
  "requested_amount": 35000,
  "requested_term_months": 24,
  "nsf_count_90d": 0,
  "revenue_volatility": "moderate",
  "documents_ready": 1,
  "training_completed": 1,
  "bank_data_consent": 1,
  "partner_data_consent": 1,
  "hffi_project_type": "food_coop",
  "hffi_underserved_area": 1,
  "hffi_snap_status": "will_apply",
  "hffi_staple_categories": ["fruits_vegetables", "bread_cereal", "dairy"],
  "hffi_perishable_food": 1
}
```

### Example response shape

```json
{
  "underwriting": {
    "score": 85,
    "band": "Partner-ready",
    "recommended_amount": 35000,
    "reasons": [],
    "strengths": [],
    "metrics": {},
    "disclaimer": "..."
  },
  "hffi": {
    "status": "Eligible profile",
    "positives": [],
    "conditions": [],
    "blockers": [],
    "disclaimer": "..."
  },
  "partner_matches": []
}
```

## Admin authentication

The MVP uses HTTP Basic Auth for local demonstration only.

Environment variables:

- `PHFD_ADMIN_USER`
- `PHFD_ADMIN_PASSWORD`

Production must replace Basic Auth with MFA-capable identity and role controls.

## Provider mode

Default:

```text
LIVE_PROVIDER_MODE=false
```

Provider submissions create sandbox references and transmit no data. Do not enable live mode until provider credentials, required application data, signed agreements, security controls, and legal review are complete.
