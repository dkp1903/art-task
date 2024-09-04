export interface Message {
    id: string;
    content: string;
    editable: boolean;
    sender: 'user' | 'bot';
  }
  