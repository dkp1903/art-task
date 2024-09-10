import asyncio
import threading
import re
import logging
from fastapi import FastAPI
from src.redis.config import Redis
from src.model.hf import GPT
from src.redis.cache import Cache
from src.redis.stream import StreamConsumer
from src.redis.producer import Producer
from routes import router
from src.schema.chat import Message

# Set up logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,
)

app = FastAPI()

# Include the router
app.include_router(router)

async def worker_main():
    redis = Redis()
    redis = await redis.create_connection()
    consumer = StreamConsumer(redis)
    cache = Cache(redis)
    producer = Producer(redis)

    logging.info("Stream consumer started")
    logging.info("Stream waiting for new messages")

    while True:
        try:
            response = await consumer.consume_stream(stream_channel="message_channel", count=1, block=0)

            if response:
                for stream, messages in response:
                    for message in messages:
                        logging.info(f"Received message from stream: {message}")
                        message_id = message[0]
                        token = [k.decode('utf-8') for k, v in message[1].items()][0]
                        message_text = [v.decode('utf-8') for k, v in message[1].items()][0]

                        logging.info(f"Processing message with token: {token}")

                        # Create and cache the human message
                        msg = Message(msg=message_text)
                        await cache.add_message_to_cache(token=token, source="human", message_data=msg.dict())

                        # Fetch and prepare the conversation history
                        data = await cache.get_chat_history(token=token)
                        message_data = data['messages'][-4:]
                        input_text = " ".join([i['msg'] for i in message_data])
                        input_text = message_text  # Using current message

                        logging.info(f"Sending input to GPT: {input_text}")

                        if input_text == 'Message Deleted':
                            res = input_text
                        else:
                            # Query GPT model
                            res = GPT().query(input=input_text)
                        res = re.sub(r'[^\w\s]', '', res)
                        msg = Message(msg=res)

                        logging.info(f"Received GPT response: {msg}")

                        # Prepare response and add to stream
                        stream_data = {str(token): str(msg.dict())}
                        logging.info(f"Stream Data: {stream_data} for token {token}")
                        await producer.add_to_stream(stream_data, "response_channel")

                        # Cache the bot response
                        await cache.add_message_to_cache(token=token, source="bot", message_data=msg.dict())

                        # Delete processed message
                        await consumer.delete_message(stream_channel="message_channel", message_id=message_id)

        except Exception as e:
            logging.error(f"Error processing stream message: {e}", exc_info=True)

def run_fastapi():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # Start the FastAPI server in a separate thread
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.start()

    # Run the worker logic in the main thread
    asyncio.run(worker_main())
