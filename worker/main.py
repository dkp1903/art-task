from src.redis.config import Redis
import asyncio
from src.model.hf import GPT
from src.redis.cache import Cache

async def main():
    redis = Redis()
    redis = await redis.create_connection()
    await Cache(redis).add_message_to_cache(token="11ff0913-3325-4352-b74a-423f5aef78f8", source="human", message_data={
        "id": "1",
        "msg": "Hello",
        "timestamp": "2022-07-16 13:20:01.092109"
    })
    data = await Cache(redis).get_chat_history(token="11ff0913-3325-4352-b74a-423f5aef78f8")
    data = await Cache(redis).get_chat_history(token="11ff0913-3325-4352-b74a-423f5aef78f8")
    print(data)

if __name__ == "__main__":
    asyncio.run(main())