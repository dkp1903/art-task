import os
from fastapi import APIRouter, FastAPI, WebSocket, Request, BackgroundTasks, HTTPException, Depends
import uuid
from ..socket.connection import ConnectionManager
from ..socket.utils import get_token
from ..redis.producer import Producer
from ..redis.config import Redis
from ..schema.chat import Chat
import json

chat = APIRouter()
manager = ConnectionManager()
redis = Redis()

# @route   POST /token
# @desc    Route generating chat token
# @access  Public

@chat.post("/token")
async def token_generator(name: str, request: Request):

    if name == "":
        raise HTTPException(status_code=400, detail={
            "loc": "name",  "msg": "Enter a valid name"})

    token = str(uuid.uuid4())

    chat_session = Chat(
        token=token,
        messages=[],
        name=name
    )
    print("Routes/Chat : ", chat_session.dict())

    # Store chat session in Redis JSON with the token as key
    redis_client = await redis.create_connection()
    await redis_client.set(str(token), json.dumps(chat_session.dict()))  # Serialize dict to JSON string

    # Set a timeout for Redis data
    await redis_client.expire(str(token), 3600)

    return chat_session.dict()


# @route   POST /refresh_token
# @desc    Route to refresh token
# @access  Public

@chat.post("/refresh_token")
async def refresh_token(request: Request):
    return None


# @route   Websocket /chat
# @desc    Socket for chatbot
# @access  Public

@chat.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, token: str = Depends(get_token)):
    await manager.connect(websocket)
    redis_client = await redis.create_connection()
    producer = Producer(redis_client)

    try:
        while True:
            data = await websocket.receive_text()
            print("Websocket response : ", data)
            stream_data = {}
            stream_data[token] = data
            await producer.add_to_stream(stream_data, "message_channel")
            await manager.send_personal_message(f"Response: Simulating response from the GPT service", websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
