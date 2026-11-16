import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.app.core.config import settings
from backend.app.nlp.fallback import (
    heuristic_sentiment_analysis,
    heuristic_intent_detection,
    heuristic_entity_extraction,
    detect_language
)

logger = logging.getLogger("nlp.analyzer")


class NLPAnalysisResult(BaseModel):
    intent: str = Field(description="One of: GREETING, ORDER_STATUS, REFUND_REQUEST, BILLING_INQUIRY, TECHNICAL_SUPPORT, COMPLAINT, HUMAN_ESCALATION, GENERAL_FAQ, OUT_OF_SCOPE")
    sentiment: str = Field(description="One of: POSITIVE, NEUTRAL, NEGATIVE, VERY_NEGATIVE")
    sentiment_score: float = Field(description="Float between -1.0 (very negative) and 1.0 (very positive)")
    language: str = Field(description="ISO 639-1 two-letter language code (e.g. en, es, fr, de, hi)")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities like order_id, product_name, email")
    requires_escalation: bool = Field(description="True if sentiment is VERY_NEGATIVE or intent is HUMAN_ESCALATION")
    reasoning: Optional[str] = Field(default=None, description="Brief justification for classification")


NLP_ANALYSIS_PROMPT = """
You are an expert NLP classification engine for NovaTech customer service.
Analyze the user message below and extract structured classification in JSON.

Classify Intent:
- ORDER_STATUS: Where is package, tracking, delivery status, order lookup
- REFUND_REQUEST: Returning products, getting money back, cancellation
- BILLING_INQUIRY: Invoices, payment issues, subscription plans, card charges
- TECHNICAL_SUPPORT: Account login, passwords, crashes, website bugs
- COMPLAINT: Expressing anger, frustration, dissatisfaction, defective goods
- HUMAN_ESCALATION: Asking for a human, supervisor, agent, manager
- GENERAL_FAQ: Store hours, warranty terms, general product info
- OUT_OF_SCOPE: Unrelated tasks (e.g. writing essays, recipes, math, coding)

Classify Sentiment:
- POSITIVE (score 0.3 to 1.0)
- NEUTRAL (score -0.2 to 0.2)
- NEGATIVE (score -0.5 to -0.2)
- VERY_NEGATIVE (score -1.0 to -0.5)

Requires Escalation:
- Set requires_escalation = true if sentiment is VERY_NEGATIVE or intent is HUMAN_ESCALATION or user demands a live agent.

Extract Entities:
- Extract order_id if present (normalize to ORD-XXXXX).
- Extract any email, phone number, product mentions.

Detected Language:
- Two-letter code (e.g. 'en', 'es', 'fr', 'de').

User Message:
\"\"\"{message}\"\"\"
"""


async def analyze_message_nlp(text: str, gemini_client: Optional[Any] = None) -> NLPAnalysisResult:
    """
    Analyzes message for intent, sentiment, language, and entities.
    Attempts Gemini structured generation first; gracefully falls back to rules.
    """
    if not text or not text.strip():
        return NLPAnalysisResult(
            intent="GENERAL_FAQ",
            sentiment="NEUTRAL",
            sentiment_score=0.0,
            language="en",
            entities={},
            requires_escalation=False,
            reasoning="Empty input"
        )

    # If Gemini client and key are available, use Gemini 2.5 Flash structured output
    if gemini_client and settings.has_gemini_key:
        try:
            prompt = NLP_ANALYSIS_PROMPT.format(message=text)
            response = await gemini_client.aio.models.generate_content(
                model=settings.GEMINI_CHAT_MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": NLPAnalysisResult,
                    "temperature": 0.1,
                }
            )
            parsed = json.loads(response.text)
            return NLPAnalysisResult(**parsed)
        except Exception as e:
            logger.warning(f"Gemini NLP analysis failed, using fallback heuristic: {e}")

    # Fallback heuristic analyzer
    sentiment_data = heuristic_sentiment_analysis(text)
    intent = heuristic_intent_detection(text)
    entities = heuristic_entity_extraction(text)
    lang = detect_language(text)

    score = sentiment_data["sentiment_score"]
    sentiment = sentiment_data["sentiment"]

    requires_escalation = (
        sentiment == "VERY_NEGATIVE" or
        score <= settings.ESCALATION_SENTIMENT_THRESHOLD or
        intent == "HUMAN_ESCALATION" or
        any(w in text.lower() for w in ["human", "supervisor", "representative", "agent", "manager"])
    )

    return NLPAnalysisResult(
        intent=intent,
        sentiment=sentiment,
        sentiment_score=score,
        language=lang,
        entities=entities,
        requires_escalation=requires_escalation,
        reasoning="Heuristic rule-based fallback classification"
    )
