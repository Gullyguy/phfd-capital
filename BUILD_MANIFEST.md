# PHFD Capital MVP Build Manifest

## Release status

- Build: 0.1 MVP
- Mode: Sandbox-first
- Product boundary: Business-purpose capital readiness, HFFI profile screening, human review, partner routing, portfolio intelligence
- Live lender data transmission: Disabled by default
- Consumer/personal lending: Not enabled

## Working modules

- Public landing page
- Five-step capital profile intake
- Explainable readiness score and reason codes
- HFFI food-retail and post-harvest supply-chain profile screen
- Ranked white-label partner routing
- Human-review dashboard
- Application status and reviewer notes
- Partner diligence room
- Audit events
- CSV export
- REST assessment endpoint and OpenAPI documentation
- Sandbox provider adapter
- Fail-closed YouLend adapter scaffold
- Four seeded demonstration profiles

## Validation

- Automated unit tests: 7 passing
- Smoke tests: `/health`, `/`, `/apply`, `/privacy`, `/disclosures`, `/admin`, and `/openapi.json` returned HTTP 200

## Production blockers

See `docs/COMPLIANCE_CHECKLIST.md` and `docs/DESIGN_DOCUMENT.md` before collecting sensitive financial data or activating a live capital provider.
