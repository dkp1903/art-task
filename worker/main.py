from fastapi import FastAPI
import asyncio
import threading
from src.redis.config import Redis
from src.model.hf import GPT
from src.redis.cache import Cache
from src.redis.stream import StreamConsumer
from src.redis.producer import Producer
import re
from routes import router
from src.schema.chat import Message

app = FastAPI()

# Include the router
app.include_router(router)

# Define the main worker function
async def worker_main():
    redis = Redis()
    redis = await redis.create_connection()
    consumer = StreamConsumer(redis)
    cache = Cache(redis)
    producer = Producer(redis)

    print("Stream consumer started")
    print("Stream waiting for new messages")
    while True:
        response = await consumer.consume_stream(stream_channel="message_channel", count=1, block=0)

        if response:
            for stream, messages in response:
                for message in messages:
                    print("First, the message : ", message)
                    message_id = message[0]
                    token = [k.decode('utf-8') for k, v in message[1].items()][0]
                    message = [v.decode('utf-8') for k, v in message[1].items()][0]
                    print(token)

                    msg = Message(msg=message)
                    await cache.add_message_to_cache(token=token, source="human", message_data=msg.dict())

                    data = await cache.get_chat_history(token=token)
                    message_data = data['messages'][-4:]
                    input = ["" + i['msg'] for i in message_data]
                    input = " ".join(input)
                    print("Message : ", message)
                    input = message

                    print("Input : ", input)

                    res = GPT().query(input=input)
                    res = re.sub(r'[^\w\s]', '', res)
                    msg = Message(msg=res)

                    print("ChatGPT response : ", msg)

                    stream_data = {}
                    stream_data[str(token)] = str(msg.dict())

                    await producer.add_to_stream(stream_data, "response_channel")
                    await cache.add_message_to_cache(token=token, source="bot", message_data=msg.dict())

                await consumer.delete_message(stream_channel="message_channel", message_id=message_id)

# Define the function to run FastAPI
def run_fastapi():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # Start the FastAPI server in a separate thread
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.start()

    # Run the worker logic in the main thread
    asyncio.run(worker_main())
