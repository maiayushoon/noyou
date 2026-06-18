from app.analysis.base import AnalysisInput
from app.analysis.rule_based import RuleBasedAnalyzer

analyzer = RuleBasedAnalyzer()


def test_positive_mention():
    r = analyzer.analyze(AnalysisInput(content="An outstanding, brilliant leader. Highly recommend!"))
    assert r.sentiment == "positive"
    assert r.risk_level == 0
    assert r.sentiment_score > 0


def test_negative_high_risk_legal():
    r = analyzer.analyze(AnalysisInput(content="He was arrested and named in a fraud lawsuit."))
    assert r.sentiment == "negative"
    assert r.risk_category == "legal"
    assert r.risk_level >= 4
    assert r.recommendation


def test_privacy_risk_detected():
    r = analyzer.analyze(AnalysisInput(content="Someone leaked her home address and private photos online."))
    assert r.risk_category == "privacy"
    assert r.risk_level >= 4


def test_negation_flips_sentiment():
    pos = analyzer.analyze(AnalysisInput(content="This service is great."))
    neg = analyzer.analyze(AnalysisInput(content="This service is not great."))
    assert pos.sentiment_score > neg.sentiment_score


def test_neutral_mention():
    r = analyzer.analyze(AnalysisInput(content="They attended the conference on Tuesday."))
    assert r.sentiment == "neutral"


def test_result_always_valid():
    r = analyzer.analyze(AnalysisInput(content="x")).validate()
    assert r.sentiment in ("positive", "neutral", "negative")
    assert 0 <= r.risk_level <= 5
    assert -1.0 <= r.sentiment_score <= 1.0
