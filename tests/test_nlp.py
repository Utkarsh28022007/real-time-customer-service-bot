import pytest
from backend.app.nlp.fallback import (
    heuristic_sentiment_analysis,
    heuristic_intent_detection,
    heuristic_entity_extraction,
    detect_language
)
from backend.app.nlp.analyzer import analyze_message_nlp


def test_sentiment_positive():
    res = heuristic_sentiment_analysis("Thank you so much! That was fantastic and super helpful!")
    assert res["sentiment"] == "POSITIVE"
    assert res["sentiment_score"] > 0


def test_sentiment_neutral():
    res = heuristic_sentiment_analysis("What are the standard hours of operations?")
    assert res["sentiment"] == "NEUTRAL"
    assert res["sentiment_score"] == 0.0


def test_sentiment_very_negative():
    res = heuristic_sentiment_analysis("This service is completely useless garbage and unacceptable! I am furious!")
    assert res["sentiment"] == "VERY_NEGATIVE"
    assert res["sentiment_score"] <= -0.5


def test_intent_order_status():
    intent = heuristic_intent_detection("Can you track my package for order ORD-88421?")
    assert intent == "ORDER_STATUS"


def test_intent_refund():
    intent = heuristic_intent_detection("I want a full refund and to return this item.")
    assert intent == "REFUND_REQUEST"


def test_intent_human_escalation():
    intent = heuristic_intent_detection("Let me speak to a human representative right now.")
    assert intent == "HUMAN_ESCALATION"


def test_entity_extraction_order_id():
    entities = heuristic_entity_extraction("Please verify status of order 88421.")
    assert entities.get("order_id") == "ORD-88421"


def test_detect_language_spanish():
    lang = detect_language("Hola, ¿dónde está mi pedido?")
    assert lang == "es"


@pytest.mark.asyncio
async def test_full_nlp_analyzer_escalation_trigger():
    res = await analyze_message_nlp("This product arrived completely broken! I demand a human supervisor!")
    assert res.requires_escalation is True
    assert res.sentiment in ["NEGATIVE", "VERY_NEGATIVE"] or res.intent == "HUMAN_ESCALATION"
