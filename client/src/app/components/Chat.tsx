import { useEffect, useRef, useState } from 'react';
import { Message } from '../interfaces/Message';
import { getToken, sendMessageViaWebSocket } from '../services/ChatService';
import { v4 as uuid4 } from 'uuid';
import MessageList from './MessageList';
import InputField from './InputField';
import ContextSelector from './ContextSelector';
import Avatar from './Avatar';
import ActionButtons from './ActionButtons';

const Chat = () => {
  const [name, setName] = useState('');
  const [token, setToken] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [context, setContext] = useState('Onboarding');

  const handleNameSubmit = async () => {
    try {
      const receivedToken = await getToken(name);
      setToken(receivedToken);

      // Establish WebSocket connection
      const chatUrl = process.env.CHAT_URL || 'wss://server-b3n6.onrender.com/chat?token=';
      wsRef.current = new WebSocket(`${chatUrl}${receivedToken}`);
      wsRef.current.onmessage = (event) => handleWebSocketMessage(event.data);
      wsRef.current.onerror = (error) => console.error('WebSocket error:', error);
      wsRef.current.onclose = () => console.log('WebSocket connection closed');
    } catch (error) {
      console.error('Error fetching token:', error);
    }
  };

  const handleWebSocketMessage = (data: string) => {
    try {
      const parsedData = JSON.parse(data.replace(/(^'|'$)/g, '').replace(/'/g, '"'));
      const newMessage: Message = {
        id: parsedData.id || uuid4(),
        content: parsedData.msg,
        editable: false,
        sender: 'bot',
      };
      setMessages((prevMessages) => [...prevMessages, newMessage]);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };

  const handleSendMessage = () => {
    if (input.trim() === '') return;
    if (editingId !== null) {
      submitEditMessage();
    } else {
      const newMessage: Message = {
        id: uuid4(),
        content: input,
        editable: false,
        sender: 'user',
      };
      console.log("NMI : ", newMessage.id);
      setMessages([...messages, newMessage]);
      sendMessageViaWebSocket(wsRef.current, JSON.stringify({ action: 'send', content: input }));
      setInput('');
    }
  };

  const handleButtonAction = (actionMessage: string) => {
    console.log("Handle button action")
    const actionMessageObject = {
      action: "send",
      content: actionMessage
    };
    const userMessage: Message = {
      id: uuid4(),
      content: actionMessage,
      editable: false,
      sender: 'user',
    };
    console.log("Action Message Object: ", JSON.stringify(actionMessageObject));
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    sendMessageViaWebSocket(wsRef.current, JSON.stringify(actionMessageObject));
  };

  const handleEditMessage = (id: string) => {
    const message = messages.find((msg) => msg.id === id);
    if (message) {
      setInput(message.content);
      setEditingId(id);
    }
  };

  const submitEditMessage = () => {
    if (editingId !== null) {
      const editedMessage = messages.find(msg => msg.id === editingId);
      if (editedMessage) {
        const messageData = {
          action: 'edit',
          id: editingId,
          content: input
        };
        sendMessageViaWebSocket(wsRef.current, JSON.stringify(messageData));
  
        setMessages((prevMessages) =>
          prevMessages.map((msg) =>
            msg.id === editingId ? { ...msg, content: input, editable: false } : msg
          )
        );
        setEditingId(null);
        setInput('');
      }
    }
  };

  const handleDeleteMessage = (id: string) => {
    const messageData = {
      action: 'delete',
      id: id
    };
    sendMessageViaWebSocket(wsRef.current, JSON.stringify(messageData));
  
    // Remove the message locally
    setMessages((prevMessages) => prevMessages.filter((msg) => msg.id !== id));
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
          <Avatar />
          <MessageList
            messages={messages}
            onEdit={handleEditMessage}
            onDelete={handleDeleteMessage}
          />
          <ActionButtons
            onCreateReport={() => handleButtonAction("Let's create a report for this month.")}
            onCallLead={() => handleButtonAction("Let's schedule a call with the lead.")}
          />
          <InputField
            input={input}
            setInput={setInput}
            onSend={handleSendMessage}
            editingId={editingId}
          />
          <ContextSelector context={context} setContext={setContext} />
        </>
      )}
    </div>
  );
};

export default Chat;
