"""Cleanup suggestion engine.

For each risky mention, propose the right manual remediation step. The same records
become the queue for *automated* cleanup post-MVP (see ROADMAP) — we just flip
``automated`` and execute via the source's API instead of showing instructions.
"""
from __future__ import annotations

from ..models.analysis import Analysis
from ..models.cleanup import CleanupAction
from ..models.mention import Mention

# Per-source removal playbooks (manual for MVP).
_REMOVAL_INSTRUCTIONS: dict[str, str] = {
    "google": (
        "Use Google's 'Results about you' tool and the Remove Outdated Content tool. "
        "If the page hosts personal/defamatory data, file a removal request and contact "
        "the site owner directly."
    ),
    "twitter": (
        "Report the post via X's reporting flow (harassment / private information). If it's "
        "your own post, delete it. For impersonation, file an impersonation report."
    ),
    "reddit": (
        "Report to subreddit moderators and Reddit admins. Personal-information posts violate "
        "Reddit policy and can be removed via the privacy report form."
    ),
    "youtube": (
        "Use YouTube's privacy complaint process or report the video. Request the uploader take "
        "it down if it's defamatory or exposes personal data."
    ),
    "news": (
        "Contact the publication's editor with a correction/removal request and supporting facts. "
        "Consider a right-to-be-forgotten request where applicable (EU)."
    ),
    "blog": (
        "Email the site owner / webmaster requesting removal. If unresponsive, escalate to the "
        "hosting provider with a privacy or defamation complaint."
    ),
    "forum": (
        "Contact forum administrators. For leaked personal data, cite their data policy and "
        "applicable privacy law (GDPR/CCPA)."
    ),
}

_DEFAULT_INSTRUCTION = (
    "Document the content (screenshot + URL), then contact the platform/host with a removal "
    "request citing privacy or defamation as appropriate."
)


def suggest_actions(mention: Mention, analysis: Analysis) -> list[dict]:
    """Return cleanup action dicts (not yet persisted) for a risky mention."""
    actions: list[dict] = []
    level = analysis.risk_level
    category = analysis.risk_category

    if level <= 1 and analysis.sentiment != "negative":
        return actions  # nothing worth doing

    source_help = _REMOVAL_INSTRUCTIONS.get(mention.source, _DEFAULT_INSTRUCTION)

    if level >= 4:
        actions.append(
            {
                "action_type": "request_removal",
                "title": f"Request removal of high-risk {category} content",
                "instructions": source_help,
            }
        )
        if category in {"legal", "privacy", "financial"}:
            actions.append(
                {
                    "action_type": "dispute",
                    "title": "Escalate / seek professional help",
                    "instructions": (
                        "This content poses serious risk. Preserve evidence and consult a "
                        "lawyer or PR professional. Consider a formal takedown / cease-and-desist."
                    ),
                }
            )
    elif level >= 2 or analysis.sentiment == "negative":
        actions.append(
            {
                "action_type": "request_removal",
                "title": f"Consider requesting removal of {category} content",
                "instructions": source_help,
            }
        )
        actions.append(
            {
                "action_type": "monitor",
                "title": "Monitor for spread",
                "instructions": "Keep this on watch; if it gains traction, escalate to removal.",
            }
        )

    # Always offer archiving so the user can suppress it from their active view.
    actions.append(
        {
            "action_type": "archive",
            "title": "Archive this mention",
            "instructions": "Hide from your active dashboard once handled or deemed acceptable.",
        }
    )
    return actions


def build_cleanup_records(user_id: str, mention: Mention, analysis: Analysis) -> list[CleanupAction]:
    return [
        CleanupAction(
            user_id=user_id,
            mention_id=mention.id,
            action_type=a["action_type"],
            title=a["title"],
            instructions=a["instructions"],
        )
        for a in suggest_actions(mention, analysis)
    ]
