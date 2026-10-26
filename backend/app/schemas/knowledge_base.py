
from pydantic import BaseModel, ConfigDict, Field


class KnowledgeBaseEntryCreate(BaseModel):
    brand_id: int = Field(gt=0)
    title: str = Field(min_length=2, max_length=200)
    category: str = Field(min_length=2, max_length=100)
    content: str = Field(min_length=10)


class KnowledgeBaseEntryResponse(BaseModel):
    id: int
    brand_id: int
    title: str
    category: str
    content: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)



class KnowledgeBaseEntryUpdate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    category: str = Field(min_length=2, max_length=100)
    content: str = Field(min_length=10)
