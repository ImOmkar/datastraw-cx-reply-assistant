
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReplyDraftCreate(BaseModel):
    conversation_id: int = Field(gt=0)
    retrieved_context: str = Field(min_length=1)
    ai_response: str = Field(min_length=1)


class ReplyDraftUpdate(BaseModel):
    edited_response: str = Field(min_length=1)


class ReplyDraftResponse(BaseModel):
    id: int
    conversation_id: int
    retrieved_context: str
    ai_response: str
    edited_response: str | None
    final_response: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    approved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
