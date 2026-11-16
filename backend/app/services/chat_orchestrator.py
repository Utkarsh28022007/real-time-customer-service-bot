import asyncio
import logging
import uuid
from typing import Dict, Any, Callable, Awaitable, Optional, List

from backend.app.core.config import settings
from backend.app.core.guardrails import mask_pii, check_out_of_scope_or_harmful, SYSTEM_GUARDRAILS_PROMPT
from backend.app.core.rate_limiter import rate_limiter
from backend.app.db.database import (
    get_or_create_session,
    save_message,
    get_recent_messages
)
from backend.app.nlp.analyzer import analyze_message_nlp, NLPAnalysisResult
from backend.app.rag.chroma_rag import KnowledgeBaseRAG
from backend.app.tools.registry import check_order_status, create_ticket, execute_tool
from backend.app.services.gemini_client import gemini_manager

logger = logging.getLogger("chat.orchestrator")


class ChatOrchestrator:
    """
    Coordinates incoming user messages, NLP classification, RAG retrieval,
    tool execution, token-by-token streaming, and conversation persistence.
    """

    def __init__(self):
        self.rag = KnowledgeBaseRAG(gemini_manager.client)

    async def init(self):
        """Index knowledge base chunks if not yet loaded."""
        try:
            await self.rag.ingest_documents()
        except Exception as e:
            logger.warning(f"Could not initialize ChromaDB immediately: {e}")

    async def process_turn(
        self,
        session_id: str,
        raw_message: str,
        emit: Callable[[Dict[str, Any]], Awaitable[None]]
    ):
        """Processes a single conversational turn over WebSocket."""
        # 1. Rate limiting check
        if not rate_limiter.is_allowed(session_id):
            await emit({
                "type": "error",
                "message": "Rate limit exceeded. Please wait a moment before sending another message.",
                "code": "RATE_LIMITED"
            })
            return

        # 2. PII Masking
        clean_text = mask_pii(raw_message.strip())
        logger.info(f"Session {session_id} received message: {clean_text}")

        # Ensure session exists in DB
        await get_or_create_session(session_id)

        # 3. Guardrail check for harmful or prompt injection
        is_blocked, refusal_text = check_out_of_scope_or_harmful(raw_message)
        if is_blocked:
            await emit({"type": "status_update", "status": "guardrail_triggered"})
            await emit({
                "type": "meta_update",
                "intent": "OUT_OF_SCOPE",
                "sentiment": "NEUTRAL",
                "score": 0.0,
                "language": "en"
            })
            # Stream refusal
            for word in refusal_text.split(" "):
                await emit({"type": "bot_chunk", "token": word + " "})
                await asyncio.sleep(0.03)

            # Persist turn
            await save_message(str(uuid.uuid4()), session_id, "user", clean_text, intent="OUT_OF_SCOPE")
            await save_message(str(uuid.uuid4()), session_id, "assistant", refusal_text, intent="OUT_OF_SCOPE")

            await emit({"type": "bot_done", "message_id": str(uuid.uuid4())})
            return

        # 4. NLP Analysis
        await emit({"type": "status_update", "status": "analyzing"})
        nlp_res = await analyze_message_nlp(clean_text, gemini_manager.client)
        
        await emit({
            "type": "meta_update",
            "intent": nlp_res.intent,
            "sentiment": nlp_res.sentiment,
            "score": nlp_res.sentiment_score,
            "language": nlp_res.language
        })

        # 5. Escalation check
        ticket_data = None
        if nlp_res.requires_escalation:
            priority = "URGENT" if nlp_res.sentiment == "VERY_NEGATIVE" else "HIGH"
            ticket_data = await create_ticket(
                summary=clean_text[:120],
                priority=priority,
                reason=f"Auto-escalated: {nlp_res.sentiment} sentiment / {nlp_res.intent} intent",
                session_id=session_id
            )
            await emit({
                "type": "escalation",
                "ticket_id": ticket_data["ticket_id"],
                "priority": ticket_data["priority"],
                "reason": f"Escalated due to {nlp_res.sentiment.lower().replace('_', ' ')} sentiment or customer request."
            })

        # 6. Tool execution if relevant (e.g., Order Status)
        tool_call_result = None
        order_id = nlp_res.entities.get("order_id")
        if not order_id and ("ord-" in clean_text.lower() or "order" in clean_text.lower()):
            import re
            m = re.search(r'\b(?:ORD-)?(\d{4,6})\b', clean_text, re.IGNORECASE)
            if m:
                order_id = f"ORD-{m.group(1)}"

        if (nlp_res.intent == "ORDER_STATUS" or order_id) and order_id:
            await emit({"type": "status_update", "status": "executing_tool", "tool": "check_order_status"})
            tool_call_result = check_order_status(order_id)
            await emit({
                "type": "tool_call",
                "tool": "check_order_status",
                "args": {"order_id": order_id},
                "result": tool_call_result
            })

        # 7. Knowledge Base RAG Retrieval
        rag_context = ""
        retrieved_chunks = []
        if nlp_res.intent in ["REFUND_REQUEST", "BILLING_INQUIRY", "GENERAL_FAQ", "TECHNICAL_SUPPORT", "COMPLAINT"]:
            await emit({"type": "status_update", "status": "retrieving"})
            retrieved_chunks = await self.rag.search(clean_text, top_k=3)
            rag_context = self.rag.build_grounded_context(retrieved_chunks)

        # 8. Construct Prompt & Stream Response
        await emit({"type": "status_update", "status": "generating"})
        
        # Load conversation history
        history = await get_recent_messages(session_id, limit=settings.MAX_HISTORY_TURNS)
        history_str = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in history[-6:]])

        prompt_parts = [
            f"System Instructions:\n{SYSTEM_GUARDRAILS_PROMPT}",
            f"Customer's Detected Language: {nlp_res.language.upper()}",
            f"Detected Intent: {nlp_res.intent} | Sentiment: {nlp_res.sentiment} ({nlp_res.sentiment_score})",
        ]
        if ticket_data:
            prompt_parts.append(f"A human support ticket has been opened: Ticket ID {ticket_data['ticket_id']}. Acknowledge this with empathy.")
        if tool_call_result:
            prompt_parts.append(f"Order Status Tool Result: {tool_call_result}")
        if rag_context:
            prompt_parts.append(rag_context)
        if history_str:
            prompt_parts.append(f"Recent Conversation:\n{history_str}")
        prompt_parts.append(f"Customer: {clean_text}\nAssistant:")

        full_prompt = "\n\n".join(prompt_parts)

        # 9. Stream Tokens
        full_bot_response = ""
        used_gemini = False

        if gemini_manager.client and settings.has_gemini_key:
            try:
                model_name = settings.GEMINI_COMPLEX_MODEL if nlp_res.intent == "COMPLAINT" else settings.GEMINI_CHAT_MODEL
                stream_response = await gemini_manager.client.aio.models.generate_content_stream(
                    model=model_name,
                    contents=full_prompt,
                )
                used_gemini = True
                async for chunk in stream_response:
                    if chunk.text:
                        full_bot_response += chunk.text
                        await emit({"type": "bot_chunk", "token": chunk.text})
            except Exception as e:
                logger.error(f"Live Gemini streaming error: {e}. Falling back to grounded response generator.")
                used_gemini = False

        if not used_gemini:
            generated_text = self._synthesize_grounded_response(
                clean_text, nlp_res, tool_call_result, ticket_data, retrieved_chunks
            )
            full_bot_response = generated_text
            words = generated_text.split(" ")
            for i, word in enumerate(words):
                token = word if i == len(words) - 1 else word + " "
                await emit({"type": "bot_chunk", "token": token})
                await asyncio.sleep(0.02)

        # 10. Persist Conversation in Database
        await save_message(
            msg_id=str(uuid.uuid4()),
            session_id=session_id,
            role="user",
            content=clean_text,
            sentiment=nlp_res.sentiment,
            sentiment_score=nlp_res.sentiment_score,
            intent=nlp_res.intent,
            language=nlp_res.language,
            tokens=len(clean_text.split())
        )
        await save_message(
            msg_id=str(uuid.uuid4()),
            session_id=session_id,
            role="assistant",
            content=full_bot_response,
            sentiment="NEUTRAL",
            sentiment_score=0.0,
            intent=nlp_res.intent,
            language=nlp_res.language,
            tokens=len(full_bot_response.split())
        )

        await emit({
            "type": "bot_done",
            "message_id": str(uuid.uuid4()),
            "total_tokens": len(full_bot_response.split())
        })

    def _synthesize_grounded_response(
        self,
        query: str,
        nlp_res: NLPAnalysisResult,
        tool_result: Optional[Dict[str, Any]],
        ticket_data: Optional[Dict[str, Any]],
        chunks: List[Dict[str, Any]]
    ) -> str:
        """Generates grounded fallback response based on tools, tickets, and knowledge."""
        lang = nlp_res.language

        # Ticket / Escalation response
        if ticket_data:
            tid = ticket_data["ticket_id"]
            if lang == "es":
                return f"Lamento mucho los inconvenientes causados. He creado el ticket de soporte #{tid} con prioridad {ticket_data['priority']}. Un agente humano se pondrá en contacto con usted de inmediato."
            return f"I sincerely apologize for the frustration this has caused. I have escalated this issue and created Support Ticket #{tid} with {ticket_data['priority']} priority. A senior support representative has been notified and will assist you directly."

        # Order status tool response
        if tool_result:
            if tool_result.get("found"):
                oid = tool_result["order_id"]
                status = tool_result["status"]
                carrier = tool_result["carrier"]
                est = tool_result["estimated_delivery"]
                tracking = tool_result["tracking_number"]
                items = ", ".join(tool_result["items"])
                return f"Here is the latest update for order **{oid}**:\n- **Status:** {status}\n- **Items:** {items}\n- **Carrier:** {carrier} (Tracking: `{tracking}`)\n- **Estimated Delivery:** {est}\n\n{tool_result['notes']}"
            else:
                return tool_result.get("message", f"I could not locate details for that order. Please check the order number.")

        # Friendly greeting
        if nlp_res.intent == "GREETING":
            if lang == "es":
                return "¡Hola! Bienvenido al servicio de atención al cliente de NovaTech. ¿En qué puedo ayudarle hoy? Puedo consultar el estado de su pedido, orientarle sobre devoluciones o resolver cualquier duda sobre nuestros productos."
            elif lang == "fr":
                return "Bonjour ! Bienvenue au service client NovaTech. Comment puis-je vous aider aujourd'hui ? Je peux vérifier l'état d'une commande, vous guider pour un retour ou répondre à vos questions."
            elif lang == "de":
                return "Hallo! Willkommen beim NovaTech Kundenservice. Wie kann ich Ihnen heute helfen? Ich kann Ihren Bestellstatus prüfen, Sie bei Rücksendungen unterstützen oder Fragen beantworten."
            return "Hello! Welcome to NovaTech Customer Care. How can I assist you today? I can help you check your order status, guide you through a return or refund, answer questions about our products, or connect you with a live specialist."

        # Out of scope
        if nlp_res.intent == "OUT_OF_SCOPE":
            return "I am NovaTech's dedicated customer support assistant. I can only answer questions related to our products, orders, shipping, returns, and services. Is there anything regarding your NovaTech account or purchase I can help you with?"

        # RAG grounded response
        if chunks:
            top_chunk = chunks[0]["text"]
            lines = [l.strip() for l in top_chunk.split("\n") if l.strip() and not l.startswith("#")]
            summary = "\n".join(lines[:4])
            return f"Based on our policy documentation:\n\n{summary}\n\nPlease let me know if you need help initiating a request or have further questions!"

        return "I'm sorry, I don't have that specific information in our records. Would you like me to connect you with a live customer support representative?"


orchestrator = ChatOrchestrator()
