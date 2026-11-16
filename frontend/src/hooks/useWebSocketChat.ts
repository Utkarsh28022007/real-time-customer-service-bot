import { useState, useEffect, useRef, useCallback } from 'react';
import { ChatMessage, EscalationInfo, ToolCallInfo, MessageMeta } from '../types';

export function useWebSocketChat(sessionId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStatus, setCurrentStatus] = useState<string>('');
  const [activeEscalation, setActiveEscalation] = useState<EscalationInfo | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [currentMeta, setCurrentMeta] = useState<MessageMeta>({});

  const wsRef = useRef<WebSocket | null>(null);
  const streamingTextRef = useRef<string>('');

  useEffect(() => {
    let isMounted = true;
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.hostname}:8000/ws/chat/${sessionId}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      if (isMounted) setIsConnected(true);
      console.log('Connected to Chatbot WebSocket:', wsUrl);
    };

    ws.onclose = () => {
      if (isMounted) {
        setIsConnected(false);
        setIsStreaming(false);
      }
      console.log('Disconnected from Chatbot WebSocket');
    };

    ws.onerror = (err) => {
      console.error('WebSocket Error:', err);
      if (isMounted) setIsConnected(false);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case 'connection_ack':
            console.log('Server ACK:', data.message);
            break;

          case 'status_update':
            setCurrentStatus(data.status);
            break;

          case 'meta_update':
            setCurrentMeta({
              intent: data.intent,
              sentiment: data.sentiment,
              score: data.score,
              language: data.language,
            });
            break;

          case 'escalation':
            setActiveEscalation({
              ticket_id: data.ticket_id,
              priority: data.priority,
              reason: data.reason,
            });
            break;

          case 'tool_call':
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last && last.role === 'assistant') {
                last.toolCall = {
                  tool: data.tool,
                  args: data.args,
                  result: data.result,
                };
              }
              return updated;
            });
            break;

          case 'bot_chunk':
            setIsStreaming(true);
            streamingTextRef.current += data.token;
            const currentSnapshot = streamingTextRef.current;

            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (!last || last.role !== 'assistant' || !last.isStreaming) {
                updated.push({
                  id: 'bot-' + Date.now(),
                  role: 'assistant',
                  content: currentSnapshot,
                  isStreaming: true,
                  createdAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                });
              } else {
                updated[updated.length - 1] = {
                  ...last,
                  content: currentSnapshot,
                };
              }
              return updated;
            });
            break;

          case 'bot_done':
            setIsStreaming(false);
            setCurrentStatus('');
            streamingTextRef.current = '';
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last && last.role === 'assistant') {
                last.isStreaming = false;
              }
              return updated;
            });
            break;

          case 'error':
            setIsStreaming(false);
            setCurrentStatus('');
            streamingTextRef.current = '';
            setMessages((prev) => [
              ...prev,
              {
                id: 'err-' + Date.now(),
                role: 'system',
                content: `⚠️ Error: ${data.message}`,
                createdAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              },
            ]);
            break;

          default:
            console.log('Unhandled packet:', data);
        }
      } catch (err) {
        console.error('Failed to parse incoming WebSocket message', err);
      }
    };

    return () => {
      isMounted = false;
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
    };
  }, [sessionId]);

  const sendMessage = useCallback((content: string) => {
    if (!content.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.warn('Cannot send: WebSocket is not connected.');
      return;
    }

    streamingTextRef.current = '';

    const userMsg: ChatMessage = {
      id: 'user-' + Date.now(),
      role: 'user',
      content: content.trim(),
      createdAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);
    setCurrentStatus('sending');

    wsRef.current.send(
      JSON.stringify({
        session_id: sessionId,
        content: content.trim(),
      })
    );
  }, [sessionId]);

  const clearChat = useCallback(() => {
    streamingTextRef.current = '';
    setMessages([]);
    setActiveEscalation(null);
    setCurrentMeta({});
  }, []);

  return {
    messages,
    sendMessage,
    isStreaming,
    currentStatus,
    activeEscalation,
    isConnected,
    currentMeta,
    clearChat,
  };
}
