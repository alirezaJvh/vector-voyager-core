from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from openai import OpenAI

from src.db.vector_db import VectorDBClient
from src.utils.chat_reply import chat_reply
from src.utils.csv_uploader import save_csv_as_vector

from .schemas import (
    LLMQuerySchema,
    LLMResponseSchema,
    RetrieveQuerySchema,
    RetrieveResponseSchema,
    TotalEmbeddingSchema,
    UploadResponseSchema,
)

vector_db = VectorDBClient()
router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponseSchema,
)
async def upload_csv(
    file: UploadFile = File(...), review_header: str = Form(...), product_id_header: str = Form(...)
):
    if not review_header:
        raise HTTPException(status_code=400, detail="review_header is required")

    if not product_id_header:
        raise HTTPException(status_code=400, detail="product_id_header is required")

    try:
        total_processed, file_size = await save_csv_as_vector(
            file=file,
            review_header=review_header,
            product_id_header=product_id_header,
            vector_db=vector_db,
        )
    except:
        raise HTTPException(status_code=500, detail="internal server error")

    return UploadResponseSchema(total_reviews=total_processed, file_size=file_size)


@router.post("/retrieve-data", response_model=RetrieveResponseSchema)
async def retrieve(payload: RetrieveQuerySchema):
    try:
        distances, _, metadata = await vector_db.search(payload.query, payload.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching for query: {str(e)}")

    return RetrieveResponseSchema(
        query=payload.query,
        top_k=payload.top_k,
        metadata=metadata,
        distances=distances.flatten().tolist(),
    )


@router.get("/total-embedding", response_model=TotalEmbeddingSchema)
async def total_embedding():
    total = vector_db.total_embedding()
    return TotalEmbeddingSchema(total_embedding=total)


@router.post("/llm", response_model=LLMResponseSchema)
async def llm(payload: LLMQuerySchema):
    try:
        answer, metadata = await chat_reply(
            query=payload.query, top_k=payload.top_k, vector_db=vector_db
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling LLM: {str(e)}")

    return LLMResponseSchema(query=payload.query, response=answer, sources=metadata)
