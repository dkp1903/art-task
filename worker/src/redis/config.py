import os
from dotenv import load_dotenv
import redis.asyncio as redis

load_dotenv()

class Redis:
    def __init__(self):
        self.REDIS_URL = os.environ['REDIS_URL']
        self.REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
        self.REDIS_USER = os.environ['REDIS_USER']
        self.REDIS_HOST = os.environ['REDIS_HOST']
        self.REDIS_PORT = os.environ['REDIS_PORT']
        self.connection_url = f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_URL}"

    async def create_connection(self):
        self.connection = redis.from_url(
            self.connection_url, db=0, username=self.REDIS_USER, password=self.REDIS_PASSWORD
        )
        return self.connection

