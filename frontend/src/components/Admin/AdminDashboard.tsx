import React, { useState, useEffect } from 'react';
import { 
  BarChart2, ArrowLeft, RefreshCw, Ticket, MessageSquare, AlertTriangle, 
  Smile, ShieldCheck, Database, CheckCircle, Clock 
} from 'lucide-react';
import { AdminMetrics, SupportTicket, ConversationSummary } from '../../types';

interface AdminDashboardProps {
  onBackToChat: () => void;
}

export const AdminDashboard: React.FC<AdminDashboardProps> = ({ onBackToChat }) => {
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [selectedTranscript, setSelectedTranscript] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [reindexing, setReindexing] = useState(false);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [mRes, tRes, cRes] = await Promise.all([
        fetch('http://localhost:8000/api/admin/metrics'),
        fetch('http://localhost:8000/api/admin/tickets'),
        fetch('http://localhost:8000/api/admin/conversations'),
      ]);

      if (mRes.ok) setMetrics(await mRes.json());
      if (tRes.ok) setTickets(await tRes.json());
      if (cRes.ok) setConversations(await cRes.json());
    } catch (err) {
      console.error('Error fetching admin dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleSelectConversation = async (sessionId: string) => {
    setSelectedSessionId(sessionId);
    try {
      const res = await fetch(`http://localhost:8000/api/admin/conversations/${sessionId}`);
      if (res.ok) setSelectedTranscript(await res.json());
    } catch (err) {
      console.error('Error fetching transcript:', err);
    }
  };

  const handleUpdateTicketStatus = async (ticketId: string, newStatus: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/admin/tickets/${ticketId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        setTickets((prev) =>
          prev.map((t) => (t.id === ticketId ? { ...t, status: newStatus as any } : t))
        );
      }
    } catch (err) {
      console.error('Failed to update ticket status', err);
    }
  };

  const handleReindexKnowledgeBase = async () => {
    try {
      setReindexing(true);
      const res = await fetch('http://localhost:8000/api/admin/rag/reindex', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        alert(`Successfully re-indexed ${data.indexed_chunks} knowledge chunks into ChromaDB!`);
      }
    } catch (err) {
      alert('Failed to reindex knowledge base: ' + err);
    } finally {
      setReindexing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToChat}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors border border-slate-700"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              <BarChart2 className="w-6 h-6 text-brand-400" />
              Customer Service Analytics & Admin Portal
            </h1>
            <p className="text-xs text-slate-400">
              Live telemetry, sentiment analysis trends, and human escalation ticket queues
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleReindexKnowledgeBase}
            disabled={reindexing}
            className="flex items-center gap-2 px-3 py-2 bg-indigo-950/60 hover:bg-indigo-900/60 text-indigo-300 border border-indigo-700/50 rounded-xl text-xs font-medium transition-all"
          >
            <Database className="w-4 h-4" />
            <span>{reindexing ? 'Reindexing...' : 'Reindex ChromaDB'}</span>
          </button>
          <button
            onClick={fetchDashboardData}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-xs font-medium transition-all"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-md">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>Total Conversations</span>
              <MessageSquare className="w-4 h-4 text-brand-400" />
            </div>
            <div className="text-2xl font-bold text-slate-100 mt-2">{metrics.total_conversations}</div>
            <div className="text-[11px] text-slate-400 mt-1">{metrics.total_messages} total messages logged</div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-md">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>Escalation Rate</span>
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-amber-400 mt-2">{metrics.escalation_rate_pct}%</div>
            <div className="text-[11px] text-slate-400 mt-1">{metrics.escalated_conversations} sessions escalated</div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-md">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>Avg Sentiment Score</span>
              <Smile className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-emerald-400 mt-2">
              {metrics.average_sentiment_score > 0 ? `+${metrics.average_sentiment_score}` : metrics.average_sentiment_score}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Scale: -1.0 (Critical) to +1.0 (Delighted)</div>
          </div>

          <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-md">
            <div className="flex items-center justify-between text-slate-400 text-xs">
              <span>Support Tickets</span>
              <Ticket className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-2xl font-bold text-slate-100 mt-2">{metrics.total_tickets}</div>
            <div className="text-[11px] text-rose-400 mt-1">{metrics.open_tickets} tickets pending review</div>
          </div>
        </div>
      )}

      {/* Analytics Charts Grid */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Top Intents Distribution */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-md space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Customer Intent Classification Breakdown</h3>
            <div className="space-y-2.5">
              {Object.entries(metrics.intent_distribution).map(([intent, count]) => {
                const maxCount = Math.max(...Object.values(metrics.intent_distribution), 1);
                const pct = Math.round((count / maxCount) * 100);
                return (
                  <div key={intent} className="space-y-1">
                    <div className="flex justify-between text-xs text-slate-300">
                      <span className="font-medium">{intent.replace('_', ' ')}</span>
                      <span className="text-slate-400">{count} queries</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div className="bg-brand-500 h-full rounded-full transition-all" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Sentiment Distribution */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-md space-y-4">
            <h3 className="text-sm font-semibold text-slate-200">Customer Sentiment Distribution</h3>
            <div className="grid grid-cols-2 gap-3">
              {['POSITIVE', 'NEUTRAL', 'NEGATIVE', 'VERY_NEGATIVE'].map((sent) => {
                const count = metrics.sentiment_distribution[sent] || 0;
                let border = 'border-slate-800';
                let text = 'text-slate-300';
                if (sent === 'POSITIVE') { border = 'border-emerald-500/30'; text = 'text-emerald-400'; }
                if (sent === 'NEGATIVE') { border = 'border-amber-500/30'; text = 'text-amber-400'; }
                if (sent === 'VERY_NEGATIVE') { border = 'border-rose-500/40'; text = 'text-rose-400'; }

                return (
                  <div key={sent} className={`p-4 rounded-xl bg-slate-800/60 border ${border}`}>
                    <div className="text-xs text-slate-400 font-medium">{sent.replace('_', ' ')}</div>
                    <div className={`text-xl font-bold mt-1 ${text}`}>{count}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Tickets Queue Table */}
      <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-md space-y-4">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
          <Ticket className="w-4 h-4 text-brand-400" />
          Escalated Support Ticket Queue
        </h3>

        {tickets.length === 0 ? (
          <p className="text-xs text-slate-400 py-4 text-center">No escalated support tickets created yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/80 text-slate-400 font-semibold uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-3 rounded-l-lg">Ticket ID</th>
                  <th className="py-2.5 px-3">Priority</th>
                  <th className="py-2.5 px-3">Issue Summary</th>
                  <th className="py-2.5 px-3">Reason</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 rounded-r-lg">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {tickets.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-2.5 px-3 font-mono font-medium text-brand-300">{t.id}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                          t.priority === 'URGENT'
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                            : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                        }`}
                      >
                        {t.priority}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 max-w-xs truncate text-slate-200">{t.summary}</td>
                    <td className="py-2.5 px-3 text-slate-400">{t.reason}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                          t.status === 'OPEN'
                            ? 'bg-rose-950 text-rose-300 border border-rose-800'
                            : t.status === 'IN_PROGRESS'
                            ? 'bg-blue-950 text-blue-300 border border-blue-800'
                            : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        }`}
                      >
                        {t.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 space-x-2">
                      {t.status !== 'RESOLVED' && (
                        <button
                          onClick={() => handleUpdateTicketStatus(t.id, 'RESOLVED')}
                          className="px-2 py-1 bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 rounded border border-emerald-500/40 font-medium transition-all"
                        >
                          Resolve
                        </button>
                      )}
                      {t.status === 'OPEN' && (
                        <button
                          onClick={() => handleUpdateTicketStatus(t.id, 'IN_PROGRESS')}
                          className="px-2 py-1 bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 rounded border border-blue-500/40 font-medium transition-all"
                        >
                          In Progress
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Conversations History and Transcript Inspector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-md space-y-3">
          <h3 className="text-sm font-semibold text-slate-200">Recent Sessions</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {conversations.map((c) => (
              <div
                key={c.id}
                onClick={() => handleSelectConversation(c.id)}
                className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                  selectedSessionId === c.id
                    ? 'bg-brand-950/60 border-brand-500'
                    : 'bg-slate-800/40 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex justify-between items-center text-slate-400 text-[10px]">
                  <span>{c.id.slice(0, 8)}...</span>
                  {c.is_escalated && (
                    <span className="text-amber-400 font-semibold flex items-center gap-0.5">
                      <AlertTriangle className="w-3 h-3" /> Escalated
                    </span>
                  )}
                </div>
                <div className="text-slate-200 mt-1 truncate">{c.last_message || 'Empty conversation'}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Live Transcript Inspector */}
        <div className="md:col-span-2 p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-md space-y-3">
          <h3 className="text-sm font-semibold text-slate-200">Conversation Transcript Inspector</h3>
          {selectedTranscript ? (
            <div className="space-y-3 max-h-96 overflow-y-auto p-3 bg-slate-950/60 rounded-xl border border-slate-800">
              {selectedTranscript.messages.map((m: any) => (
                <div key={m.id} className="space-y-1">
                  <div className="flex items-center gap-2 text-[10px] text-slate-400">
                    <span className="font-bold uppercase text-slate-300">{m.role}</span>
                    <span>•</span>
                    <span>{m.created_at}</span>
                    {m.intent && <span className="text-brand-400 font-medium">Intent: {m.intent}</span>}
                    {m.sentiment && <span className="text-amber-400 font-medium">Sentiment: {m.sentiment}</span>}
                  </div>
                  <div className="p-2.5 rounded-lg text-xs bg-slate-850 bg-slate-900 border border-slate-800 text-slate-200 whitespace-pre-wrap">
                    {m.content}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-slate-500 text-xs">
              Select a session on the left to inspect full messages and NLP telemetry.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
