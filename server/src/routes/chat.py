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

@chat.get("/refresh_token")
async def refresh_token(request: Request, token: str):
    json_client = redis.create_rejson_connection()
    cache = Cache(json_client)
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
    await manager.connect(websocket)
    redis_client = await redis.create_connection()
    producer = Producer(redis_client)
    consumer = StreamConsumer(redis_client)

    try:
        while True:
            data = await websocket.receive_text()
            print("Websocket response : ", data)
            stream_data = {}
            stream_data[token] = data
            await producer.add_to_stream(stream_data, "message_channel")
            response = await consumer.consume_stream(stream_channel="response_channel", block=0)

            print("Response : ", response)

            for stream, messages in response:
                for message in messages:
                    response_token = [k.decode('utf-8')
                                      for k, v in message[1].items()][0]

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
