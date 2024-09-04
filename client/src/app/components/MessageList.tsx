import { Message } from '../interfaces/Message';

interface MessageListProps {
  messages: Message[];
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

const MessageList = ({ messages, onEdit, onDelete }: MessageListProps) => (
  <div className="mb-4">
    {messages.map((msg, index) => (
      <div
        key={`${msg.id}-${index}`}
        className={`flex items-start mb-2 ${msg.sender === 'user' ? 'justify-end' : ''}`}
      >
        <div className="relative max-w-xs">
          {msg.sender === 'bot' && (
            <img
              src="https://i.ibb.co/mD94qxS/ava.png"
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
                  onClick={() => onEdit(msg.id)}
                  className="px-2 py-1 bg-white text-purple-500 rounded-full text-xs font-medium hover:bg-gray-200"
                >
                  Edit
                </button>
                <button
                  onClick={() => onDelete(msg.id)}
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
);

export default MessageList;
