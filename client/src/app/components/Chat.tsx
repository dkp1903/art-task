// components/Chat.tsx
import { useEffect, useRef, useState } from 'react';
import { generateToken, connectWebSocket } from '../utils/websocket';

interface Message {
  id: number;
  content: string;
  editable: boolean;
  sender: 'user' | 'bot';
}

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [editingId, setEditingId] = useState<number | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const token = generateToken();
    wsRef.current = connectWebSocket(token);

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleSendMessage = () => {
    if (input.trim() === '') return;

    if (editingId !== null) {
      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.id === editingId ? { ...msg, content: input, editable: false } : msg
        )
      );
      setEditingId(null);
    } else {
      const newMessage: Message = {
        id: Date.now(),
        content: input,
        editable: false,
        sender: 'user',
      };
      setMessages([...messages, newMessage]);

      // Send the message to the WebSocket server if needed
      if (wsRef.current) {
        wsRef.current.send(input);
      }
    }

    setInput('');
  };

  const handleEditMessage = (id: number) => {
    const message = messages.find((msg) => msg.id === id);
    if (message) {
      setInput(message.content);
      setEditingId(id);
    }
  };

  const handleDeleteMessage = (id: number) => {
    setMessages((prevMessages) => prevMessages.filter((msg) => msg.id !== id));
  };

  return (
    <div className="max-w-md mx-auto my-8 p-4 bg-white rounded-lg shadow-md">
      <div className="text-center mb-4">
        <img
          src="/avatar.png" // Replace with the actual avatar image source
          alt="Avatar"
          className="w-12 h-12 rounded-full mx-auto"
        />
        <h2 className="text-lg font-semibold mt-2">Hey👋, I’m Ava</h2>
        <p className="text-gray-600">Ask me anything or pick a place to start</p>
      </div>

      <div className="mb-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex items-start mb-2 ${msg.sender === 'user' ? 'justify-end' : ''}`}>
            <div className="relative">
              {msg.sender === 'bot' && (
                <img
                  src="/avatar.png" // Replace with the actual avatar image source
                  alt="Avatar"
                  className="w-8 h-8 rounded-full mr-3"
                />
              )}
              <div
                className={`p-3 rounded-lg ${
                  msg.sender === 'user' ? 'bg-purple-500 text-white' : 'bg-gray-100 text-gray-700'
                }`}
              >
                {msg.content}
              </div>
              {msg.sender === 'user' && (
                <div className="absolute right-0 top-0 mt-1 mr-1 flex space-x-1">
                  <button
                    onClick={() => handleEditMessage(msg.id)}
                    className="text-xs text-blue-500 hover:underline"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteMessage(msg.id)}
                    className="text-xs text-red-500 hover:underline"
                  >
                    Delete
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4">
        <input
          type="text"
          placeholder="Your question"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
        />
        <button
          onClick={handleSendMessage}
          className="mt-2 w-full px-4 py-2 bg-purple-500 text-white rounded-lg"
        >
          {editingId ? 'Save' : 'Send'}
        </button>
      </div>

      <div className="mt-4">
        <select className="w-full px-4 py-2 border border-gray-300 rounded-lg">
          <option value="Onboarding">Onboarding</option>
          <option value="Support">Support</option>
          <option value="Feedback">Feedback</option>
        </select>
      </div>
    </div>
  );
};

export default Chat;
