from typing import Optional

from pydantic import BaseModel, Field

# from fastapi import UploadFile


class RetrieveQuerySchema(BaseModel):
    query: str
    top_k: Optional[int] = Field(default=10)


class UploadCSVSchema(BaseModel):
    review_header: str
    product_id_header: str
    # file: UploadFile


class RetrieveResponseSchema(BaseModel):
    query: str
    top_k: int
    metadata: list[dict]
    distances: list[float]


class TotalEmbeddingSchema(BaseModel):
    total_embedding: int


class UploadResponseSchema(BaseModel):
    total_reviews: int
    file_size: int


class LLMQuerySchema(BaseModel):
    query: str
    top_k: Optional[int] = Field(default=10)


class LLMResponseSchema(BaseModel):
    query: str
    response: str
    sources: list[dict]
