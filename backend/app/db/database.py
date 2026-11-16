import os
import aiosqlite
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.core.config import settings

DB_FILE = "./data/chatbot.db"


def get_db_path() -> str:
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite+aiosqlite:///"):
        path = db_url.replace("sqlite+aiosqlite:///", "")
    elif db_url.startswith("sqlite:///"):
        path = db_url.replace("sqlite:///", "")
    else:
        path = DB_FILE
    
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    return path


async def init_db():
    """Initializes tables for sessions, messages, and support tickets."""
    path = get_db_path()
    async with aiosqlite.connect(path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                is_escalated INTEGER DEFAULT 0,
                escalation_reason TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sentiment TEXT,
                sentiment_score REAL,
                intent TEXT,
                language TEXT DEFAULT 'en',
                tokens INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES conversation_sessions (id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                user_email TEXT,
                summary TEXT NOT NULL,
                priority TEXT DEFAULT 'MEDIUM',
                reason TEXT,
                status TEXT DEFAULT 'OPEN',
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES conversation_sessions (id)
            )
        """)
        await db.commit()


async def get_or_create_session(session_id: str, language: str = "en") -> Dict[str, Any]:
    path = get_db_path()
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM conversation_sessions WHERE id = ?", (session_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)

        await db.execute(
            "INSERT INTO conversation_sessions (id, created_at, updated_at, language, is_escalated) VALUES (?, ?, ?, ?, 0)",
            (session_id, now, now, language)
        )
        await db.commit()
        return {
            "id": session_id,
            "created_at": now,
            "updated_at": now,
            "language": language,
            "is_escalated": 0,
            "escalation_reason": None
        }


async def save_message(
    msg_id: str,
    session_id: str,
    role: str,
    content: str,
    sentiment: Optional[str] = None,
    sentiment_score: Optional[float] = None,
    intent: Optional[str] = None,
    language: str = "en",
    tokens: int = 0
) -> Dict[str, Any]:
    path = get_db_path()
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(path) as db:
        await db.execute("""
            INSERT INTO messages (id, session_id, role, content, sentiment, sentiment_score, intent, language, tokens, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (msg_id, session_id, role, content, sentiment, sentiment_score, intent, language, tokens, now))
        
        await db.execute(
            "UPDATE conversation_sessions SET updated_at = ?, language = ? WHERE id = ?",
            (now, language, session_id)
        )
        await db.commit()

    return {
        "id": msg_id,
        "session_id": session_id,
        "role": role,
        "content": content,
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "intent": intent,
        "language": language,
        "created_at": now
    }


async def get_recent_messages(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    path = get_db_path()
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
            (session_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            messages = [dict(r) for r in rows]
            messages.reverse()
            return messages


async def save_ticket(
    ticket_id: str,
    session_id: Optional[str],
    user_email: Optional[str],
    summary: str,
    priority: str = "MEDIUM",
    reason: Optional[str] = None,
    status: str = "OPEN"
) -> Dict[str, Any]:
    path = get_db_path()
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(path) as db:
        await db.execute("""
            INSERT INTO support_tickets (id, session_id, user_email, summary, priority, reason, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (ticket_id, session_id, user_email, summary, priority, reason, status, now))

        if session_id:
            await db.execute(
                "UPDATE conversation_sessions SET is_escalated = 1, escalation_reason = ? WHERE id = ?",
                (reason or summary, session_id)
            )
        await db.commit()

    return {
        "id": ticket_id,
        "session_id": session_id,
        "user_email": user_email,
        "summary": summary,
        "priority": priority,
        "reason": reason,
        "status": status,
        "created_at": now
    }


async def list_tickets(limit: int = 50) -> List[Dict[str, Any]]:
    path = get_db_path()
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM support_tickets ORDER BY created_at DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def update_ticket_status(ticket_id: str, status: str) -> bool:
    path = get_db_path()
    async with aiosqlite.connect(path) as db:
        cursor = await db.execute(
            "UPDATE support_tickets SET status = ? WHERE id = ?", (status.upper(), ticket_id)
        )
        await db.commit()
        return cursor.rowcount > 0


async def list_sessions(limit: int = 50) -> List[Dict[str, Any]]:
    path = get_db_path()
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM conversation_sessions ORDER BY updated_at DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            sessions = []
            for r in rows:
                s = dict(r)
                # Fetch last message
                async with db.execute(
                    "SELECT content, role FROM messages WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
                    (s["id"],)
                ) as m_cursor:
                    last_m = await m_cursor.fetchone()
                    s["last_message"] = last_m["content"] if last_m else None
                    s["last_message_role"] = last_m["role"] if last_m else None
                sessions.append(s)
            return sessions


async def get_session_transcript(session_id: str) -> Optional[Dict[str, Any]]:
    path = get_db_path()
    async with aiosqlite.connect(path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM conversation_sessions WHERE id = ?", (session_id,)) as cursor:
            s_row = await cursor.fetchone()
            if not s_row:
                return None
            session = dict(s_row)

        async with db.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC", (session_id,)
        ) as cursor:
            m_rows = await cursor.fetchall()
            messages = [dict(m) for m in m_rows]

        return {
            "session": session,
            "messages": messages
        }


async def get_metrics() -> Dict[str, Any]:
    path = get_db_path()
    async with aiosqlite.connect(path) as db:
        async with db.execute("SELECT COUNT(*) FROM conversation_sessions") as cur:
            total_sessions = (await cur.fetchone())[0] or 0

        async with db.execute("SELECT COUNT(*) FROM conversation_sessions WHERE is_escalated = 1") as cur:
            escalated_sessions = (await cur.fetchone())[0] or 0

        async with db.execute("SELECT COUNT(*) FROM messages") as cur:
            total_messages = (await cur.fetchone())[0] or 0

        async with db.execute("SELECT AVG(sentiment_score) FROM messages WHERE sentiment_score IS NOT NULL") as cur:
            avg_sentiment = (await cur.fetchone())[0] or 0.0

        async with db.execute("SELECT COUNT(*) FROM support_tickets") as cur:
            total_tickets = (await cur.fetchone())[0] or 0

        async with db.execute("SELECT COUNT(*) FROM support_tickets WHERE status = 'OPEN'") as cur:
            open_tickets = (await cur.fetchone())[0] or 0

        # Intent distribution
        intent_dist = {}
        async with db.execute("""
            SELECT intent, COUNT(*) FROM messages 
            WHERE role = 'user' AND intent IS NOT NULL 
            GROUP BY intent
        """) as cur:
            for row in await cur.fetchall():
                intent_dist[row[0]] = row[1]

        # Sentiment distribution
        sentiment_dist = {}
        async with db.execute("""
            SELECT sentiment, COUNT(*) FROM messages 
            WHERE role = 'user' AND sentiment IS NOT NULL 
            GROUP BY sentiment
        """) as cur:
            for row in await cur.fetchall():
                sentiment_dist[row[0]] = row[1]

        esc_rate = round((escalated_sessions / total_sessions * 100), 1) if total_sessions > 0 else 0.0

        return {
            "total_conversations": total_sessions,
            "total_messages": total_messages,
            "escalated_conversations": escalated_sessions,
            "escalation_rate_pct": esc_rate,
            "average_sentiment_score": round(avg_sentiment, 2),
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "intent_distribution": intent_dist,
            "sentiment_distribution": sentiment_dist,
        }
