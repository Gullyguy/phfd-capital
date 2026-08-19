from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from .base import CapitalProvider


class MockProvider(CapitalProvider):
    def __init__(self, slug: str, name: str) -> None:
        self.slug = slug
        self.name = name

    async def submit(self, application: dict[str, Any]) -> dict[str, Any]:
        raw = f"{self.slug}:{application['id']}".encode()
        external_id = hashlib.sha256(raw).hexdigest()[:14].upper()
        return {
            "mode": "sandbox-mock",
            "provider": self.name,
            "external_id": external_id,
            "status": "Prepared for partner review",
            "submitted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "message": "No live lender data was transmitted. Configure credentials and execute a signed partner agreement before enabling live submission.",
        }
