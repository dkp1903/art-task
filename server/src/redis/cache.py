import redis
import json

class Cache:
    def __init__(self, redis_client):
        self.redis_client = redis_client

    async def get_chat_history(self, token: str):
        # Get the JSON data from Redis
        data = self.redis_client.get(str(token))

        # Deserialize the data from JSON format
        if data is not None:
            data = json.loads(data)
        return data