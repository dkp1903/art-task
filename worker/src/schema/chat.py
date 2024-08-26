from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
import uuid


class Message(BaseModel):
    id: str = str(uuid.uuid4())
    msg: str
    timestamp: str = str(datetime.now())