import redis
import json

class Cache:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    async def get_chat_history(self, token: str):
        # Get the JSON data from Redis
        data = await self.redis_client.get(str(token))

        # Deserialize the data from JSON format
        if data is not None:
            print("Cache data : ", data)
            data = json.loads(data)
        return data
    
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