from fastapi import WebSocket, status, Query
from typing import Optional
from ..redis.config import Redis

redis = Redis()

async def get_token(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    if token is None or token == "":
        token="c5831589-a8e1-442a-8e18-f8db5b01b35e"
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    redis_client = await redis.create_connection()
    isexists = await redis_client.exists(token)

    if isexists == 1:
        print("Started websocket")
        return token
    else:
        print("Closing websocket")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Session not authenticated or expired token")

