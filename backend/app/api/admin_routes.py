from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.db.database import (
    get_metrics,
    list_sessions,
    get_session_transcript,
    list_tickets,
    update_ticket_status
)
from backend.app.services.chat_orchestrator import orchestrator

router = APIRouter(prefix="/api/admin", tags=["admin"])


class TicketStatusUpdate(BaseModel):
    status: str  # OPEN, IN_PROGRESS, RESOLVED


@router.get("/metrics")
async def get_dashboard_metrics():
    """Computes KPIs and statistical trends for the customer service dashboard."""
    return await get_metrics()


@router.get("/conversations")
async def list_conversations(limit: int = 50):
    """Returns recent conversation sessions."""
    return await list_sessions(limit)


@router.get("/conversations/{session_id}")
async def get_conversation_history(session_id: str):
    """Retrieves the full message history for a given session."""
    data = await get_session_transcript(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Conversation session not found")
    return data


@router.get("/tickets")
async def get_tickets(limit: int = 50):
    """Lists support tickets."""
    return await list_tickets(limit)


@router.patch("/tickets/{ticket_id}")
async def patch_ticket_status(ticket_id: str, body: TicketStatusUpdate):
    """Updates status for a support ticket."""
    success = await update_ticket_status(ticket_id, body.status)
    if not success:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"success": True, "ticket_id": ticket_id, "status": body.status.upper()}


@router.post("/rag/reindex")
async def trigger_rag_reindex():
    """Forces re-indexing of knowledge base markdown files."""
    count = await orchestrator.rag.ingest_documents(force_reload=True)
    return {"success": True, "indexed_chunks": count}
