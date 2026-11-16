import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Float, Integer, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    language = Column(String(10), default="en")
    is_escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text, nullable=True)

    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")
    tickets = relationship("SupportTicket", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), ForeignKey("conversation_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    sentiment = Column(String(20), nullable=True)  # "POSITIVE", "NEUTRAL", "NEGATIVE", "VERY_NEGATIVE"
    sentiment_score = Column(Float, nullable=True)
    intent = Column(String(50), nullable=True)
    language = Column(String(10), default="en")
    tokens = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ConversationSession", back_populates="messages")


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(String(32), primary_key=True)  # e.g. TICK-92841
    session_id = Column(String(64), ForeignKey("conversation_sessions.id"), nullable=True)
    user_email = Column(String(255), nullable=True)
    summary = Column(Text, nullable=False)
    priority = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, URGENT
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ConversationSession", back_populates="tickets")
