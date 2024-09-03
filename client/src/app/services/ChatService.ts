import axios from 'axios';

export const getToken = async (name: string): Promise<string> => {
  const serverUrl = 'https://3500-dkp1903-arttask-imbornlwndw.ws-us116.gitpod.io/token';// process.env.SERVER_URL || 'https://server-b3n6.onrender.com/token';
  const response = await axios.post(serverUrl, null, { params: { name } });
  return response.data.token;
};

export const sendMessageViaWebSocket = (ws: WebSocket | null, message: string) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(message);
  } else {
    console.error('WebSocket is not connected');
  }
};
