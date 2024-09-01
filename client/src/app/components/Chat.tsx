import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { v4 as uuid4 } from 'uuid';

interface Message {
  id: string; // Changed to string to match UUID type
  content: string;
  editable: boolean;
  sender: 'user' | 'bot';
}

const Chat = () => {
  const [name, setName] = useState('');
  const [token, setToken] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null); // Changed to string
  const wsRef = useRef<WebSocket | null>(null);
  const [context, setContext] = useState('Onboarding');

  const handleNameSubmit = async () => {
    try {
      const response = await axios.post('https://3500-dkp1903-arttask-imbornlwndw.ws-us115.gitpod.io/token', null, {
        params: { name }
      });
      const receivedToken = response.data.token;
      setToken(receivedToken);

      // Establish WebSocket connection
      wsRef.current = new WebSocket(`wss://3500-dkp1903-arttask-imbornlwndw.ws-us115.gitpod.io/chat?token=${receivedToken}`);

      // Handle incoming messages from the server
      wsRef.current.onmessage = (event) => {
        try {

          console.log("data : ", event.data);
          const rawData = event.data
            .replace(/^'{/, '{') // Strip leading single quote and opening curly brace
            .replace(/}'$/, '}') // Strip trailing single quote and closing curly brace
            .replace(/'/g, '"'); // Replace single quotes with double quotes

          // Parse the cleaned string as JSON
          const parsedData = JSON.parse(rawData);
          const message = parsedData.msg; // Extract the `msg` field

        

          const newMessage: Message = {
            id: parsedData.id || uuid4(), // Use uuid for ID
            content: message,
            editable: false,
            sender: 'bot',
          };
          setMessages((prevMessages) => [...prevMessages, newMessage]);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      // Handle WebSocket errors
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      // Handle WebSocket close event
      wsRef.current.onclose = () => {
        console.log('WebSocket connection closed');
      };
    } catch (error) {
      console.error('Error fetching token:', error);
    }
  };

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
        id: uuid4(),
        content: input,
        editable: false,
        sender: 'user',
      };
      setMessages([...messages, newMessage]);

      // Send the message to the WebSocket server
      if (wsRef.current) {
        wsRef.current.send(input);
      }
    }

    setInput('');
  };

  const handleEditMessage = (id: string) => { // Changed to string
    const message = messages.find((msg) => msg.id === id);
    if (message) {
      setInput(message.content);
      setEditingId(id);
    }
  };

  const handleDeleteMessage = (id: string) => { // Changed to string
    setMessages((prevMessages) => prevMessages.filter((msg) => msg.id !== id));
  };

  // New handler for the context select
  const handleContextChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setContext(event.target.value);
    // You can send the context to the server or use it to adjust the bot's behavior
  };

  // New handlers for the buttons
  const handleCreateReport = () => {
    const newMessage: Message = {
      id: uuid4(),
      content: "Let's create a report for this month.",
      editable: false,
      sender: 'user',
    };
    setMessages([...messages, newMessage]);
    wsRef.current?.send("Let's create a report for this month.");
  };

  const handleCallLead = () => {
    const newMessage: Message = {
      id: uuid4(),
      content: "Let's schedule a call with the lead.",
      editable: false,
      sender: 'user',
    };
    setMessages([...messages, newMessage]);
    wsRef.current?.send("Let's schedule a call with the lead.");
  };

  return (
    <div className="max-w-md mx-auto my-8 p-4 bg-white rounded-lg shadow-md">
      {!token ? (
        <div>
          <h2 className="text-lg font-semibold mb-4 text-gray-900">Enter your name to start chatting</h2>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your name"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4 text-gray-900 placeholder-gray-500"
          />
          <button
            onClick={handleNameSubmit}
            className="w-full px-4 py-2 bg-purple-500 text-white rounded-lg"
          >
            Start Chat
          </button>
        </div>
      ) : (
        <>
          <div className="text-center mb-4">
            <img
              src="https://i.ibb.co/mD94qxS/ava.png" // Replace with the actual avatar image source
              alt="Avatar"
              className="w-12 h-12 rounded-full mx-auto"
            />
            <h2 className="text-lg font-semibold mt-2 text-gray-900">Hey👋, I’m Ava</h2>
            <p className="text-gray-600">Ask me anything or pick a place to start</p>
          </div>

          <div className="mb-4">
            {messages.map((msg, index) => (
              <div
                key={`${msg.id}-${index}`}
                className={`flex items-start mb-2 ${msg.sender === 'user' ? 'justify-end' : ''}`}
              >
                <div className="relative max-w-xs">
                  {msg.sender === 'bot' && (
                    <img
                      src="https://i.ibb.co/mD94qxS/ava.png" // Replace with the actual avatar image source
                      alt="Avatar"
                      className="w-8 h-8 rounded-full mr-3"
                    />
                  )}
                  <div
                    className={`p-3 rounded-lg ${
                      msg.sender === 'user' ? 'bg-purple-500 text-white' : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    <p className="mb-2">{msg.content}</p>
                    {msg.sender === 'user' && (
                      <div className="flex space-x-2 mt-1">
                        <button
                          onClick={() => handleEditMessage(msg.id)}
                          className="px-2 py-1 bg-white text-purple-500 rounded-full text-xs font-medium hover:bg-gray-200"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteMessage(msg.id)}
                          className="px-2 py-1 bg-white text-purple-500 rounded-full text-xs font-medium hover:bg-gray-200"
                        >
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="flex flex-col space-y-2 mb-4">
            <button
              onClick={handleCreateReport}
              className="px-4 py-2 bg-white text-purple-500 border border-purple-500 rounded-full text-sm font-medium hover:bg-gray-100"
            >
              Create Report this month
            </button>
            <button
              onClick={handleCallLead}
              className="px-4 py-2 bg-white text-purple-500 border border-purple-500 rounded-full text-sm font-medium hover:bg-gray-100"
            >
              Call Lead
            </button>
          </div>

          <div className="mt-4">
            <input
              type="text"
              placeholder="Your question"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900"
            />
            <button
              onClick={handleSendMessage}
              className="mt-2 w-full px-4 py-2 bg-purple-500 text-white rounded-lg"
            >
              {editingId ? 'Save' : 'Send'}
            </button>
          </div>

          <div className="mt-4">
            <select
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-900"
              value={context}
              onChange={handleContextChange}
            >
              <option value="Onboarding">Onboarding</option>
              <option value="Support">Support</option>
              <option value="Feedback">Feedback</option>
            </select>
          </div>
        </>
      )}
    </div>
  );
};

export default Chat;
