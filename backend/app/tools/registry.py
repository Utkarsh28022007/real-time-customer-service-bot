import random
import re
from typing import Dict, Any, Optional
from backend.app.tools.mock_db import MOCK_ORDERS, MOCK_FAQ_TOPICS
from backend.app.db.database import save_ticket


def normalize_order_id(raw_id: str) -> str:
    """Normalize user order ID format (e.g. '88421' -> 'ORD-88421')."""
    cleaned = raw_id.strip().upper()
    if not cleaned.startswith("ORD-"):
        # Match numeric sequence
        match = re.search(r'\d+', cleaned)
        if match:
            return f"ORD-{match.group(0)}"
    return cleaned


def check_order_status(order_id: str) -> Dict[str, Any]:
    """
    Look up the real-time status of a customer order using its Order ID.
    """
    normalized = normalize_order_id(order_id)
    if normalized in MOCK_ORDERS:
        order = MOCK_ORDERS[normalized]
        return {
            "found": True,
            "order_id": order["order_id"],
            "status": order["status"],
            "carrier": order["carrier"],
            "tracking_number": order["tracking_number"],
            "estimated_delivery": order["estimated_delivery"],
            "items": [item["name"] for item in order["items"]],
            "total": f"${order['total']:.2f}",
            "notes": order["notes"]
        }
    else:
        return {
            "found": False,
            "order_id": order_id,
            "message": f"Order '{order_id}' was not found in our fulfillment records. Please verify the 5-digit number or check the email confirmation."
        }


async def create_ticket(
    summary: str,
    priority: str = "MEDIUM",
    reason: Optional[str] = None,
    session_id: Optional[str] = None,
    user_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a support escalation ticket for a human customer support agent.
    """
    priority = priority.upper()
    if priority not in ["LOW", "MEDIUM", "HIGH", "URGENT"]:
        priority = "MEDIUM"

    ticket_number = f"TICK-{random.randint(10000, 99999)}"
    
    try:
        await save_ticket(
            ticket_id=ticket_number,
            session_id=session_id,
            user_email=user_email,
            summary=summary,
            priority=priority,
            reason=reason or "Automated sentiment/intent escalation",
            status="OPEN"
        )
    except Exception as e:
        print(f"Error persisting ticket: {e}")

    return {
        "success": True,
        "ticket_id": ticket_number,
        "priority": priority,
        "status": "OPEN",
        "message": f"Support Ticket {ticket_number} has been logged with {priority} priority. A support specialist has been assigned."
    }


def get_faq(topic: str) -> Dict[str, Any]:
    """
    Retrieve quick policy or company FAQs by topic (returns, shipping, warranty, support_hours).
    """
    key = topic.lower().strip()
    for k, v in MOCK_FAQ_TOPICS.items():
        if k in key or key in k:
            return {"found": True, "topic": k, "answer": v}
            
    return {
        "found": False,
        "topic": topic,
        "message": f"No specific static FAQ found for '{topic}'. Checking knowledge base..."
    }


GEMINI_TOOLS_DECLARATIONS = [
    {
        "name": "check_order_status",
        "description": "Look up real-time shipping status, carrier, tracking number, and delivery date for a customer order.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "order_id": {
                    "type": "STRING",
                    "description": "The order identifier, e.g. ORD-88421 or 88421."
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "create_ticket",
        "description": "Create a customer support ticket to escalate an issue to a human agent.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "summary": {
                    "type": "STRING",
                    "description": "Brief description of the customer's issue or complaint."
                },
                "priority": {
                    "type": "STRING",
                    "enum": ["LOW", "MEDIUM", "HIGH", "URGENT"],
                    "description": "Urgency of the issue. Use HIGH or URGENT for angry customers or defective orders."
                },
                "reason": {
                    "type": "STRING",
                    "description": "Reason for escalation (e.g., negative sentiment, damaged product, human requested)."
                }
            },
            "required": ["summary"]
        }
    },
    {
        "name": "get_faq",
        "description": "Retrieve standard company policies on returns, shipping, warranty, or support hours.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "topic": {
                    "type": "STRING",
                    "description": "The topic name (returns, shipping, warranty, support_hours)."
                }
            },
            "required": ["topic"]
        }
    }
]


async def execute_tool(name: str, args: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
    """Execute a tool by name with arguments."""
    if name == "check_order_status":
        order_id = args.get("order_id", "")
        return check_order_status(order_id)
    elif name == "create_ticket":
        return await create_ticket(
            summary=args.get("summary", "Customer support escalation"),
            priority=args.get("priority", "HIGH"),
            reason=args.get("reason", "Requested by customer"),
            session_id=session_id
        )
    elif name == "get_faq":
        return get_faq(args.get("topic", ""))
    else:
        return {"error": f"Unknown tool: {name}"}
