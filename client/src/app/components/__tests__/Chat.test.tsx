import '@testing-library/jest-dom/extend-expect';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Chat from '../Chat';
import { getToken, sendMessageViaWebSocket } from '../../services/ChatService';
import { v4 as uuid4 } from 'uuid';

jest.mock('../services/ChatService', () => ({
  getToken: jest.fn(),
  sendMessageViaWebSocket: jest.fn(),
}));

describe('Chat component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders initial form to enter name', () => {
    render(<Chat />);
    
    const inputElement = screen.getByPlaceholderText(/Your name/i);
    const buttonElement = screen.getByText(/Start Chat/i);
    
    expect(inputElement).toBeInTheDocument();
    expect(buttonElement).toBeInTheDocument();
  });

  test('calls getToken when name is submitted', async () => {
    (getToken as jest.Mock).mockResolvedValue('fake-token');
    
    render(<Chat />);
    
    fireEvent.change(screen.getByPlaceholderText(/Your name/i), { target: { value: 'John Doe' } });
    fireEvent.click(screen.getByText(/Start Chat/i));

    await waitFor(() => {
      expect(getToken).toHaveBeenCalledWith('John Doe');
    });
  });

  test('establishes WebSocket connection and receives a message', async () => {
    (getToken as jest.Mock).mockResolvedValue('fake-token');
    
    const fakeWebSocket = {
      send: jest.fn(),
      onmessage: null,
      onerror: jest.fn(),
      onclose: jest.fn(),
    };
    
    global.WebSocket = jest.fn(() => fakeWebSocket as any);
    
    render(<Chat />);
    
    fireEvent.change(screen.getByPlaceholderText(/Your name/i), { target: { value: 'John Doe' } });
    fireEvent.click(screen.getByText(/Start Chat/i));

    await waitFor(() => {
      expect(getToken).toHaveBeenCalledWith('John Doe');
    });

    // Simulate incoming WebSocket message
    const messageData = { id: uuid4(), msg: 'Hello, user!' };
    const event = { data: JSON.stringify(messageData) };

    // Trigger WebSocket message event
    if (fakeWebSocket.onmessage) {
      fakeWebSocket.onmessage(event);
    }

    const receivedMessage = await screen.findByText('Hello, user!');
    expect(receivedMessage).toBeInTheDocument();
  });

  test('sends a message and clears input field', async () => {
    (getToken as jest.Mock).mockResolvedValue('fake-token');
    
    render(<Chat />);
    
    fireEvent.change(screen.getByPlaceholderText(/Your name/i), { target: { value: 'John Doe' } });
    fireEvent.click(screen.getByText(/Start Chat/i));

    await waitFor(() => {
      expect(getToken).toHaveBeenCalledWith('John Doe');
    });

    fireEvent.change(screen.getByPlaceholderText(/Type a message/i), { target: { value: 'Hello, bot!' } });
    fireEvent.click(screen.getByText(/Send/i));

    expect(screen.queryByPlaceholderText(/Type a message/i)).toHaveValue('');
    expect(sendMessageViaWebSocket).toHaveBeenCalled();
    const userMessage = screen.getByText('Hello, bot!');
    expect(userMessage).toBeInTheDocument();
  });

  test('handles message editing', async () => {
    (getToken as jest.Mock).mockResolvedValue('fake-token');
    
    render(<Chat />);

    // Simulate name submit and WebSocket connection
    fireEvent.change(screen.getByPlaceholderText(/Your name/i), { target: { value: 'John Doe' } });
    fireEvent.click(screen.getByText(/Start Chat/i));

    await waitFor(() => {
      expect(getToken).toHaveBeenCalledWith('John Doe');
    });

    // Simulate sending a message
    fireEvent.change(screen.getByPlaceholderText(/Type a message/i), { target: { value: 'Hello, bot!' } });
    fireEvent.click(screen.getByText(/Send/i));

    const editButton = screen.getByText(/Edit/i);
    fireEvent.click(editButton);

    expect(screen.getByPlaceholderText(/Type a message/i)).toHaveValue('Hello, bot!');
  });

  test('deletes a message', async () => {
    (getToken as jest.Mock).mockResolvedValue('fake-token');
    
    render(<Chat />);

    // Simulate name submit and WebSocket connection
    fireEvent.change(screen.getByPlaceholderText(/Your name/i), { target: { value: 'John Doe' } });
    fireEvent.click(screen.getByText(/Start Chat/i));

    await waitFor(() => {
      expect(getToken).toHaveBeenCalledWith('John Doe');
    });

    // Simulate sending a message
    fireEvent.change(screen.getByPlaceholderText(/Type a message/i), { target: { value: 'Hello, bot!' } });
    fireEvent.click(screen.getByText(/Send/i));

    const deleteButton = screen.getByText(/Delete/i);
    fireEvent.click(deleteButton);

    expect(screen.queryByText('Hello, bot!')).not.toBeInTheDocument();
  });
});
