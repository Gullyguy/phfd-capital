from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProviderError(RuntimeError):
    pass


class CapitalProvider(ABC):
    slug: str
    name: str

    @abstractmethod
    async def submit(self, application: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
