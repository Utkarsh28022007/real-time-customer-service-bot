export type Role = 'user' | 'assistant' | 'system';

export interface ToolCallInfo {
  tool: string;
  args: Record<string, any>;
  result: Record<string, any>;
}

export interface EscalationInfo {
  ticket_id: string;
  priority: string;
  reason: string;
}

export interface MessageMeta {
  intent?: string;
  sentiment?: string;
  score?: number;
  language?: string;
}

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  sentiment?: string;
  sentiment_score?: number;
  intent?: string;
  language?: string;
  toolCall?: ToolCallInfo;
  isStreaming?: boolean;
  createdAt: string;
}

export interface AdminMetrics {
  total_conversations: number;
  total_messages: number;
  escalated_conversations: number;
  escalation_rate_pct: number;
  average_sentiment_score: number;
  total_tickets: number;
  open_tickets: number;
  intent_distribution: Record<string, number>;
  sentiment_distribution: Record<string, number>;
}

export interface SupportTicket {
  id: string;
  session_id?: string;
  user_email?: string;
  summary: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  reason?: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED';
  created_at: string;
}

export interface ConversationSummary {
  id: string;
  created_at: string;
  updated_at: string;
  language: string;
  is_escalated: boolean;
  escalation_reason?: string;
  last_message?: string;
  last_message_role?: string;
}
