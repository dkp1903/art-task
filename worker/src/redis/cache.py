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
    
    async def update_message_in_cache(self, token: str, message_id: str, new_content: str):
    # Retrieve chat history
        data = await self.get_chat_history(token)
        if not data:
            return
        # Find and update the message with the given ID
        for message in data['messages']:
            if message['id'] == message_id:
                message['msg'] = new_content
        # Save updated history back to Redis
        await self.redis_client.set(token, json.dumps(data))
        print("Updated message in cache")
        return message_id

    async def delete_message_from_cache(self, token: str, message_id: str):
        # Retrieve chat history
        data = await self.get_chat_history(token)
        if not data:
            return
        # Filter out the message to be deleted
        data['messages'] = [msg for msg in data['messages'] if msg['id'] != message_id]
        # Save updated history back to Redis
        await self.redis_client.set(token, json.dumps(data))
        print("Deleted message from cache")
        return message_id