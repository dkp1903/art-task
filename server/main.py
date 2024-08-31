from fastapi import FastAPI, Request
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from src.routes.chat import chat

load_dotenv()

api = FastAPI()
api.include_router(chat)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to restrict origins as needed
    allow_credentials=True,
    allow_methods=["*"],  # Update this to restrict methods as needed
    allow_headers=["*"],  # Update this to restrict headers as needed
)

@api.get("/test")
async def root():
    return {"msg": "API is Online"}


if __name__ == "__main__":
    if os.environ.get('APP_ENV') == "development":
        uvicorn.run("main:api", host="0.0.0.0", port=3500,
                    workers=4, reload=True)
    else:
      pass