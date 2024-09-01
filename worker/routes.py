from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class TestResponse(BaseModel):
    message: str

@router.get("/test", response_model=TestResponse)
async def test_endpoint():
    return {"message": "This is a test endpoint"}
