import os
from dotenv import load_dotenv
import redis.asyncio as redis
import json

load_dotenv()

class Redis:
    def __init__(self):
        """Initialize connection settings"""
        self.REDIS_URL = os.environ['REDIS_URL']
        self.REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
        self.REDIS_USER = os.environ['REDIS_USER']
        self.connection_url = f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_URL}"
        self.REDIS_HOST = os.environ['REDIS_HOST']
        self.REDIS_PORT = os.environ['REDIS_PORT']

    async def create_connection(self):
        print("Url : ", self.connection_url)
        self.connection = redis.from_url(
            self.connection_url)
        print(self.connection)
        return self.connection

    async def set_json_data(self, key: str, value: dict):
        """Set a JSON-encoded value in Redis"""
        json_data = json.dumps(value)  # Serialize dictionary to JSON string
        await self.connection.set(key, json_data)

    async def get_json_data(self, key: str):
        """Get a JSON-encoded value from Redis"""
        raw_data = await self.connection.get(key)
        if raw_data:
            return json.loads(raw_data)  # Deserialize JSON string to dictionary
        return None