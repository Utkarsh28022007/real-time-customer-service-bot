import React, { useRef, useEffect } from 'react';
import { Header } from './Header';
import { MessageBubble } from './MessageBubble';
import { EscalationCard } from './EscalationCard';
import { ChatInput } from './ChatInput';
import { ChatMessage, EscalationInfo, MessageMeta } from '../../types';
import { MessageSquareDashed } from 'lucide-react';

interface ChatContainerProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  isConnected: boolean;
  currentStatus: string;
  activeEscalation: EscalationInfo | null;
  currentMeta: MessageMeta;
  onSendMessage: (msg: string) => void;
  onReset: () => void;
  onOpenAdmin: () => void;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  messages,
  isStreaming,
  isConnected,
  currentStatus,
  activeEscalation,
  currentMeta,
  onSendMessage,
  onReset,
  onOpenAdmin,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentStatus]);

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-slate-900 border-x border-slate-800 shadow-2xl">
      <Header
        isConnected={isConnected}
        isEscalated={!!activeEscalation}
        currentMeta={currentMeta}
        onReset={onReset}
        onOpenAdmin={onOpenAdmin}
      />

      {activeEscalation && <EscalationCard escalation={activeEscalation} />}

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 space-y-3">
            <div className="w-16 h-16 rounded-2xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400">
              <MessageSquareDashed className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-200">Welcome to NovaTech Customer Support</h3>
              <p className="text-xs text-slate-400 max-w-sm mt-1">
                Ask about our return policies, track your shipments in real-time, or request customer assistance.
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
        )}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput
        onSendMessage={onSendMessage}
        isStreaming={isStreaming}
        isConnected={isConnected}
        currentStatus={currentStatus}
      />
    </div>
  );
};
