from pydantic import BaseModel, Field
from typing import Optional


class QuerySchema(BaseModel):
    query: str
    top_k: Optional[int] = Field(default=10)

class QueryResponseSchema(BaseModel):
    query: str
    top_k: int
    metadata: list[dict]
    distances: list[float]

class TotalEmbeddingSchema(BaseModel):
    total_embedding: int

class UploadResponseSchema(BaseModel):
    total_reviews: int
    file_size: int
    
    
