import React, { useState } from 'react';
import { useWebSocketChat } from './hooks/useWebSocketChat';
import { ChatContainer } from './components/Chat/ChatContainer';
import { AdminDashboard } from './components/Admin/AdminDashboard';

export function App() {
  const [sessionId, setSessionId] = useState<string>(() => 'sess-' + Math.random().toString(36).substring(2, 9));
  const [activeTab, setActiveTab] = useState<'chat' | 'admin'>('chat');

  const {
    messages,
    sendMessage,
    isStreaming,
    currentStatus,
    activeEscalation,
    isConnected,
    currentMeta,
    clearChat,
  } = useWebSocketChat(sessionId);

  const handleResetSession = () => {
    clearChat();
    setSessionId('sess-' + Math.random().toString(36).substring(2, 9));
  };

  return (
    <div className="min-h-screen bg-slate-950 font-sans antialiased text-slate-100">
      {activeTab === 'chat' ? (
        <ChatContainer
          messages={messages}
          isStreaming={isStreaming}
          isConnected={isConnected}
          currentStatus={currentStatus}
          activeEscalation={activeEscalation}
          currentMeta={currentMeta}
          onSendMessage={sendMessage}
          onReset={handleResetSession}
          onOpenAdmin={() => setActiveTab('admin')}
        />
      ) : (
        <AdminDashboard onBackToChat={() => setActiveTab('chat')} />
      )}
    </div>
  );
}

export default App;
