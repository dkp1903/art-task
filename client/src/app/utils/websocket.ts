// utils/websocket.ts
export function generateToken() {
    return Math.random().toString(36).substr(2);
  }
  
  export function connectWebSocket(token: string) {
    const ws = new WebSocket(`wss://server-b3n6.onrender.com/chat?token=${token}`);
  
    ws.onopen = () => {
      console.log('Connected to WebSocket');
    };
  
    ws.onmessage = (event) => {
      console.log('Message from server: ', event.data);
    };
  
    ws.onerror = (error) => {
      console.error('WebSocket error: ', error);
    };
  
    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };
  
    return ws;
  }
  