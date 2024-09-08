import os
import uuid
import json
import logging
from datetime import datetime
from fastapi import APIRouter, WebSocket, Request, HTTPException, Depends
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel
from ..socket.connection import ConnectionManager
from ..socket.utils import get_token
from ..redis.producer import Producer
from ..redis.config import Redis
from ..redis.stream import StreamConsumer
from ..redis.cache import Cache
from ..schema.chat import Chat

# Set up logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,
)

chat = APIRouter()
manager = ConnectionManager()
redis = Redis()

# @route   POST /token
# @desc    Route generating chat token
# @access  Public

@chat.post("/token")
async def token_generator(name: str, request: Request):
    logging.info("Token generation initiated")

    if not name:
        logging.warning("Invalid name provided")
        raise HTTPException(status_code=400, detail={
            "loc": "name", "msg": "Enter a valid name"
        })

    token = str(uuid.uuid4())

    chat_session = Chat(
        token=token,
        messages=[],
        name=name
    )

    logging.info(f"Generated chat session: {chat_session.dict()}")

    # Store chat session in Redis
    try:
        redis_client = await redis.create_connection()
        await redis_client.set(token, json.dumps(chat_session.dict()))
        await redis_client.expire(token, 3600)
        logging.info(f"Chat session stored in Redis with token {token}")
    except Exception as e:
        logging.error(f"Error storing chat session in Redis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create session")

    return chat_session.dict()


# @route   POST /refresh_token
# @desc    Route to refresh token
# @access  Public

@chat.get("/refresh_token")
async def refresh_token(request: Request, token: str):
    logging.info(f"Refreshing token: {token}")
    
    cache = Cache(redis)
    data = await cache.get_chat_history(token)

    if not data:
        logging.warning(f"Token {token} not found or session expired")
        raise HTTPException(status_code=400, detail="Session expired or does not exist")

    logging.info(f"Session data retrieved for token: {token}")
    return data


# @route   Websocket /chat
# @desc    Socket for chatbot
# @access  Public

@chat.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, token: str = Depends(get_token)):
    logging.info(f"WebSocket connection initialized for token: {token}")

    await manager.connect(websocket)
    redis_client = await redis.create_connection()
    producer = Producer(redis_client)
    consumer = StreamConsumer(redis_client)

    logging.info("WebSocket connection established, listening for messages")

    await consumer.reset_stream("response_channel")

    try:
        while True:
            data = await websocket.receive_text()
            logging.info(f"Received message: {data}")

            stream_data = {token: data}
            logging.info(f"Streaming data to Redis: {stream_data}")
            await producer.add_to_stream(stream_data, "message_channel")

            response = await consumer.consume_stream(stream_channel="response_channel", block=0)
            logging.info(f"Received response from stream: {response}")

            for stream, messages in response:
                for message in messages:
                    response_token = [k.decode('utf-8') for k, v in message[1].items()][0]

                    if token == response_token:
                        response_message = [v.decode('utf-8') for k, v in message[1].items()][0]
                        logging.info(f"Sending message to client: {response_message}")
                        await manager.send_personal_message(response_message, websocket)

                    logging.info(f"Deleting message with ID: {message[0].decode('utf-8')}")
                    await consumer.delete_message(stream_channel="response_channel", message_id=message[0].decode('utf-8'))

    except WebSocketDisconnect:
        logging.info("WebSocket disconnected")
        manager.disconnect(websocket)

    except Exception as e:
        logging.error(f"Error during WebSocket handling: {e}", exc_info=True)
