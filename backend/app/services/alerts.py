"""Alert generation — turns risky analyses and score drops into notifications."""
from __future__ import annotations

from ..models.alert import Alert
from ..models.analysis import Analysis
from ..models.mention import Mention

_SEVERITY_BY_RISK = {5: "critical", 4: "high", 3: "medium", 2: "medium", 1: "low"}


def alert_for_mention(user_id: str, mention: Mention, analysis: Analysis) -> Alert | None:
    """Create an alert if a mention is risky enough to warrant one."""
    if analysis.risk_level < 3 and analysis.sentiment != "negative":
        return None
    if analysis.risk_level < 2:
        return None

    severity = _SEVERITY_BY_RISK.get(analysis.risk_level, "low")
    title = f"{severity.title()} risk: {analysis.risk_category} mention on {mention.source}"
    message = (
        f"{analysis.summary or ''} "
        f"Recommendation: {analysis.recommendation or 'Review this mention.'}"
    ).strip()
    return Alert(
        user_id=user_id,
        mention_id=mention.id,
        severity=severity,
        title=title,
        message=message,
    )


def score_drop_alert(user_id: str, before: float, after: float, threshold: float = 5.0) -> Alert | None:
    if before - after < threshold:
        return None
    return Alert(
        user_id=user_id,
        severity="high" if before - after >= 10 else "medium",
        title=f"Reputation score dropped {before:.0f} -> {after:.0f}",
        message="New mentions reduced your reputation score. Review the latest high-risk items.",
    )
