"""Training data for the reputation sentiment model.

Two sources, combined:

1. A curated **seed** of reputation-relevant phrases (below) so the model trains and
   works the moment the package is installed — no data collection required.
2. **Real labelled mentions** from the database: every analysed mention is a
   ``(content, sentiment)`` example. As scans accumulate and users correct labels, the
   model gets better each time it is retrained — this is the "for the future" part.

To avoid a feedback loop, DB rows produced by the trained model itself are excluded;
we only learn from the rule-based/LLM analysers and human labels.
"""
from __future__ import annotations

LABELS = ("positive", "neutral", "negative")

# Curated seed — short, reputation-flavoured text per class. Small but balanced; the
# DB examples do the heavy lifting once real data exists.
SEED: list[tuple[str, str]] = [
    # --- positive ---
    ("Absolutely fantastic service, the team went above and beyond for us.", "positive"),
    ("I'm thrilled with the results — highly recommend them to anyone.", "positive"),
    ("A brilliant, trustworthy professional who delivered exactly as promised.", "positive"),
    ("Outstanding work and genuinely kind people. Five stars.", "positive"),
    ("They saved my project. Incredible attention to detail and care.", "positive"),
    ("Proud to share that we just won an award for our community work.", "positive"),
    ("Such a positive experience from start to finish, will return.", "positive"),
    ("Honest, reliable, and great value — couldn't be happier.", "positive"),
    ("Their generosity and integrity really stood out to everyone.", "positive"),
    ("A wonderful leader who inspires the whole team every day.", "positive"),
    ("Excellent communication and a flawless final product.", "positive"),
    ("Best decision we made all year. Truly exceptional.", "positive"),
    ("Grateful for the support — they truly care about clients.", "positive"),
    ("Impressive results and a refreshingly transparent process.", "positive"),
    ("Kind, competent, and professional. A pleasure to work with.", "positive"),
    # --- neutral ---
    ("The company announced a new office location opening next quarter.", "neutral"),
    ("He spoke at the conference about industry trends on Tuesday.", "neutral"),
    ("The product is available in three sizes and two colors.", "neutral"),
    ("They published a quarterly report covering revenue and headcount.", "neutral"),
    ("The article describes the history of the organization.", "neutral"),
    ("A profile listing their education and previous employers.", "neutral"),
    ("The event is scheduled for the first week of next month.", "neutral"),
    ("She was mentioned in a list of attendees at the summit.", "neutral"),
    ("The website was updated with new contact information.", "neutral"),
    ("The team released a software update with minor changes.", "neutral"),
    ("An interview discussing the roadmap for the coming year.", "neutral"),
    ("The brand sponsored a local sports tournament this season.", "neutral"),
    ("Their name appears in the directory under consulting services.", "neutral"),
    ("A neutral summary of the merger was posted online.", "neutral"),
    ("The report notes the figures without further comment.", "neutral"),
    # --- negative ---
    ("Total scam. They took my money and disappeared — avoid at all costs.", "negative"),
    ("Horrible experience, rude staff and they lied about everything.", "negative"),
    ("This person is a fraud and cannot be trusted with anything.", "negative"),
    ("Worst service I've ever had. Completely unprofessional and dishonest.", "negative"),
    ("They ripped off dozens of customers and ignored every complaint.", "negative"),
    ("Allegations of misconduct have surfaced against the executive.", "negative"),
    ("Disgraceful behavior. I'm filing a formal complaint and a lawsuit.", "negative"),
    ("Deeply disappointing — broken promises and zero accountability.", "negative"),
    ("A toxic, abusive workplace according to several former employees.", "negative"),
    ("They leaked private data and refused to take responsibility.", "negative"),
    ("Stay away. Shady practices and constant lies about the product.", "negative"),
    ("The review exposes a pattern of cheating and deception.", "negative"),
    ("Furious about the terrible quality and the insulting response.", "negative"),
    ("Caught falsifying records — an absolute betrayal of trust.", "negative"),
    ("Embarrassing scandal as the investigation reveals wrongdoing.", "negative"),
]


def _db_examples(db, *, min_confidence: float = 0.55, limit: int = 20000) -> list[tuple[str, str]]:
    """Pull ``(content, sentiment)`` pairs from analysed mentions for weak supervision."""
    from sqlalchemy import select

    from ..models.analysis import Analysis
    from ..models.mention import Mention

    rows = db.execute(
        select(Mention.content, Analysis.sentiment)
        .join(Analysis, Analysis.mention_id == Mention.id)
        .where(
            Analysis.confidence >= min_confidence,
            Analysis.analyzer.notlike("trained%"),  # never learn from our own output
        )
        .limit(limit)
    ).all()
    out: list[tuple[str, str]] = []
    for content, sentiment in rows:
        if content and sentiment in LABELS and len(content.strip()) >= 8:
            out.append((content.strip(), sentiment))
    return out


def load_training_data(db=None) -> tuple[list[str], list[str]]:
    """Return ``(texts, labels)`` combining the seed with DB examples (deduplicated)."""
    pairs: list[tuple[str, str]] = list(SEED)
    if db is not None:
        pairs.extend(_db_examples(db))

    seen: set[str] = set()
    texts: list[str] = []
    labels: list[str] = []
    for text, label in pairs:
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        texts.append(text)
        labels.append(label)
    return texts, labels
