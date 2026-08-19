from __future__ import annotations

import os
from typing import Any

import httpx

from .base import CapitalProvider, ProviderError


COMPANY_TYPE_MAP = {
    "llc": "LimitedLiabilityCompany",
    "corporation": "Corporation",
    "public benefit corporation": "Corporation",
    "cooperative": "Corporation",
    "nonprofit": "NonProfit",
    "sole proprietorship": "SoleTrader",
    "partnership": "Partnership",
}


class YouLendProvider(CapitalProvider):
    """YouLend Create Lead scaffold.

    The public MVP intentionally does not collect the complete U.S. KYC/business
    dataset required for a live lead. The adapter therefore fails closed unless
    every mandatory field is supplied by a production-grade secure workflow.
    """

    slug = "youlend"
    name = "YouLend"

    def __init__(self) -> None:
        self.base_url = os.getenv("YOULEND_BASE_URL", "https://partners.staging-youlendapi.com")
        self.token = os.getenv("YOULEND_ACCESS_TOKEN", "")
        self.api_version = os.getenv("YOULEND_API_VERSION", "1.0")

    async def submit(self, application: dict[str, Any]) -> dict[str, Any]:
        if not self.token:
            raise ProviderError("YOULEND_ACCESS_TOKEN is not configured")
        if not application.get("partner_data_consent"):
            raise ProviderError("Applicant has not consented to partner data sharing")

        required = {
            "phone": application.get("phone"),
            "employer_identification_number": application.get("employer_identification_number"),
            "registered_address_line1": application.get("registered_address_line1"),
            "registered_city": application.get("registered_city"),
            "zip_code": application.get("zip_code"),
            "state": application.get("state"),
            "signup_client_ip": application.get("signup_client_ip"),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ProviderError(
                "Live YouLend lead creation is blocked because the secure production workflow "
                f"has not supplied mandatory U.S. fields: {', '.join(missing)}"
            )

        legal_structure = str(application.get("legal_structure") or "").strip().lower()
        company_type = COMPANY_TYPE_MAP.get(legal_structure)
        if not company_type:
            raise ProviderError(f"No approved YouLend company-type mapping for: {legal_structure or 'blank'}")

        months_trading = max(0, round(float(application.get("years_in_business") or 0) * 12))
        key_contact = f"{application['first_name']} {application['last_name']}".strip()
        payload = {
            "thirdPartyCustomerId": application["id"],
            "thirdPartyLeadId": application["id"],
            "companyName": application["business_name"],
            "countryISOCode": "USA",
            "loanCurrencyISOCode": "USD",
            "keyContactName": key_contact,
            "companyType": company_type,
            "registeredAddress": {
                "line1": application["registered_address_line1"],
                "line2": application.get("registered_address_line2"),
                "city": application["registered_city"],
                "region": application["state"],
                "postalCode": application["zip_code"],
                "countryISOCode": "USA",
            },
            "contactPhoneNumber": application["phone"],
            "contactEmailAddress": application["email"],
            "confirmedCreditSearch": bool(application.get("confirmed_credit_search")),
            "monthlyCardRevenue": float(application.get("monthly_revenue") or 0),
            "monthsTrading": months_trading,
            "loanAmount": float(application.get("requested_amount") or 0),
            "companyWebsite": application.get("company_website"),
            "signupClientIp": application["signup_client_ip"],
            "employerIdentificationNumber": application["employer_identification_number"],
            "preferredLanguageCode": "en-US",
            "additionalInfo": {
                "phfdReadinessBand": application.get("readiness_band"),
                "phfdApplicationId": application.get("id"),
            },
        }
        headers = {
            "Authorization": f"Bearer {self.token}",
            "api-version": self.api_version,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{self.base_url}/onboarding/Leads", json=payload, headers=headers)
        if response.status_code >= 400:
            raise ProviderError(f"YouLend API returned {response.status_code}: {response.text[:500]}")
        data = response.json()
        return {
            "mode": "live",
            "provider": self.name,
            "status": "Lead created",
            "external_id": data.get("id") or data.get("leadId"),
            "signup_url": data.get("signUpURL") or data.get("signupURL"),
            "response": data,
        }
