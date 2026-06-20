"""Alert generation — turns risky analyses and score drops into notifications."""
from __future__ import annotations

from ..models.alert import Alert
from ..models.analysis import Analysis
from ..models.mention import Mention

_SEVERITY_BY_RISK = {5: "critical", 4: "high", 3: "medium", 2: "medium", 1: "low"}

# Sources for content the user OWNS are suffixed with this (e.g. "reddit_owned",
# "youtube_owned") by the OAuth adapters. A risky flag on the user's OWN post is
# uniquely actionable — they can edit or delete it themselves — so it earns a
# distinct, high-urgency alert.
_OWNED_SUFFIX = "_owned"
_OWNED_MIN_RISK = 3  # risk_level threshold for the owned-post alert path


def _platform_from_owned_source(source: str) -> str:
    """Derive a human platform label from an owned source ("reddit_owned" -> "Reddit")."""
    prefix = source[: -len(_OWNED_SUFFIX)] if source.endswith(_OWNED_SUFFIX) else source
    return prefix.replace("_", " ").title() if prefix else "connected account"


def alert_for_mention(user_id: str, mention: Mention, analysis: Analysis) -> Alert | None:
    """Create an alert if a mention is risky enough to warrant one.

    A flagged post on one of the user's OWN connected accounts (source ends with
    ``_owned``) at risk level >= 3 produces a DISTINCT, high-urgency alert — it is
    content they directly control and should review first. All other (third-party)
    mentions follow the standard severity-by-risk path unchanged. Exactly one alert
    is ever returned, so there is no double-alerting.
    """
    source = mention.source or ""
    is_owned = source.endswith(_OWNED_SUFFIX)

    # Owned-post path: the user's own connected-account content, flagged risky.
    if is_owned and analysis.risk_level >= _OWNED_MIN_RISK:
        platform = _platform_from_owned_source(source)
        severity = _SEVERITY_BY_RISK.get(analysis.risk_level, "high")
        # Floor owned-post alerts at high urgency — this is content the user owns.
        if severity not in {"high", "critical"}:
            severity = "high"
        title = f"A post on your connected {platform} was flagged"
        message = (
            f"{analysis.summary or 'This post on your connected account was flagged as risky.'} "
            f"Recommendation: {analysis.recommendation or 'Review or remove this post.'}"
        ).strip()
        return Alert(
            user_id=user_id,
            mention_id=mention.id,
            severity=severity,
            title=title,
            message=message,
        )

    # Standard third-party-mention path.
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
