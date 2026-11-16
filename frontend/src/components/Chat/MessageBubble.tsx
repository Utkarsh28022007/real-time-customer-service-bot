import React from 'react';
import { User, Bot, Wrench, Package, Truck, CheckCircle2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { ChatMessage } from '../../types';

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  if (isSystem) {
    return (
      <div className="flex justify-center my-2">
        <div className="bg-slate-800/80 text-slate-300 text-xs px-4 py-2 rounded-full border border-slate-700/60 shadow-sm max-w-lg text-center">
          {message.content}
        </div>
      </div>
    );
  }

  // Sentiment color badges
  const getSentimentBadge = (sentiment?: string, score?: number) => {
    if (!sentiment) return null;
    let color = 'bg-slate-700/50 text-slate-300 border-slate-600/50';
    if (sentiment === 'POSITIVE') color = 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30';
    if (sentiment === 'NEGATIVE') color = 'bg-amber-500/15 text-amber-300 border-amber-500/30';
    if (sentiment === 'VERY_NEGATIVE') color = 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse';

    return (
      <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${color}`}>
        {sentiment} {score !== undefined ? `(${score > 0 ? '+' : ''}${score})` : ''}
      </span>
    );
  };

  const getIntentBadge = (intent?: string) => {
    if (!intent) return null;
    return (
      <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-brand-500/15 text-brand-300 border border-brand-500/30">
        Intent: {intent}
      </span>
    );
  };

  return (
    <div className={`flex gap-3 my-4 ${isUser ? 'flex-row-reverse' : 'flex-row'} animate-fadeIn`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 shadow-md ${
          isUser
            ? 'bg-slate-700 text-slate-200 border border-slate-600'
            : 'bg-gradient-to-tr from-brand-600 to-indigo-500 text-white shadow-brand-500/20'
        }`}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      <div className={`flex flex-col max-w-[82%] sm:max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Metadata badges for user or assistant messages */}
        {(message.intent || message.sentiment) && (
          <div className="flex flex-wrap gap-1.5 mb-1.5">
            {getIntentBadge(message.intent)}
            {getSentimentBadge(message.sentiment, message.sentiment_score)}
          </div>
        )}

        {/* Tool Call Box */}
        {message.toolCall && (
          <div className="mb-2 w-full p-3 bg-slate-800/90 border border-slate-700 rounded-xl text-xs space-y-2 shadow-inner">
            <div className="flex items-center justify-between text-indigo-400 font-medium">
              <span className="flex items-center gap-1.5">
                <Wrench className="w-3.5 h-3.5" />
                <span>Tool Executed: <code className="font-mono">{message.toolCall.tool}</code></span>
              </span>
              <span className="text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Success
              </span>
            </div>

            {message.toolCall.tool === 'check_order_status' && message.toolCall.result?.found && (
              <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 space-y-1">
                <div className="flex items-center justify-between font-semibold text-slate-200">
                  <span className="flex items-center gap-1.5">
                    <Package className="w-3.5 h-3.5 text-brand-400" />
                    {message.toolCall.result.order_id}
                  </span>
                  <span className="text-emerald-400">{message.toolCall.result.status}</span>
                </div>
                <div className="text-[11px] text-slate-400 flex items-center gap-2">
                  <Truck className="w-3 h-3" />
                  <span>{message.toolCall.result.carrier} ({message.toolCall.result.tracking_number})</span>
                  <span>•</span>
                  <span>Est: {message.toolCall.result.estimated_delivery}</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Message Bubble */}
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
            isUser
              ? 'bg-brand-600 text-white rounded-tr-none'
              : 'bg-slate-800/95 text-slate-100 border border-slate-700/70 rounded-tl-none prose prose-invert max-w-none prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-li:my-0.5'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div>
              <ReactMarkdown>{message.content}</ReactMarkdown>
              {message.isStreaming && (
                <span className="inline-block w-2 h-4 ml-1 bg-brand-400 animate-pulse align-middle" />
              )}
            </div>
          )}
        </div>

        {/* Timestamp */}
        <span className="text-[10px] text-slate-400 mt-1 px-1">
          {message.createdAt}
        </span>
      </div>
    </div>
  );
};
