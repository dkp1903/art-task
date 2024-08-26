from src.redis.config import Redis
import asyncio
from src.model.hf import GPT
from src.redis.cache import Cache
from src.schema.chat import Message

async def main():
    redis = Redis()
    redis = await redis.create_connection()
    await Cache(redis).add_message_to_cache(token="11ff0913-3325-4352-b74a-423f5aef78f8", source="human", message_data={
        "id": "1",
        "msg": "Do you know what is caching",
        "timestamp": "2022-07-16 13:20:01.092109"
    })
    data = await Cache(redis).get_chat_history(token="11ff0913-3325-4352-b74a-423f5aef78f8")
    print("Cache Data : ", data)
    message_data = data['messages'][-4:]

    input = ["" + i['msg'] for i in message_data]
    input = " ".join(input)

    res = GPT().query(input=input)

    msg = Message(
        msg=res
    )

    print("Bot response : ", msg)
    await Cache(redis).add_message_to_cache(token="11ff0913-3325-4352-b74a-423f5aef78f8", source="bot", message_data=msg.dict())

if __name__ == "__main__":
    asyncio.run(main())