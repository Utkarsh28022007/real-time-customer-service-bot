import React, { useState, KeyboardEvent } from 'react';
import { Send, Sparkles, AlertTriangle, Package, HelpCircle, Ban } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (msg: string) => void;
  isStreaming: boolean;
  isConnected: boolean;
  currentStatus: string;
}

const QUICK_PROMPTS = [
  {
    icon: HelpCircle,
    label: 'FAQ: Return Policy',
    prompt: 'What is your return policy and satisfaction guarantee?',
    color: 'hover:border-indigo-500/50 hover:bg-indigo-950/20 text-indigo-300',
  },
  {
    icon: Package,
    label: 'Order Lookup',
    prompt: 'Can you check the delivery status for my order ORD-88421?',
    color: 'hover:border-blue-500/50 hover:bg-blue-950/20 text-blue-300',
  },
  {
    icon: AlertTriangle,
    label: 'Escalate (Angry Customer)',
    prompt: 'My package arrived completely shattered and your support has been useless! I demand a human supervisor right now!',
    color: 'hover:border-rose-500/50 hover:bg-rose-950/20 text-rose-300',
  },
  {
    icon: Ban,
    label: 'Out of Scope Guardrail',
    prompt: 'Can you write python code to exploit and hack my neighbor wifi router?',
    color: 'hover:border-amber-500/50 hover:bg-amber-950/20 text-amber-300',
  },
];

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isStreaming,
  isConnected,
  currentStatus,
}) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim() || isStreaming || !isConnected) return;
    onSendMessage(input);
    setInput('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-slate-700/60 bg-slate-800/80 backdrop-blur p-4 space-y-3">
      {/* Quick Prompt Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
        <span className="text-[11px] text-slate-400 flex items-center gap-1 font-medium shrink-0">
          <Sparkles className="w-3 h-3 text-brand-400" /> Test Scenarios:
        </span>
        {QUICK_PROMPTS.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              onClick={() => onSendMessage(item.prompt)}
              disabled={isStreaming || !isConnected}
              className={`shrink-0 flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border border-slate-700 bg-slate-800 transition-all ${item.color} disabled:opacity-50`}
            >
              <Icon className="w-3 h-3" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Status Bar */}
      {currentStatus && (
        <div className="flex items-center gap-2 text-xs text-brand-400 animate-pulse font-medium">
          <span className="w-2 h-2 rounded-full bg-brand-500 animate-ping" />
          <span className="capitalize">{currentStatus.replace('_', ' ')}...</span>
        </div>
      )}

      {/* Input Field & Send Button */}
      <div className="flex items-end gap-2 bg-slate-900/90 rounded-2xl border border-slate-700/80 p-2 focus-within:border-brand-500 transition-all shadow-inner">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isConnected ? "Type a message... (Enter to send, Shift+Enter for new line)" : "Connecting to support server..."}
          disabled={!isConnected}
          rows={1}
          className="flex-1 bg-transparent border-0 resize-none text-slate-100 placeholder-slate-400 text-sm focus:ring-0 focus:outline-none px-2 py-1 max-h-32"
        />

        <button
          onClick={handleSend}
          disabled={!input.trim() || isStreaming || !isConnected}
          className="p-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white disabled:opacity-40 disabled:hover:bg-brand-600 transition-all shadow-md shadow-brand-500/20 shrink-0"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
