
from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    brand_id: int = Field(gt=0)
    customer_name: str = Field(min_length=2, max_length=150)
    customer_email: str | None = None
    order_number: str | None = None
    order_status: str = Field(min_length=2, max_length=50)
    order_details: str = Field(min_length=2)


class ConversationResponse(BaseModel):
    id: int
    brand_id: int
    customer_name: str
    customer_email: str | None
    order_number: str | None
    order_status: str
    order_details: str
    status: str

    model_config = ConfigDict(from_attributes=True)
