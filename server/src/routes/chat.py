import os
from fastapi import APIRouter, FastAPI, WebSocket, Request, BackgroundTasks, HTTPException, Depends
import uuid
from ..socket.connection import ConnectionManager
from ..socket.utils import get_token
from ..redis.producer import Producer
from ..redis.config import Redis
from ..redis.stream import StreamConsumer
from ..schema.chat import Chat
import json
from ..redis.cache import Cache
import uuid
from datetime import datetime
from pydantic import BaseModel

chat = APIRouter()
manager = ConnectionManager()
redis = Redis()

# @route   POST /token
# @desc    Route generating chat token
# @access  Public

@chat.post("/token")
async def token_generator(name: str, request: Request):

    print("Create token Init")

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

    print("Chat sesh created")
    # Set a timeout for Redis data
    await redis_client.expire(str(token), 3600)

    return chat_session.dict()


# @route   POST /refresh_token
# @desc    Route to refresh token
# @access  Public

@chat.get("/refresh_token")
async def refresh_token(request: Request, token: str):
    cache = Cache(redis)
    data = await cache.get_chat_history(token)

    if data == None:
        raise HTTPException(
            status_code=400, detail="Session expired or does not exist")
    else:
        return data


# @route   Websocket /chat
# @desc    Socket for chatbot
# @access  Public

@chat.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, token: str = Depends(get_token)):
    print("Init connection")
    await manager.connect(websocket)
    redis_client = await redis.create_connection()
    print("Connection created")

    producer = Producer(redis_client)

    consumer = StreamConsumer(redis_client)
    await consumer.reset_stream("response_channel")

    try:
        while True:
            data = await websocket.receive_text()
            print("Received Message : ", data)

            stream_data = {}
            print("Received Token : ", token)
            stream_data[token] = data
            await producer.add_to_stream(stream_data, "message_channel")
            response = await consumer.consume_stream(stream_channel="response_channel", block=0)

            print("Response : ", response)

            print("Printing all")
    
            await consumer.print_all_messages("response_channel")

            for stream, messages in response:
                for message in messages:
                    response_token = [k.decode('utf-8')
                                      for k, v in message[1].items()][0]
                    print("Token : ", token)
                    print ("Response Token : ", response_token)
                    if token == response_token:
                        response_message = [v.decode('utf-8')
                                            for k, v in message[1].items()][0]

                        print(message[0].decode('utf-8'))
                        print(token)
                        print(response_token)

                        await manager.send_personal_message(response_message, websocket)

                    await consumer.delete_message(stream_channel="response_channel", message_id=message[0].decode('utf-8'))

            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
