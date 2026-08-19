from __future__ import annotations

import os

from .base import CapitalProvider
from .mock import MockProvider
from .youlend import YouLendProvider


PROVIDER_NAMES = {
    "youlend": "YouLend",
    "lendflow": "Lendflow",
    "kanmon": "Kanmon",
    "parafin": "Parafin",
    "loanwell": "LoanWell",
}


def get_provider(slug: str) -> CapitalProvider:
    live_mode = os.getenv("LIVE_PROVIDER_MODE", "false").lower() == "true"
    if live_mode and slug == "youlend":
        return YouLendProvider()
    if slug not in PROVIDER_NAMES:
        raise KeyError(f"Unknown provider: {slug}")
    return MockProvider(slug, PROVIDER_NAMES[slug])
