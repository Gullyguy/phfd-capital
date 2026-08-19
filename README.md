# PHFD Capital MVP

A working, sandbox-first business capital platform for:

- Capital readiness intake
- Explainable, non-binding readiness scoring
- HFFI food-retail/supply-chain profile screening
- White-label capital partner matching
- Human review and notes
- Partner submission adapters
- Audit trail
- Portfolio dashboard and CSV export

## Run locally

```bash
cd phfd-capital-mvp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
./start.sh
```

Open:

- Public platform: `http://localhost:8000`
- Capital intake: `http://localhost:8000/apply`
- Admin: `http://localhost:8000/admin`
- API documentation: `http://localhost:8000/docs`

Default local admin:

```text
username: admin
password: change-me-now
```

Change those credentials before any shared demonstration.

## Run tests

```bash
pytest -q
```

## Seed demonstration profiles

```bash
python seed_demo.py
```

## Safety boundary

This application does not currently make, broker, approve, deny, or promise loans. Default provider mode is a sandbox mock that transmits no applicant data. Live lending requires a signed provider agreement, credentials, legal review, required disclosures, production authentication, encryption, privacy controls, and applicant consent.

## Documentation

- `docs/DESIGN_DOCUMENT.md`
- `docs/PARTNER_OUTREACH_PACKET.md`
- `docs/COMPLIANCE_CHECKLIST.md`
- `docs/PRIVACY_AND_DISCLOSURE_IMPLEMENTATION.md`
- `docs/API_SPEC.md`
- `VENDOR_MATRIX.csv`
- `docs/FIREBASE_DEPLOYMENT.md`

## Firebase production architecture

The repository includes a Cloud Run container, Firebase Hosting rewrite, Firestore persistence adapter, Cloud Build pipeline, and deployment runbook. Production uses `PHFD_USE_FIRESTORE=true`; local development continues using SQLite. Live provider mode stays disabled.
