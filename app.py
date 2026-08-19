from __future__ import annotations

import csv
import io
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field

import db
import hffi
import routing
import underwriting
from providers import ProviderError, get_provider

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    db.seed_partners()
    yield


app = FastAPI(
    title="PHFD Capital",
    description=(
        "Business-purpose capital readiness, HFFI profile screening, partner routing, "
        "and portfolio workflow for PHFD Community Capital."
    ),
    version="0.1.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
security = HTTPBasic(auto_error=False)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    return response

ADMIN_USER = os.getenv("PHFD_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("PHFD_ADMIN_PASSWORD", "change-me-now")

STATUS_OPTIONS = [
    "New",
    "Needs documents",
    "Capital readiness",
    "Manual review",
    "Partner review",
    "Referred",
    "Closed",
]

BOOL_FIELDS = {
    "documents_ready",
    "training_completed",
    "bank_data_consent",
    "partner_data_consent",
    "hffi_underserved_area",
    "hffi_perishable_food",
    "hffi_downstream_snap_retail",
    "hffi_prepared_food_primary",
    "hffi_charitable_free_food",
    "hffi_preharvest_primary",
    "hffi_standalone_kitchen",
    "hffi_kitchen_integrated_grocery",
    "hffi_few_packaged_goods_only",
}

FLOAT_FIELDS = {
    "years_in_business",
    "monthly_revenue",
    "monthly_expenses",
    "cash_balance",
    "avg_daily_balance",
    "existing_monthly_debt",
    "requested_amount",
}

INT_FIELDS = {"requested_term_months", "nsf_count_90d"}


class AssessmentRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    years_in_business: float = Field(default=0, ge=0)
    monthly_revenue: float = Field(default=0, ge=0)
    monthly_expenses: float = Field(default=0, ge=0)
    cash_balance: float = Field(default=0, ge=0)
    avg_daily_balance: float = Field(default=0, ge=0)
    existing_monthly_debt: float = Field(default=0, ge=0)
    requested_amount: float = Field(default=0, ge=0)
    requested_term_months: int = Field(default=24, ge=3, le=84)
    nsf_count_90d: int = Field(default=0, ge=0)
    revenue_volatility: str = "moderate"
    documents_ready: int = 0
    training_completed: int = 0
    bank_data_consent: int = 0
    partner_data_consent: int = 0
    hffi_project_type: str = ""
    hffi_underserved_area: int = 0
    hffi_snap_status: str = "none"
    hffi_staple_categories: list[str] = Field(default_factory=list)
    hffi_perishable_food: int = 0
    hffi_downstream_snap_retail: int = 0
    hffi_prepared_food_primary: int = 0
    hffi_charitable_free_food: int = 0
    hffi_preharvest_primary: int = 0
    hffi_standalone_kitchen: int = 0
    hffi_kitchen_integrated_grocery: int = 0
    hffi_few_packaged_goods_only: int = 0


def authenticate_admin(credentials: HTTPBasicCredentials | None = Depends(security)) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin credentials required",
            headers={"WWW-Authenticate": "Basic"},
        )
    username_ok = secrets.compare_digest(credentials.username.encode(), ADMIN_USER.encode())
    password_ok = secrets.compare_digest(credentials.password.encode(), ADMIN_PASSWORD.encode())
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def money(value: Any) -> str:
    try:
        return "${:,.0f}".format(float(value or 0))
    except (TypeError, ValueError):
        return "$0"


def percent(value: Any) -> str:
    try:
        return "{:.0f}%".format(float(value or 0))
    except (TypeError, ValueError):
        return "0%"


templates.env.filters["money"] = money
templates.env.filters["percent"] = percent


def _clean_text(value: Any, max_length: int = 2000) -> str:
    return str(value or "").strip()[:max_length]


def _to_float(value: Any) -> float:
    try:
        return max(float(value or 0), 0.0)
    except (TypeError, ValueError):
        return 0.0


def _to_int(value: Any) -> int:
    try:
        return max(int(float(value or 0)), 0)
    except (TypeError, ValueError):
        return 0


def analyze_payload(payload: dict[str, Any]) -> dict[str, Any]:
    uw = underwriting.assess(payload).as_dict()
    return {
        "underwriting": uw,
        "hffi": hffi.evaluate(payload),
        "partner_matches": routing.match_partners(payload, uw),
    }


async def form_payload(request: Request) -> dict[str, Any]:
    form = await request.form()
    payload: dict[str, Any] = {}

    for key in db_application_columns():
        if key in BOOL_FIELDS:
            payload[key] = 1 if form.get(key) in {"1", "true", "on", "yes"} else 0
        elif key in FLOAT_FIELDS:
            payload[key] = _to_float(form.get(key))
        elif key in INT_FIELDS:
            payload[key] = _to_int(form.get(key))
        elif key == "hffi_staple_categories":
            payload[key] = ",".join(_clean_text(v, 50) for v in form.getlist(key))
        elif key in form:
            payload[key] = _clean_text(form.get(key))

    payload.setdefault("state", "CO")
    payload.setdefault("requested_term_months", 24)
    payload.setdefault("revenue_volatility", "moderate")
    payload.setdefault("hffi_snap_status", "none")
    payload.setdefault("hffi_staple_categories", "")
    for key in BOOL_FIELDS:
        payload.setdefault(key, 0)

    required = ["first_name", "last_name", "email", "business_name"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing required fields: {', '.join(missing)}")
    if "@" not in payload["email"]:
        raise HTTPException(status_code=422, detail="Enter a valid email address")
    if payload.get("requested_amount", 0) <= 0:
        raise HTTPException(status_code=422, detail="Requested amount must be greater than zero")
    return payload


def db_application_columns() -> set[str]:
    return {
        "first_name", "last_name", "email", "phone", "business_name", "legal_structure",
        "state", "zip_code", "industry", "business_type", "years_in_business", "monthly_revenue",
        "monthly_expenses", "cash_balance", "avg_daily_balance", "existing_monthly_debt",
        "requested_amount", "requested_term_months", "loan_purpose", "nsf_count_90d",
        "revenue_volatility", "documents_ready", "training_completed", "bank_data_consent",
        "partner_data_consent", "hffi_project_type", "hffi_underserved_area", "hffi_snap_status",
        "hffi_staple_categories", "hffi_perishable_food", "hffi_downstream_snap_retail",
        "hffi_prepared_food_primary", "hffi_charitable_free_food", "hffi_preharvest_primary",
        "hffi_standalone_kitchen", "hffi_kitchen_integrated_grocery",
        "hffi_few_packaged_goods_only", "hffi_notes",
    }


@app.get("/health", response_class=JSONResponse)
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "phfd-capital", "mode": "sandbox-first"}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"mode": "Business-purpose capital readiness"},
    )


@app.get("/apply", response_class=HTMLResponse)
async def apply_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="apply.html", context={})


@app.get("/privacy", response_class=HTMLResponse)
async def privacy_notice(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="privacy.html", context={})


@app.get("/disclosures", response_class=HTMLResponse)
async def capital_disclosures(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="disclosures.html", context={})


@app.post("/apply", response_class=HTMLResponse)
async def submit_application(request: Request) -> RedirectResponse:
    payload = await form_payload(request)
    analysis = analyze_payload(payload)
    app_id = db.create_application(payload, analysis)
    return RedirectResponse(url=f"/result/{app_id}", status_code=303)


@app.get("/result/{app_id}", response_class=HTMLResponse)
async def result(request: Request, app_id: str) -> HTMLResponse:
    application = db.get_application(app_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={"application": application},
    )


@app.post("/api/v1/assess", response_class=JSONResponse)
async def api_assess(body: AssessmentRequest) -> dict[str, Any]:
    payload = body.model_dump()
    if isinstance(payload.get("hffi_staple_categories"), list):
        # HFFI evaluator accepts a list; database storage is not involved here.
        pass
    return analyze_payload(payload)


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin: str = Depends(authenticate_admin)) -> HTMLResponse:
    applications = db.list_applications()
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "admin": admin,
            "metrics": db.dashboard_metrics(),
            "applications": applications,
            "status_options": STATUS_OPTIONS,
        },
    )


@app.get("/admin/applications/{app_id}", response_class=HTMLResponse)
async def admin_application(
    request: Request,
    app_id: str,
    admin: str = Depends(authenticate_admin),
) -> HTMLResponse:
    application = db.get_application(app_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return templates.TemplateResponse(
        request=request,
        name="application.html",
        context={
            "admin": admin,
            "application": application,
            "events": db.audit_events(app_id),
            "status_options": STATUS_OPTIONS,
        },
    )


@app.post("/admin/applications/{app_id}/status")
async def set_status(
    app_id: str,
    status_value: str = Form(...),
    reviewer_notes: str = Form(""),
    admin: str = Depends(authenticate_admin),
) -> RedirectResponse:
    if status_value not in STATUS_OPTIONS:
        raise HTTPException(status_code=400, detail="Invalid status")
    if db.get_application(app_id) is None:
        raise HTTPException(status_code=404, detail="Application not found")
    db.update_application_status(app_id, status_value, reviewer_notes[:5000], actor=admin)
    return RedirectResponse(url=f"/admin/applications/{app_id}", status_code=303)


@app.post("/admin/applications/{app_id}/submit/{provider_slug}")
async def submit_provider(
    app_id: str,
    provider_slug: str,
    admin: str = Depends(authenticate_admin),
) -> RedirectResponse:
    application = db.get_application(app_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    if not application.get("partner_data_consent"):
        raise HTTPException(status_code=400, detail="Applicant has not consented to partner data sharing")
    try:
        provider = get_provider(provider_slug)
        response = await provider.submit(application)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProviderError as exc:
        response = {"mode": "error", "status": "Not submitted", "message": str(exc)}
    db.update_provider_submission(app_id, provider_slug, response, actor=admin)
    return RedirectResponse(url=f"/admin/applications/{app_id}", status_code=303)


@app.get("/admin/partners", response_class=HTMLResponse)
async def partners(request: Request, admin: str = Depends(authenticate_admin)) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="partners.html",
        context={"admin": admin, "partners": db.list_partners()},
    )


@app.post("/admin/partners/{slug}/status")
async def partner_status(
    slug: str,
    status_value: str = Form(...),
    notes: str = Form(""),
    admin: str = Depends(authenticate_admin),
) -> RedirectResponse:
    del admin
    if db.get_partner(slug) is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    db.update_partner_status(slug, status_value[:80], notes[:5000])
    return RedirectResponse(url="/admin/partners", status_code=303)


@app.get("/admin/export.csv")
async def export_csv(admin: str = Depends(authenticate_admin)) -> StreamingResponse:
    del admin
    output = io.StringIO()
    fieldnames = [
        "id", "created_at", "status", "first_name", "last_name", "email", "business_name",
        "zip_code", "industry", "years_in_business", "monthly_revenue", "requested_amount",
        "readiness_score", "readiness_band", "recommended_amount", "hffi_status",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for item in db.list_applications(limit=10000):
        writer.writerow({
            **{k: item.get(k) for k in fieldnames if k != "hffi_status"},
            "hffi_status": (item.get("hffi_result") or {}).get("status", ""),
        })
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=phfd-capital-applications.csv"},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api/") or "application/json" in request.headers.get("accept", ""):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"status_code": exc.status_code, "detail": exc.detail},
        status_code=exc.status_code,
        headers=exc.headers,
    )
