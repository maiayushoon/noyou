"""Offline demo connector — makes the whole product runnable with zero keys.

It deterministically synthesizes a realistic, varied mix of mentions (positive,
neutral, negative, and a few genuinely risky ones) for any query, across several
fake sources. Deterministic per (query, source) so repeated scans dedupe cleanly,
with a rotating slice so each scan can also surface something new.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from .base import BaseConnector, RawMention

# (source, template, author) — templates use {name}.
_TEMPLATES: list[tuple[str, str, str]] = [
    ("google", "{name} delivered an outstanding keynote — truly inspiring and professional.", "TechDaily"),
    ("google", "Customers praise {name}: 'reliable, honest, and the best in the business.'", "ReviewHub"),
    ("twitter", "Just met {name} at the conference. Super talented and kind!", "@dev_anna"),
    ("twitter", "Honestly disappointed by {name}, the service was poor and slow.", "@frustrated_user"),
    ("twitter", "Why is everyone hyping {name}? Total scam if you ask me. Avoid.", "@skeptic22"),
    ("reddit", "Has anyone worked with {name}? Heard mixed things, some say unprofessional.", "u/careerthrow"),
    ("reddit", "{name} was incredibly helpful when I reached out. Highly recommend.", "u/grateful_dev"),
    ("news", "Local report: {name} named in a lawsuit over alleged contract fraud.", "City News"),
    ("news", "{name} wins industry award for innovation and community leadership.", "Business Wire"),
    ("youtube", "Review: working with {name} — pros, cons, and honest thoughts.", "CreatorChannel"),
    ("blog", "I had a terrible experience with {name}. Felt cheated and ignored. Be warned.", "consumerblog"),
    ("forum", "Old thread resurfaced claiming {name} leaked private data of clients.", "anon_forum"),
    ("google", "{name} featured as a rising leader in this year's '30 under 30'.", "ProfileMag"),
    ("twitter", "{name} is overrated but not bad. Mediocre at best.", "@neutral_takes"),
    ("reddit", "PSA: someone is impersonating {name} online — verify before trusting.", "u/modteam"),
]


class DemoConnector(BaseConnector):
    name = "demo"
    label = "Demo (synthetic)"

    def search(self, query: str, *, limit: int = 25) -> list[RawMention]:
        name = query.strip() or "the subject"
        # Rotate the starting offset by a stable hash of the query so different
        # accounts get different-looking feeds, but the same account is consistent.
        seed = int(hashlib.sha256(name.encode()).hexdigest(), 16)
        offset = seed % len(_TEMPLATES)

        mentions: list[RawMention] = []
        now = datetime.now(timezone.utc)
        for i in range(min(limit, len(_TEMPLATES))):
            source, template, author = _TEMPLATES[(offset + i) % len(_TEMPLATES)]
            content = template.format(name=name)
            ext_id = hashlib.sha1(f"{source}:{content}".encode()).hexdigest()[:16]
            mentions.append(
                RawMention(
                    source=source,
                    external_id=ext_id,
                    content=content,
                    title=content[:60],
                    url=f"https://example.com/{source}/{ext_id}",
                    author=author,
                    published_at=now - timedelta(days=(i * 3) % 90, hours=i),
                )
            )
        return mentions
