import re
from typing import Dict, Any, List

INTENT_KEYWORDS = {
    "GREETING": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "howdy", "greetings"],
    "ORDER_STATUS": ["order", "track", "package", "tracking", "shipped", "delivery", "status", "where is", "ord-"],
    "REFUND_REQUEST": ["refund", "return", "money back", "exchange", "send back", "cancel order", "restocking"],
    "BILLING_INQUIRY": ["bill", "charge", "charged", "invoice", "payment", "card", "subscription", "price", "cost"],
    "TECHNICAL_SUPPORT": ["login", "password", "reset", "bug", "crash", "error", "connect", "not working", "broken"],
    "COMPLAINT": ["terrible", "awful", "horrible", "worst", "unacceptable", "scam", "rip off", "angry", "furious", "garbage"],
    "HUMAN_ESCALATION": ["human", "agent", "supervisor", "representative", "operator", "speak to someone", "person", "manager", "support rep"],
    "GENERAL_FAQ": ["hours", "warranty", "contact", "who are you", "what is novatech", "policy", "faq"]
}

VERY_NEGATIVE_WORDS = [
    "furious", "disgusted", "lawsuit", "sue", "unacceptable", "scam", "shattered", 
    "useless", "worst", "garbage", "pathetic", "hate", "stole", "ripoff", "threat"
]
NEGATIVE_WORDS = [
    "disappointed", "annoyed", "frustrated", "late", "broken", "damaged", "wrong", 
    "complaint", "fail", "slow", "bad", "issue", "problem", "ridiculous"
]
POSITIVE_WORDS = [
    "thank", "thanks", "great", "excellent", "awesome", "perfect", "good", "happy", 
    "love", "helpful", "wonderful", "appreciate", "fantastic"
]


def heuristic_sentiment_analysis(text: str) -> Dict[str, Any]:
    """Calculate rule-based sentiment and polarity score."""
    lower = text.lower()
    
    very_neg_count = sum(1 for w in VERY_NEGATIVE_WORDS if w in lower)
    neg_count = sum(1 for w in NEGATIVE_WORDS if w in lower)
    pos_count = sum(1 for w in POSITIVE_WORDS if w in lower)
    
    # Check for intense punctuation or ALL CAPS indicating anger
    is_caps = len(text) > 8 and text.isupper()
    exclamation_count = text.count("!")
    
    score = 0.0
    if very_neg_count > 0 or (neg_count >= 2 and exclamation_count >= 2) or (neg_count >= 1 and is_caps):
        sentiment = "VERY_NEGATIVE"
        score = -0.85 - min(0.15, (very_neg_count * 0.05))
    elif neg_count > pos_count:
        sentiment = "NEGATIVE"
        score = -0.4 - min(0.3, neg_count * 0.1)
    elif pos_count > neg_count:
        sentiment = "POSITIVE"
        score = 0.5 + min(0.4, pos_count * 0.15)
    else:
        sentiment = "NEUTRAL"
        score = 0.0
        
    return {
        "sentiment": sentiment,
        "sentiment_score": round(score, 2)
    }


def heuristic_intent_detection(text: str) -> str:
    """Classify user intent based on keyword frequencies."""
    lower = text.lower()
    words = set(re.findall(r'\b\w+\b', lower))
    
    # Priority check for human escalation
    for word in INTENT_KEYWORDS["HUMAN_ESCALATION"]:
        if word in lower:
            return "HUMAN_ESCALATION"

    # Friendly greeting check
    greetings = {"hello", "hi", "hey", "howdy", "greetings"}
    if words.intersection(greetings) or any(g in lower for g in ["good morning", "good afternoon", "good evening"]):
        if not any(k in lower for k in ["order", "refund", "return", "broken", "bill", "track", "cancel", "speak"]):
            return "GREETING"

    # Score each intent category
    best_intent = "GENERAL_FAQ"
    max_score = 0
    
    for intent, kws in INTENT_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in lower)
        if score > max_score:
            max_score = score
            best_intent = intent

    if max_score == 0:
        # Check out of scope
        if any(w in lower for w in ["poem", "joke", "recipe", "quantum", "weather", "translate", "code python"]):
            return "OUT_OF_SCOPE"
        return "GENERAL_FAQ"

    return best_intent


def heuristic_entity_extraction(text: str) -> Dict[str, Any]:
    """Extract entities like order IDs, emails, product keywords."""
    entities: Dict[str, Any] = {}
    
    # Match order ID
    order_match = re.search(r'\b(?:ORD-)?(\d{4,6})\b', text, re.IGNORECASE)
    if order_match:
        entities["order_id"] = f"ORD-{order_match.group(1)}"
        
    return entities


def detect_language(text: str) -> str:
    """Basic language detection heuristic (defaults to 'en')."""
    lower = text.lower()
    spanish_markers = ["hola", "gracias", "por favor", "¿", "dónde", "pedido", "devolución"]
    french_markers = ["bonjour", "merci", "s'il vous plaît", "commande", "remboursement"]
    german_markers = ["hallo", "danke", "bitte", "bestellung", "rückerstattung"]
    
    if any(m in lower for m in spanish_markers):
        return "es"
    if any(m in lower for m in french_markers):
        return "fr"
    if any(m in lower for m in german_markers):
        return "de"
    return "en"
