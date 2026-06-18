"""Scan orchestration — the pipeline that ties the whole product together.

For a user::

    accounts → connectors.search() → dedupe → persist Mention
            → analyzer.analyze() → persist Analysis
            → alerts + cleanup suggestions
            → recompute reputation score → notify

Public-launch hardening:
  * **Async execution** — the API creates a ``pending`` scan and runs the heavy,
    network-bound pipeline in a background task (``execute_scan``), so a slow scan
    never ties up the request worker. The scheduler still runs ``run_scan`` inline.
  * **Plan-scoped connectors** — a scan only uses sources the user's plan allows.
  * **Bounded work** — the number of search queries per scan is capped.
  * **URL sanitization** — only http/https URLs from external sources are stored,
    preventing ``javascript:`` (and similar) URLs from reaching the UI.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..analysis import get_analyzer
from ..analysis.base import AnalysisInput
from ..connectors import get_active_connectors
from ..connectors.demo import DemoConnector
from ..core.config import settings
from ..core.database import SessionLocal
from ..core.plans import plan_allows_connector
from ..models.account import Account
from ..models.analysis import Analysis
from ..models.mention import Mention
from ..models.scan import Scan
from ..models.user import User
from ..notifications import dispatch_alert
from . import alerts as alert_svc
from . import cleanup as cleanup_svc
from .relevance import is_relevant
from .scoring import ScoredMention, compute_score

logger = logging.getLogger("noyou.scan")

DEFAULT_QUERY_LIMIT = 25
MAX_QUERIES_PER_SCAN = 10  # hard cap on search terms so a scan's work is bounded


def _safe_url(url: str | None) -> str | None:
    """Allow only http/https URLs — block javascript:/data:/etc. from external data."""
    if not url:
        return None
    try:
        return url if urlparse(url).scheme in ("http", "https") else None
    except ValueError:
        return None


def _connectors_for(user: User):
    """Active connectors filtered to those the user's plan permits (demo fallback)."""
    allowed = [c for c in get_active_connectors() if plan_allows_connector(user.plan, c.name)]
    return allowed or [DemoConnector()]


def _queries_for_user(db: Session, user: User) -> list[str]:
    """Search terms: each linked account handle, plus the user's name as a fallback."""
    accounts = db.scalars(
        select(Account).where(Account.user_id == user.id, Account.is_active == True)  # noqa: E712
    ).all()
    queries = [a.handle for a in accounts if a.handle]
    if user.full_name:
        queries.append(user.full_name)
    if not queries:
        queries.append(user.email.split("@")[0])
    # de-dupe, preserve order, and cap the total work.
    seen: set[str] = set()
    unique = [q for q in queries if not (q in seen or seen.add(q))]
    return unique[:MAX_QUERIES_PER_SCAN]


def start_scan(db: Session, user: User, *, trigger: str = "manual") -> Scan:
    """Create a ``pending`` scan row (counts toward the daily quota) without running it."""
    scan = Scan(
        user_id=user.id,
        status="pending",
        trigger=trigger,
        score_before=user.reputation_score,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def execute_scan(scan_id: str) -> None:
    """Run a previously-created scan to completion in its own DB session.

    Designed to be handed to FastAPI ``BackgroundTasks`` so the request returns
    immediately while the network-bound work happens off the request path.
    """
    db = SessionLocal()
    try:
        scan = db.get(Scan, scan_id)
        if scan is None or scan.status not in ("pending", "running"):
            return
        user = db.get(User, scan.user_id)
        if user is None:
            return
        _run_pipeline(db, user, scan)
    except Exception:
        logger.exception("execute_scan failed for scan %s", scan_id)
    finally:
        db.close()


def run_scan(db: Session, user: User, *, trigger: str = "manual") -> Scan:
    """Synchronous scan (used by the scheduler and seed). Creates + runs in one call."""
    scan = start_scan(db, user, trigger=trigger)
    _run_pipeline(db, user, scan)
    db.refresh(scan)
    return scan


def _run_pipeline(db: Session, user: User, scan: Scan) -> None:
    connectors = _connectors_for(user)
    analyzer = get_analyzer()

    scan.status = "running"
    scan.connectors_used = ",".join(c.name for c in connectors)
    if scan.score_before is None:
        scan.score_before = user.reputation_score
    db.add(scan)
    db.commit()

    new_alerts = []
    new_count = 0
    found_count = 0
    filtered_count = 0  # mentions dropped as irrelevant fuzzy-junk

    try:
        queries = _queries_for_user(db, user)
        subject_name = user.full_name or queries[0]

        # Existing external_ids so re-scans don't create duplicate mentions.
        existing_ids = set(
            db.scalars(select(Mention.external_id).where(Mention.user_id == user.id)).all()
        )

        for connector in connectors:
            for query in queries:
                try:
                    raw_mentions = connector.search(query, limit=DEFAULT_QUERY_LIMIT)
                except Exception as exc:
                    logger.warning("connector %s failed for %r: %s", connector.name, query, exc)
                    continue

                for raw in raw_mentions:
                    found_count += 1

                    # Relevance gate: broad keyless sources fuzzy-match junk
                    # ("precourt", "Michael Jordan", ...). Drop mentions whose
                    # text isn't actually about the query. The synthetic 'demo'
                    # connector always bypasses so the offline demo populates.
                    if (
                        settings.relevance_filter
                        and raw.source != "demo"
                        and not is_relevant(query, f"{raw.title or ''} {raw.content or ''}")
                    ):
                        filtered_count += 1
                        continue

                    if raw.external_id in existing_ids:
                        continue
                    existing_ids.add(raw.external_id)
                    new_count += 1

                    mention = Mention(
                        user_id=user.id,
                        scan_id=scan.id,
                        source=raw.source,
                        external_id=raw.external_id,
                        url=_safe_url(raw.url),
                        author=raw.author,
                        title=raw.title,
                        content=raw.content,
                        published_at=raw.published_at,
                    )
                    db.add(mention)
                    db.flush()  # assign mention.id

                    result = analyzer.analyze(
                        AnalysisInput(
                            content=raw.content,
                            title=raw.title,
                            source=raw.source,
                            author=raw.author,
                            subject_name=subject_name,
                        )
                    )
                    analysis = Analysis(
                        mention_id=mention.id,
                        sentiment=result.sentiment,
                        sentiment_score=result.sentiment_score,
                        risk_level=result.risk_level,
                        risk_category=result.risk_category,
                        context=result.context,
                        summary=result.summary,
                        recommendation=result.recommendation,
                        analyzer=result.analyzer,
                        confidence=result.confidence,
                    )
                    db.add(analysis)

                    alert = alert_svc.alert_for_mention(user.id, mention, analysis)
                    if alert:
                        db.add(alert)
                        new_alerts.append(alert)

                    for action in cleanup_svc.build_cleanup_records(user.id, mention, analysis):
                        db.add(action)

        db.flush()

        # Recompute score from the user's full current corpus.
        new_score = recompute_user_score(db, user)
        scan.score_after = new_score

        drop_alert = alert_svc.score_drop_alert(user.id, scan.score_before or 100.0, new_score)
        if drop_alert:
            db.add(drop_alert)
            new_alerts.append(drop_alert)

        scan.status = "completed"
        scan.mentions_found = found_count
        scan.new_mentions = new_count
        scan.finished_at = datetime.now(timezone.utc)
        db.commit()

        if filtered_count:
            logger.info(
                "scan %s for user %s: dropped %d irrelevant mention(s) of %d found",
                scan.id, user.id, filtered_count, found_count,
            )

        _notify(db, user, new_alerts)

    except Exception as exc:
        db.rollback()
        scan.status = "failed"
        scan.error = str(exc)[:1000]
        scan.finished_at = datetime.now(timezone.utc)
        db.commit()
        logger.exception("scan failed for user %s", user.id)


def recompute_user_score(db: Session, user: User) -> float:
    """Recompute and persist the user's reputation score from all their mentions."""
    rows = db.execute(
        select(
            Analysis.sentiment,
            Analysis.risk_level,
            Analysis.confidence,
            Mention.published_at,
            Mention.status,
        )
        .join(Mention, Mention.id == Analysis.mention_id)
        .where(Mention.user_id == user.id)
    ).all()

    scored = [
        ScoredMention(
            sentiment=r.sentiment,
            risk_level=r.risk_level,
            confidence=r.confidence,
            published_at=r.published_at,
            status=r.status,
        )
        for r in rows
    ]
    score = compute_score(scored)
    user.reputation_score = score
    db.add(user)
    db.commit()
    return score


def _notify(db: Session, user: User, new_alerts: list) -> None:
    if not new_alerts:
        return
    high = [a for a in new_alerts if a.severity in {"high", "critical"}]
    targets = high or new_alerts[:1]
    for alert in targets:
        ok = dispatch_alert(user.email, alert.title, alert.message)
        if ok:
            alert.notified = True
    db.commit()
