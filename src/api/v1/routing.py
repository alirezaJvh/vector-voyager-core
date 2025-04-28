from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from openai import OpenAI
from db.vector_db import VectorDBClient
from utils.csv_uploader import save_csv_as_vector
from .schemas import (
    RetrieveQuerySchema, 
    RetrieveResponseSchema, 
    UploadResponseSchema,
    TotalEmbeddingSchema,
    LLMQuerySchema,
    LLMResponseSchema
)

vector_db = VectorDBClient()
router = APIRouter()

# TODO: make better name for reviw_header and prodocut_id_header
# upload csv file to save it in vector database
@router.post("/upload", response_model=UploadResponseSchema, )
async def upload_csv(file: UploadFile = File(...), review_header: str = Form(...), product_id_header: str = Form(...)):

    if not review_header:
        raise HTTPException(status_code=400, detail="review_header is required")

    if not product_id_header:
        raise HTTPException(status_code=400, detail="product_id_header is required")

    try:
        total_processed, file_size = await save_csv_as_vector(
            file=file,
            review_header=review_header,
            product_id_header=product_id_header,
            vector_db=vector_db
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
        distances=distances.flatten().tolist()
    )


@router.get("/total-embedding", response_model=TotalEmbeddingSchema)
async def total_embedding():
    total =  vector_db.total_embedding()
    return TotalEmbeddingSchema(total_embedding=total)


# TODO:  
@router.post('/llm', response_model=LLMResponseSchema)
async def llm(payload: LLMQuerySchema):
    query_payload = RetrieveQuerySchema(query=payload.query, top_k=payload.top_k)
    # TODO: use service and do not use retrieve api
    result = await retrieve(query_payload)
    print(result.metadata)
    print(result.distances)

    context = ""
    for idx, doc in enumerate(result.metadata):
        print(doc)
        if doc :
            doc_content = "\t ".join([f"{key}: {value}" for key, value in doc.items()])
            context += f"Document {idx+1}:\n{doc_content}\n\n"

    # TODO: use better prompt
    prompt = f"""
    Answer the following question based on the provided context.
    
    Context:
    {context}
    
    Question: {payload.query}
    
    Answer:
    """
    # TODO: move it to prodiver
    openai_client = OpenAI()
    try:
        # TODO: use enum
        # TODO: history
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        print(response.choices)
        answer = response.choices[0].message.content

        return LLMResponseSchema(
            query=payload.query,
            response=answer,
            sources=result.metadata
        )

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error calling LLM: {str(e)}")


