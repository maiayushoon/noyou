"""The data-source contract.

Every place we look for mentions — Google, X/Twitter, Reddit, YouTube, LinkedIn,
or the offline demo generator — implements ``BaseConnector.search`` and yields
``RawMention`` records. The scanning service treats them all identically, so adding
a new source is: write one class, register it. Nothing downstream changes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RawMention:
    """A normalized mention from any source, before AI analysis or persistence."""

    source: str
    external_id: str                     # stable id from the source for de-duplication
    content: str
    url: str | None = None
    title: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    extra: dict = field(default_factory=dict)


class BaseConnector(ABC):
    #: short id used in config (CONNECTORS=...) and stored on mentions
    name: str = "base"
    #: human label for the UI
    label: str = "Base"

    #: whether this connector can run with the current config (keys present, etc.)
    def is_configured(self) -> bool:  # noqa: D401 - simple predicate
        return True

    @abstractmethod
    def search(self, query: str, *, limit: int = 25) -> list[RawMention]:
        """Return mentions matching ``query`` (a name, handle, or brand term)."""
        raise NotImplementedError
