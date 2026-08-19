from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("PHFD_DB_PATH", BASE_DIR / "data" / "phfd_capital.db"))
USE_FIRESTORE = os.getenv("PHFD_USE_FIRESTORE", "false").lower() == "true"


def firestore_db():
    from google.cloud import firestore
    return firestore.Client()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def connect() -> Iterable[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    if USE_FIRESTORE:
        return
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'New',
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                business_name TEXT NOT NULL,
                legal_structure TEXT,
                state TEXT NOT NULL DEFAULT 'CO',
                zip_code TEXT,
                industry TEXT,
                business_type TEXT,
                years_in_business REAL NOT NULL DEFAULT 0,
                monthly_revenue REAL NOT NULL DEFAULT 0,
                monthly_expenses REAL NOT NULL DEFAULT 0,
                cash_balance REAL NOT NULL DEFAULT 0,
                avg_daily_balance REAL NOT NULL DEFAULT 0,
                existing_monthly_debt REAL NOT NULL DEFAULT 0,
                requested_amount REAL NOT NULL DEFAULT 0,
                requested_term_months INTEGER NOT NULL DEFAULT 24,
                loan_purpose TEXT,
                nsf_count_90d INTEGER NOT NULL DEFAULT 0,
                revenue_volatility TEXT NOT NULL DEFAULT 'moderate',
                documents_ready INTEGER NOT NULL DEFAULT 0,
                training_completed INTEGER NOT NULL DEFAULT 0,
                bank_data_consent INTEGER NOT NULL DEFAULT 0,
                partner_data_consent INTEGER NOT NULL DEFAULT 0,
                hffi_project_type TEXT,
                hffi_underserved_area INTEGER NOT NULL DEFAULT 0,
                hffi_snap_status TEXT,
                hffi_staple_categories TEXT,
                hffi_perishable_food INTEGER NOT NULL DEFAULT 0,
                hffi_downstream_snap_retail INTEGER NOT NULL DEFAULT 0,
                hffi_prepared_food_primary INTEGER NOT NULL DEFAULT 0,
                hffi_charitable_free_food INTEGER NOT NULL DEFAULT 0,
                hffi_preharvest_primary INTEGER NOT NULL DEFAULT 0,
                hffi_standalone_kitchen INTEGER NOT NULL DEFAULT 0,
                hffi_kitchen_integrated_grocery INTEGER NOT NULL DEFAULT 0,
                hffi_few_packaged_goods_only INTEGER NOT NULL DEFAULT 0,
                hffi_notes TEXT,
                readiness_score INTEGER,
                readiness_band TEXT,
                recommended_amount REAL,
                score_reasons TEXT,
                score_strengths TEXT,
                hffi_result TEXT,
                partner_matches TEXT,
                provider_submissions TEXT,
                reviewer_notes TEXT
            );

            CREATE TABLE IF NOT EXISTS partners (
                slug TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                priority INTEGER NOT NULL DEFAULT 99,
                status TEXT NOT NULL DEFAULT 'Researching',
                fit_summary TEXT,
                contact_method TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                website TEXT,
                notes TEXT,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id TEXT,
                created_at TEXT NOT NULL,
                actor TEXT NOT NULL,
                event_type TEXT NOT NULL,
                detail TEXT,
                FOREIGN KEY(application_id) REFERENCES applications(id) ON DELETE CASCADE
            );
            """
        )


def seed_partners() -> None:
    now = utc_now()
    partners = [
        {
            "slug": "youlend",
            "name": "YouLend",
            "category": "Managed embedded capital",
            "priority": 1,
            "fit_summary": "Fastest managed-capital pilot candidate; no-code, embedded components, and custom API paths.",
            "contact_method": "Email partnership team or use partner contact form",
            "contact_email": "partnership@youlend.com",
            "contact_phone": "+1 332 345 8560",
            "website": "https://youlend.com/us/company/contact",
            "notes": "Ask whether PHFD's community network and bank-data consent model meet U.S. pilot requirements.",
        },
        {
            "slug": "lendflow",
            "name": "Lendflow",
            "category": "White-label multi-lender marketplace",
            "priority": 2,
            "fit_summary": "Broad product marketplace and fully branded application journey; best near-term route to multiple lender options.",
            "contact_method": "Book demo / contact sales form",
            "contact_email": "",
            "contact_phone": "",
            "website": "https://www.lendflow.com/contact-us",
            "notes": "Confirm paid plan, lender waterfall, Colorado coverage, adverse-action ownership, and revenue-share economics.",
        },
        {
            "slug": "kanmon",
            "name": "Kanmon",
            "category": "Full-stack embedded working capital",
            "priority": 3,
            "fit_summary": "Handles underwriting, compliance, capital, servicing, and collections under the partner's brand.",
            "contact_method": "Email / partner conversation",
            "contact_email": "hello@kanmon.com",
            "contact_phone": "",
            "website": "https://kanmon.com/contact/",
            "notes": "Best once PHFD has recurring merchant activity and observable operating or transaction data.",
        },
        {
            "slug": "parafin",
            "name": "Parafin",
            "category": "Turnkey embedded capital",
            "priority": 4,
            "fit_summary": "Full managed program with term and revenue-based products; strong fit after PHFD builds merchant data and scale.",
            "contact_method": "Contact sales form",
            "contact_email": "",
            "contact_phone": "",
            "website": "https://www.parafin.com/contact",
            "notes": "Ask about minimum merchant count, transaction-data requirements, community-platform pilots, and Celtic Bank coverage.",
        },
        {
            "slug": "loanwell",
            "name": "LoanWell",
            "category": "Community-lender operating system",
            "priority": 5,
            "fit_summary": "White-label intake, underwriting, e-sign, ACH, KYC, servicing, reporting; best for PHFD-owned microfund/CDFI path.",
            "contact_method": "Email sales / book demo",
            "contact_email": "sales@loanwell.com",
            "contact_phone": "",
            "website": "https://loanwell.com/pages/other-pages/contact.html",
            "notes": "Technology, not loan capital. Evaluate after counsel approves PHFD's own business-purpose microloan pilot.",
        },
        {
            "slug": "sivo",
            "name": "Sivo",
            "category": "Debt capital infrastructure",
            "priority": 6,
            "fit_summary": "Potential later-stage debt capital source for a PHFD lending program; not the first borrower-facing pilot.",
            "contact_method": "Book a meeting",
            "contact_email": "",
            "contact_phone": "",
            "website": "https://www.sivo.com/debt-as-a-service",
            "notes": "Explore only after PHFD has legal lending structure, servicing stack, underwriting history, and portfolio performance.",
        },
    ]
    if USE_FIRESTORE:
        client = firestore_db()
        for p in partners:
            ref = client.collection("partners").document(p["slug"])
            current = ref.get()
            payload = {**p, "updated_at": now}
            if current.exists:
                payload["status"] = current.to_dict().get("status", "Researching")
            else:
                payload["status"] = "Researching"
            ref.set(payload, merge=True)
        return
    with connect() as conn:
        for p in partners:
            conn.execute(
                """
                INSERT INTO partners (
                    slug, name, category, priority, status, fit_summary,
                    contact_method, contact_email, contact_phone, website, notes, updated_at
                ) VALUES (?, ?, ?, ?, 'Researching', ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    name=excluded.name,
                    category=excluded.category,
                    priority=excluded.priority,
                    fit_summary=excluded.fit_summary,
                    contact_method=excluded.contact_method,
                    contact_email=excluded.contact_email,
                    contact_phone=excluded.contact_phone,
                    website=excluded.website,
                    notes=excluded.notes
                """,
                (
                    p["slug"], p["name"], p["category"], p["priority"],
                    p["fit_summary"], p["contact_method"], p["contact_email"],
                    p["contact_phone"], p["website"], p["notes"], now,
                ),
            )


def _json(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def create_application(payload: dict[str, Any], analysis: dict[str, Any]) -> str:
    app_id = str(uuid.uuid4())
    now = utc_now()
    fields = {
        **payload,
        "id": app_id,
        "created_at": now,
        "updated_at": now,
        "status": "New",
        "readiness_score": analysis["underwriting"]["score"],
        "readiness_band": analysis["underwriting"]["band"],
        "recommended_amount": analysis["underwriting"]["recommended_amount"],
        "score_reasons": _json(analysis["underwriting"]["reasons"]),
        "score_strengths": _json(analysis["underwriting"]["strengths"]),
        "hffi_result": _json(analysis["hffi"]),
        "partner_matches": _json(analysis["partner_matches"]),
        "provider_submissions": _json({}),
        "reviewer_notes": "",
    }

    if USE_FIRESTORE:
        firestore_fields = dict(fields)
        firestore_fields.update({
            "score_reasons": analysis["underwriting"]["reasons"],
            "score_strengths": analysis["underwriting"]["strengths"],
            "hffi_result": analysis["hffi"],
            "partner_matches": analysis["partner_matches"],
            "provider_submissions": {},
            "hffi_staple_categories": [x for x in str(payload.get("hffi_staple_categories", "")).split(",") if x],
        })
        client = firestore_db()
        client.collection("applications").document(app_id).set(firestore_fields)
        client.collection("applications").document(app_id).collection("audit_events").add({
            "application_id": app_id, "created_at": now, "actor": "system",
            "event_type": "application_created", "detail": {"score": analysis["underwriting"]["score"]},
        })
        return app_id
    columns = list(fields.keys())
    placeholders = ",".join("?" for _ in columns)
    values = [fields[c] for c in columns]
    with connect() as conn:
        conn.execute(
            f"INSERT INTO applications ({','.join(columns)}) VALUES ({placeholders})",
            values,
        )
        conn.execute(
            "INSERT INTO audit_events (application_id, created_at, actor, event_type, detail) VALUES (?, ?, ?, ?, ?)",
            (app_id, now, "system", "application_created", _json({"score": analysis["underwriting"]["score"]})),
        )
    return app_id


def _decode_application(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    for key in ["score_reasons", "score_strengths", "hffi_result", "partner_matches", "provider_submissions"]:
        try:
            data[key] = json.loads(data.get(key) or "{}")
        except json.JSONDecodeError:
            data[key] = {} if key not in ("score_reasons", "score_strengths", "partner_matches") else []
    data["hffi_staple_categories"] = [
        x for x in (data.get("hffi_staple_categories") or "").split(",") if x
    ]
    return data


def get_application(app_id: str) -> dict[str, Any] | None:
    if USE_FIRESTORE:
        snap = firestore_db().collection("applications").document(app_id).get()
        return snap.to_dict() if snap.exists else None
    with connect() as conn:
        row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    return _decode_application(row)


def list_applications(limit: int = 250) -> list[dict[str, Any]]:
    if USE_FIRESTORE:
        query = firestore_db().collection("applications").order_by("created_at", direction="DESCENDING").limit(limit)
        return [snap.to_dict() for snap in query.stream()]
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM applications ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [_decode_application(r) for r in rows if r is not None]


def update_application_status(app_id: str, status: str, reviewer_notes: str, actor: str = "admin") -> None:
    now = utc_now()
    if USE_FIRESTORE:
        ref = firestore_db().collection("applications").document(app_id)
        ref.update({"status": status, "reviewer_notes": reviewer_notes, "updated_at": now})
        ref.collection("audit_events").add({"application_id": app_id, "created_at": now, "actor": actor, "event_type": "status_updated", "detail": {"status": status, "notes": reviewer_notes}})
        return
    with connect() as conn:
        conn.execute(
            "UPDATE applications SET status=?, reviewer_notes=?, updated_at=? WHERE id=?",
            (status, reviewer_notes, now, app_id),
        )
        conn.execute(
            "INSERT INTO audit_events (application_id, created_at, actor, event_type, detail) VALUES (?, ?, ?, ?, ?)",
            (app_id, now, actor, "status_updated", _json({"status": status, "notes": reviewer_notes})),
        )


def update_provider_submission(app_id: str, provider_slug: str, result: dict[str, Any], actor: str = "admin") -> None:
    now = utc_now()
    if USE_FIRESTORE:
        client = firestore_db(); ref = client.collection("applications").document(app_id)
        snap = ref.get(); current = (snap.to_dict() or {}).get("provider_submissions", {})
        current[provider_slug] = result
        ref.update({"provider_submissions": current, "updated_at": now})
        ref.collection("audit_events").add({"application_id": app_id, "created_at": now, "actor": actor, "event_type": "provider_submission", "detail": {"provider": provider_slug, "result": result}})
        return
    with connect() as conn:
        row = conn.execute("SELECT provider_submissions FROM applications WHERE id=?", (app_id,)).fetchone()
        current = json.loads((row[0] if row else None) or "{}")
        current[provider_slug] = result
        conn.execute(
            "UPDATE applications SET provider_submissions=?, updated_at=? WHERE id=?",
            (_json(current), now, app_id),
        )
        conn.execute(
            "INSERT INTO audit_events (application_id, created_at, actor, event_type, detail) VALUES (?, ?, ?, ?, ?)",
            (app_id, now, actor, "provider_submission", _json({"provider": provider_slug, "result": result})),
        )


def list_partners() -> list[dict[str, Any]]:
    if USE_FIRESTORE:
        return [snap.to_dict() for snap in firestore_db().collection("partners").order_by("priority").stream()]
    with connect() as conn:
        rows = conn.execute("SELECT * FROM partners ORDER BY priority, name").fetchall()
    return [dict(r) for r in rows]


def get_partner(slug: str) -> dict[str, Any] | None:
    if USE_FIRESTORE:
        snap = firestore_db().collection("partners").document(slug).get()
        return snap.to_dict() if snap.exists else None
    with connect() as conn:
        row = conn.execute("SELECT * FROM partners WHERE slug=?", (slug,)).fetchone()
    return dict(row) if row else None


def update_partner_status(slug: str, status: str, notes: str | None = None) -> None:
    now = utc_now()
    if USE_FIRESTORE:
        values = {"status": status, "updated_at": now}
        if notes is not None: values["notes"] = notes
        firestore_db().collection("partners").document(slug).update(values)
        return
    with connect() as conn:
        if notes is None:
            conn.execute("UPDATE partners SET status=?, updated_at=? WHERE slug=?", (status, now, slug))
        else:
            conn.execute("UPDATE partners SET status=?, notes=?, updated_at=? WHERE slug=?", (status, notes, now, slug))


def dashboard_metrics() -> dict[str, Any]:
    if USE_FIRESTORE:
        applications = list_applications(limit=10000)
        by_status: dict[str, int] = {}
        for item in applications:
            state = item.get("status", "New"); by_status[state] = by_status.get(state, 0) + 1
        scores = [float(item.get("readiness_score") or 0) for item in applications]
        return {
            "total_applications": len(applications),
            "total_requested": sum(float(item.get("requested_amount") or 0) for item in applications),
            "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
            "hffi_eligible_profiles": sum(1 for item in applications if (item.get("hffi_result") or {}).get("status") == "Eligible profile"),
            "by_status": by_status,
        }
    with connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        requested = conn.execute("SELECT COALESCE(SUM(requested_amount),0) FROM applications").fetchone()[0]
        avg_score = conn.execute("SELECT COALESCE(AVG(readiness_score),0) FROM applications").fetchone()[0]
        by_status = conn.execute(
            "SELECT status, COUNT(*) AS c FROM applications GROUP BY status ORDER BY c DESC"
        ).fetchall()
        hffi_count = 0
        for row in conn.execute("SELECT hffi_result FROM applications").fetchall():
            try:
                result = json.loads(row[0] or "{}")
                if result.get("status") == "Eligible profile":
                    hffi_count += 1
            except json.JSONDecodeError:
                pass
    return {
        "total_applications": total,
        "total_requested": float(requested or 0),
        "average_score": round(float(avg_score or 0), 1),
        "hffi_eligible_profiles": hffi_count,
        "by_status": {r["status"]: r["c"] for r in by_status},
    }


def audit_events(app_id: str) -> list[dict[str, Any]]:
    if USE_FIRESTORE:
        query = firestore_db().collection("applications").document(app_id).collection("audit_events").order_by("created_at", direction="DESCENDING")
        return [snap.to_dict() for snap in query.stream()]
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_events WHERE application_id=? ORDER BY id DESC", (app_id,)
        ).fetchall()
    events = []
    for r in rows:
        item = dict(r)
        try:
            item["detail"] = json.loads(item.get("detail") or "{}")
        except json.JSONDecodeError:
            pass
        events.append(item)
    return events
