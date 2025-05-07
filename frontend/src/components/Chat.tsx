import { useState, useRef, useEffect } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Generate or load session_id
  const getSessionId = () => {
    let sessionId = localStorage.getItem('session_id');
    if (!sessionId) {
      sessionId = Math.random().toString(36).substring(2) + Date.now().toString(36);
      localStorage.setItem('session_id', sessionId);
    }
    return sessionId;
  };
  const sessionId = getSessionId();

  useEffect(() => {
    ws.current = new WebSocket(
      window.location.protocol === 'https:'
        ? 'wss://' + window.location.host + '/ws'
        : 'ws://' + window.location.host + '/ws'
    );

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.error) {
        alert(data.error);
        setIsLoading(false);
        return;
      }
      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    };

    ws.current.onerror = () => {
      alert('WebSocket Error: Failed to connect to backend.');
      setIsLoading(false);
    };

    return () => {
      ws.current?.close();
    };
    // eslint-disable-next-line
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !ws.current || ws.current.readyState !== 1) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    ws.current.send(
      JSON.stringify({
        prompt: input,
        model: 'mistral',
        session_id: sessionId,
        conversation_id: conversationId,
      })
    );
    setInput('');
  };

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', height: '100vh', display: 'flex', flexDirection: 'column', padding: 16 }}>
      <div style={{ flex: 1, overflowY: 'auto', border: '1px solid #ddd', borderRadius: 8, padding: 16, marginBottom: 16, background: '#fafbfc' }}>
        {messages.map((message, index) => (
          <div
            key={index}
            style={{
              marginBottom: 16,
              padding: 12,
              borderRadius: 8,
              background: message.role === 'user' ? '#e3f0ff' : '#f3f3f3',
              alignSelf: message.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%',
            }}
          >
            <div style={{ fontWeight: 'bold', marginBottom: 4 }}>
              {message.role === 'user' ? 'You' : 'AI Assistant'}
            </div>
            <div>{message.content}</div>
          </div>
        ))}
        {isLoading && (
          <div style={{ textAlign: 'center', margin: 16 }}>
            <span>Loading...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 8 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={isLoading}
          style={{ flex: 1, padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
        />
        <button
          type="submit"
          disabled={isLoading}
          style={{ padding: '8px 16px', borderRadius: 4, border: 'none', background: '#3182ce', color: '#fff', fontWeight: 'bold', cursor: isLoading ? 'not-allowed' : 'pointer' }}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};
