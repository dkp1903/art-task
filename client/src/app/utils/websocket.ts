// utils/websocket.ts
export function generateToken() {
    return Math.random().toString(36).substr(2); // Simple token generation
  }
  
  export function connectWebSocket(token: string) {
    const ws = new WebSocket(`wss://3500-dkp1903-arttask-a8mfnahxlkg.ws-us115.gitpod.io?token=${token}`);
  
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
  