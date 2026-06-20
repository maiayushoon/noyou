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

# Curated seed — short, reputation-flavoured text per class, spanning the contexts a
# reputation manager actually sees: customer reviews, news-style sentences, social
# posts, professional/HR contexts, scams and complaints, and neutral announcements.
# Roughly class-balanced; the DB examples do the heavy lifting once real data exists.
SEED: list[tuple[str, str]] = [
    # ============================ POSITIVE ============================
    # -- reviews / customer praise --
    ("Absolutely fantastic service, the team went above and beyond for us.", "positive"),
    ("I'm thrilled with the results — highly recommend them to anyone.", "positive"),
    ("A brilliant, trustworthy professional who delivered exactly as promised.", "positive"),
    ("Outstanding work and genuinely kind people. Five stars.", "positive"),
    ("They saved my project. Incredible attention to detail and care.", "positive"),
    ("Such a positive experience from start to finish, will return.", "positive"),
    ("Honest, reliable, and great value — couldn't be happier.", "positive"),
    ("Excellent communication and a flawless final product.", "positive"),
    ("Best decision we made all year. Truly exceptional.", "positive"),
    ("Grateful for the support — they truly care about clients.", "positive"),
    ("Kind, competent, and professional. A pleasure to work with.", "positive"),
    ("Five stars, would absolutely book again without hesitation.", "positive"),
    ("They fixed the issue in minutes and refused to overcharge me.", "positive"),
    ("Fast, friendly, and the quality exceeded my expectations.", "positive"),
    ("The staff treated us like family — warm and welcoming throughout.", "positive"),
    ("Worth every penny. I've already recommended them to three friends.", "positive"),
    ("Smooth process, clear pricing, and a result I genuinely love.", "positive"),
    ("Came in under budget and ahead of schedule. Hugely impressed.", "positive"),
    ("The product arrived early and works even better than advertised.", "positive"),
    ("Patient, knowledgeable, and never pushy. A rare find these days.", "positive"),
    ("They followed up afterwards just to make sure I was happy.", "positive"),
    ("Top-notch craftsmanship and a team that clearly takes pride in it.", "positive"),
    ("Refreshingly transparent — no hidden fees and no surprises.", "positive"),
    ("My go-to from now on. Consistent, dependable, and fairly priced.", "positive"),
    ("Hands down the best experience I've had with any provider.", "positive"),
    # -- news-style / accomplishments --
    ("Proud to share that we just won an award for our community work.", "positive"),
    ("Their generosity and integrity really stood out to everyone.", "positive"),
    ("A wonderful leader who inspires the whole team every day.", "positive"),
    ("Impressive results and a refreshingly transparent process.", "positive"),
    ("The firm was recognised as one of the best places to work this year.", "positive"),
    ("The startup raised funding and was praised for its ethical practices.", "positive"),
    ("Critics applauded the launch as a bold step forward for the industry.", "positive"),
    ("The charity was celebrated for raising a record amount for local schools.", "positive"),
    ("Analysts highlighted the company's strong growth and loyal customer base.", "positive"),
    ("The CEO earned wide respect for handling the crisis with honesty.", "positive"),
    ("Their new clinic was praised for improving care across the region.", "positive"),
    ("The researcher was honoured for a breakthrough that helps thousands.", "positive"),
    ("Volunteers thanked the foundation for its tireless, selfless work.", "positive"),
    ("The restaurant earned a glowing review for service and atmosphere.", "positive"),
    ("Investors welcomed the results, citing trust and steady leadership.", "positive"),
    # -- social posts / personal --
    ("So happy with how my new website turned out, the designer nailed it!", "positive"),
    ("Huge shoutout to this team — they made a stressful move feel easy.", "positive"),
    ("Can't recommend these folks enough, genuinely lovely to deal with.", "positive"),
    ("Just had the best meal of my life here, the chef is incredible.", "positive"),
    ("Thank you for going out of your way to help us, it meant a lot.", "positive"),
    ("This brand keeps earning my loyalty, every order is a delight.", "positive"),
    ("Blown away by the customer support, they actually listened.", "positive"),
    ("What a gem of a business, supportive and full of integrity.", "positive"),
    ("Love supporting a company that treats its staff this well.", "positive"),
    ("Beyond grateful — they turned a nightmare situation around for me.", "positive"),
    # -- professional / HR --
    ("A dependable colleague whose work consistently raises the bar.", "positive"),
    ("She mentors junior staff with patience and real generosity.", "positive"),
    ("An ethical operator who always puts clients before profit.", "positive"),
    ("References describe him as honest, diligent, and a true team player.", "positive"),
    ("Clients trust her completely because she always delivers.", "positive"),
    ("A standout hire — talented, humble, and incredibly hard-working.", "positive"),
    ("Their leadership turned the department around in under a year.", "positive"),
    ("Respected across the field for fairness and sound judgment.", "positive"),
    ("He resolved a tense negotiation with grace and integrity.", "positive"),
    ("The board commended her vision and her care for employees.", "positive"),
    # -- recovery / reassurance (positive tone) --
    ("They owned the mistake immediately and made it right, no fuss.", "positive"),
    ("Even when something went wrong, they handled it beautifully.", "positive"),
    ("Quick refund, sincere apology — that's how you keep a customer.", "positive"),
    ("Reliable, safe, and exactly what they promised. Total peace of mind.", "positive"),
    ("Trustworthy from day one, and that trust has been rewarded.", "positive"),
    ("A genuinely caring approach that you rarely see anymore.", "positive"),
    ("Couldn't fault a single thing — flawless from quote to finish.", "positive"),
    ("Exceptional value and people who clearly love what they do.", "positive"),
    ("The whole experience left me smiling. Wholeheartedly recommend.", "positive"),
    ("Professional, prompt, and a joy to work with start to finish.", "positive"),
    ("They earned a customer for life with that kind of service.", "positive"),
    ("Stellar results and a team I'd happily trust again tomorrow.", "positive"),
    ("Highly skilled and refreshingly honest about what was possible.", "positive"),
    ("A delightful surprise — exceeded every expectation we had.", "positive"),
    ("Glowing feedback all round; the client could not be happier.", "positive"),
    ("Phenomenal support, clear answers, and zero runaround.", "positive"),
    ("They treated my small order with the same care as a big one.", "positive"),
    ("Wonderful from start to finish — I'll be back without a doubt.", "positive"),
    ("Their integrity shines through in every interaction.", "positive"),
    ("Simply the most reliable partner we've ever worked with.", "positive"),
    ("An inspiring example of doing business the right way.", "positive"),
    ("Warm, capable, and endlessly patient with all my questions.", "positive"),
    ("Outstanding outcome and a process that felt genuinely fair.", "positive"),
    ("They made a complicated thing simple, and did it with a smile.", "positive"),
    ("First class all the way — service, quality, and follow-up.", "positive"),

    # ============================ NEUTRAL ============================
    # -- announcements / corporate --
    ("The company announced a new office location opening next quarter.", "neutral"),
    ("They published a quarterly report covering revenue and headcount.", "neutral"),
    ("The team released a software update with minor changes.", "neutral"),
    ("The brand sponsored a local sports tournament this season.", "neutral"),
    ("The website was updated with new contact information.", "neutral"),
    ("The board appointed a new chief financial officer effective Monday.", "neutral"),
    ("The firm relocated its headquarters to the downtown district.", "neutral"),
    ("The company will hold its annual meeting on the third of March.", "neutral"),
    ("A press release outlined the schedule for the product rollout.", "neutral"),
    ("The organisation updated its privacy policy earlier this week.", "neutral"),
    ("Registration for the workshop opens at nine on Friday morning.", "neutral"),
    ("The branch will operate on reduced hours during the holiday.", "neutral"),
    ("They added two new payment options to the checkout page.", "neutral"),
    ("The agenda lists four speakers and a panel discussion.", "neutral"),
    ("The store moved to a larger unit on the same street.", "neutral"),
    # -- factual / bio / profile --
    ("He spoke at the conference about industry trends on Tuesday.", "neutral"),
    ("The article describes the history of the organization.", "neutral"),
    ("A profile listing their education and previous employers.", "neutral"),
    ("She was mentioned in a list of attendees at the summit.", "neutral"),
    ("Their name appears in the directory under consulting services.", "neutral"),
    ("The report notes the figures without further comment.", "neutral"),
    ("The product is available in three sizes and two colors.", "neutral"),
    ("The event is scheduled for the first week of next month.", "neutral"),
    ("An interview discussing the roadmap for the coming year.", "neutral"),
    ("A neutral summary of the merger was posted online.", "neutral"),
    ("The biography lists his degrees and the years he held each role.", "neutral"),
    ("Her LinkedIn page shows ten years at three different firms.", "neutral"),
    ("The filing records the company's address and registration number.", "neutral"),
    ("The transcript covers the questions asked during the session.", "neutral"),
    ("The map marks the location of the new facility near the highway.", "neutral"),
    # -- news-style neutral --
    ("The council reviewed the proposal and deferred a decision.", "neutral"),
    ("Shares closed flat after a quiet trading session today.", "neutral"),
    ("The spokesperson confirmed the dates but gave no further detail.", "neutral"),
    ("The study compared two methods and reported the measurements.", "neutral"),
    ("Officials said the inspection was routine and concluded on time.", "neutral"),
    ("The vendor list was published alongside the tender documents.", "neutral"),
    ("The agency released updated guidelines for the application process.", "neutral"),
    ("The committee met for two hours and adjourned without a vote.", "neutral"),
    ("The survey collected responses from about four hundred participants.", "neutral"),
    ("The schedule was posted and tickets go on sale next week.", "neutral"),
    # -- logistics / how-to / mixed-neutral --
    ("The package is expected to arrive within five business days.", "neutral"),
    ("Customers can reach support by phone or through the web form.", "neutral"),
    ("The manual explains how to set up the device step by step.", "neutral"),
    ("The subscription renews annually unless cancelled beforehand.", "neutral"),
    ("The app supports both light and dark display modes.", "neutral"),
    ("The parking lot has spaces reserved for visitors near the entrance.", "neutral"),
    ("The menu lists prices and indicates which dishes are vegetarian.", "neutral"),
    ("The form requires a name, an email address, and a phone number.", "neutral"),
    ("The office is open weekdays from eight until five.", "neutral"),
    ("The newsletter goes out on the first Monday of each month.", "neutral"),
    ("The course runs for six weeks with one session per week.", "neutral"),
    ("The warehouse stocks roughly two thousand items at any time.", "neutral"),
    ("The contract term is twelve months with an option to extend.", "neutral"),
    ("The system performs scheduled maintenance overnight on Sundays.", "neutral"),
    ("The invoice itemises labour, materials, and applicable tax.", "neutral"),
    # -- social-neutral / observational --
    ("Saw their booth at the trade show; it was near the main hall.", "neutral"),
    ("They posted a photo of the new signage outside the building.", "neutral"),
    ("Heard they're hiring for a couple of roles in the design team.", "neutral"),
    ("Their stand had a sign-up sheet and some printed brochures.", "neutral"),
    ("Looks like they changed their logo and updated the colours.", "neutral"),
    ("The webinar replay is available on their channel now.", "neutral"),
    ("They shared the slides from yesterday's presentation online.", "neutral"),
    ("Noticed the opening hours on the door were recently changed.", "neutral"),
    ("Someone asked about pricing and they replied with a link.", "neutral"),
    ("The thread lists a few alternatives without recommending one.", "neutral"),
    ("Their account reposts industry news a couple of times a week.", "neutral"),
    ("The page describes the team and links to a contact form.", "neutral"),
    ("A short clip showed the factory floor during a tour.", "neutral"),
    ("The update mostly covered backend changes users won't notice.", "neutral"),
    ("They announced a webinar but haven't set a date yet.", "neutral"),
    ("The listing shows the square footage and the asking figure.", "neutral"),
    ("The notice reminded tenants about the upcoming inspection.", "neutral"),
    ("The release notes mention bug fixes and a version bump.", "neutral"),
    ("The roster was updated to reflect the new shift pattern.", "neutral"),
    ("The directory entry includes the address and business hours.", "neutral"),
    ("The report tallies attendance and lists the agenda items.", "neutral"),
    ("Their blog covered a topic without taking a clear side.", "neutral"),
    ("The handbook outlines the steps for submitting a request.", "neutral"),
    ("The dashboard displays the totals for the current period.", "neutral"),
    ("The memo restated the policy and the relevant deadlines.", "neutral"),

    # ============================ NEGATIVE ============================
    # -- scams / fraud --
    ("Total scam. They took my money and disappeared — avoid at all costs.", "negative"),
    ("This person is a fraud and cannot be trusted with anything.", "negative"),
    ("They ripped off dozens of customers and ignored every complaint.", "negative"),
    ("Stay away. Shady practices and constant lies about the product.", "negative"),
    ("They charged my card twice and then blocked my number.", "negative"),
    ("A classic bait and switch — the deal vanished once they had my deposit.", "negative"),
    ("Pure con artists. They promised a refund that never came.", "negative"),
    ("Beware: fake reviews and a product that doesn't even work.", "negative"),
    ("They strung me along for weeks then ghosted me entirely.", "negative"),
    ("Took the payment up front and delivered absolutely nothing.", "negative"),
    ("It's a pyramid scheme dressed up as a business opportunity.", "negative"),
    ("They forged the signature on the paperwork to close the deal.", "negative"),
    ("Counterfeit goods sold as genuine — a complete rip-off.", "negative"),
    ("The 'guarantee' is worthless; they refuse every claim.", "negative"),
    ("Phishing emails from this company keep targeting our staff.", "negative"),
    # -- complaints / bad service --
    ("Horrible experience, rude staff and they lied about everything.", "negative"),
    ("Worst service I've ever had. Completely unprofessional and dishonest.", "negative"),
    ("Deeply disappointing — broken promises and zero accountability.", "negative"),
    ("Furious about the terrible quality and the insulting response.", "negative"),
    ("Disgraceful behavior. I'm filing a formal complaint and a lawsuit.", "negative"),
    ("Waited three hours and they still got the order completely wrong.", "negative"),
    ("They overcharged me and then refused to explain the bill.", "negative"),
    ("The product broke within a day and support just hung up on me.", "negative"),
    ("Rude, dismissive, and clearly couldn't care less about customers.", "negative"),
    ("Avoid. They cancelled at the last minute and kept my deposit.", "negative"),
    ("The work was sloppy and they left a mess for me to clean up.", "negative"),
    ("Endless excuses, missed deadlines, and a bill that kept growing.", "negative"),
    ("Cold, unhelpful, and they made me feel like a nuisance.", "negative"),
    ("The repair made it worse and they denied any responsibility.", "negative"),
    ("Never again. Overpriced, late, and arrogant about it.", "negative"),
    # -- misconduct / scandal / news-negative --
    ("Allegations of misconduct have surfaced against the executive.", "negative"),
    ("A toxic, abusive workplace according to several former employees.", "negative"),
    ("They leaked private data and refused to take responsibility.", "negative"),
    ("The review exposes a pattern of cheating and deception.", "negative"),
    ("Caught falsifying records — an absolute betrayal of trust.", "negative"),
    ("Embarrassing scandal as the investigation reveals wrongdoing.", "negative"),
    ("Regulators fined the firm for misleading its own investors.", "negative"),
    ("Whistleblowers describe a culture of bullying and cover-ups.", "negative"),
    ("The lawsuit accuses the company of negligence and fraud.", "negative"),
    ("Customers were left stranded after the abrupt, unexplained closure.", "negative"),
    ("Reports allege the director pocketed funds meant for charity.", "negative"),
    ("The audit uncovered years of falsified safety inspections.", "negative"),
    ("An exposé details unsafe conditions and ignored warnings.", "negative"),
    ("Former staff allege wage theft and intimidation at the firm.", "negative"),
    ("The scandal widened as more victims came forward this week.", "negative"),
    # -- social posts / personal anger --
    ("Do not give these people your money, I'm warning you.", "negative"),
    ("Still waiting on the refund they promised a month ago. Disgusted.", "negative"),
    ("They treated my elderly mother appallingly. Absolutely shameful.", "negative"),
    ("Worst decision ever. Wish I'd read the warnings first.", "negative"),
    ("They blocked me the second I asked for my money back.", "negative"),
    ("Lied to my face, then denied ever saying it. Untrustworthy.", "negative"),
    ("I've never been so insulted by a so-called professional.", "negative"),
    ("They ruined my event and didn't even apologise.", "negative"),
    ("Save yourself the heartache and steer well clear of them.", "negative"),
    ("Absolutely livid — they damaged my property and walked away.", "negative"),
    # -- professional / reference-negative --
    ("Unreliable and dishonest; I would never work with him again.", "negative"),
    ("She missed every deadline and blamed everyone but herself.", "negative"),
    ("A bully of a manager who drove half the team to quit.", "negative"),
    ("He took credit for others' work and undermined his colleagues.", "negative"),
    ("Cut corners on safety and lied to the client about it.", "negative"),
    ("References warn that he cannot be trusted with finances.", "negative"),
    ("Incompetent and evasive — the project failed under her watch.", "negative"),
    ("He berated junior staff and created a hostile environment.", "negative"),
    ("Constantly late, defensive, and impossible to rely on.", "negative"),
    ("They sabotaged the handover out of pure spite.", "negative"),
    # -- product / quality-negative --
    ("Cheap, flimsy, and it fell apart after one use. Total waste.", "negative"),
    ("The app is riddled with bugs and crashes every few minutes.", "negative"),
    ("Misleading photos — what arrived looked nothing like the listing.", "negative"),
    ("Defective on arrival and they made returning it a nightmare.", "negative"),
    ("Overhyped garbage. Don't believe the glowing fake reviews.", "negative"),
    ("It stopped working a week after the warranty conveniently expired.", "negative"),
    ("Filthy room, broken fixtures, and a manager who shrugged.", "negative"),
    ("The food was cold, the service slow, and the bill outrageous.", "negative"),
    ("Slow, buggy, and the so-called premium tier is a scam.", "negative"),
    ("Dangerous product that should never have been sold.", "negative"),
    ("Cheaply made, poorly packed, and not worth half the price.", "negative"),
    ("They sold me a lemon and laughed off my complaint.", "negative"),
    ("Endless hidden fees buried in pages of fine print.", "negative"),
    ("Customer service is a maze designed to make you give up.", "negative"),
    ("A shambles from start to finish. Avoid like the plague.", "negative"),
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
