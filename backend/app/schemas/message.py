
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    sender_type: str = Field(pattern="^(customer|agent)$")
    content: str = Field(min_length=1)


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_type: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
