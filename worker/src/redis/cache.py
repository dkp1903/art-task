import json
from redis.asyncio.client import Redis

class Cache:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def get_chat_history(self, token: str):
        # Retrieve the raw JSON string from Redis
        raw_data = await self.redis_client.get(str(token))
        
        # Deserialize the JSON string into a Python dictionary
        if raw_data:
            return json.loads(raw_data)  # Deserialize JSON string to dictionary
        return None
    
    async def add_message_to_cache(self, token: str, source: str, message_data: dict):
        # Retrieve the current chat history
        chat_history = await self.get_chat_history(token)
        
        if chat_history is None:
            chat_history = {'messages': []}
        
        if source == "human":
            message_data['msg'] = "Human: " + message_data['msg']
        elif source == "bot":
            message_data['msg'] = "Bot: " + message_data['msg']
        
        # Append the new message to the chat history
        chat_history['messages'].append(message_data)
        
        # Store the updated chat history back in Redis
        await self.redis_client.set(str(token), json.dumps(chat_history))