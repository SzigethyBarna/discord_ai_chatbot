from pydantic import BaseModel
from typing import Optional

class BotCreate(BaseModel):
    name: str
    platform: str
    system_prompt: str

class BotResponse(BaseModel):
    id: int
    name: str
    platform: str
    system_prompt: str
    is_active: bool

    class Config:
        from_attributes = True  