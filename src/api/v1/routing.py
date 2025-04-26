from fastapi import APIRouter, UploadFile, File, HTTPException
from common.validation import CSVFileValidator
from db.vector_db import VectorDBClient
from .schemas import (
    QuerySchema, 
    QueryResponseSchema, 
    UploadResponseSchema,
    TotalEmbeddingSchema
)

vector_db = VectorDBClient()
router = APIRouter()

# upload csv file to save it in vector database
@router.post("/upload", response_model=UploadResponseSchema)
async def upload_csv(file: UploadFile = File(...), review_header: str = None, product_id_header: str = None):
    if not review_header:
        raise HTTPException(status_code=400, detail="review_header is required")
    
    if not product_id_header:
        raise HTTPException(status_code=400, detail="product_id_header is required")
    # Validate the CSV file
    data, file_size = await CSVFileValidator.validate_csv_file(
        file=file,
        required_header=[review_header, product_id_header]
    )

    # remove all existing embeddings
    await vector_db.remove_all()

    reviews = []
    product_ids = []
    for row in data:
        review = row.get(review_header, "").strip()
        product_id = row.get(product_id_header, "").strip()
        if review and product_id:
            reviews.append(review)
            product_ids.append(product_id)

    batch_size = 300
    total_processed = 0

    for idx in range(0, len(reviews), batch_size):
        batch_reviews = reviews[idx:idx + batch_size]
        batch_product_ids = product_ids[idx:idx + batch_size]

        # add embedding to vector database
        indices = await vector_db.add_embedding_batch(batch_reviews, batch_product_ids)
        total_processed += len(indices)

    return UploadResponseSchema(
        total_reviews=total_processed,
        file_size=file_size
    )


@router.post("/query", response_model=QueryResponseSchema)
async def query(payload: QuerySchema):

    query, top_k = payload.query, payload.top_k
    if not query:
        raise HTTPException(status_code=400, detail="Query text is required")

    distances, _, metadata = await vector_db.search(query, top_k)
    print(metadata)

    return QueryResponseSchema(
        query=query,
        top_k=top_k,
        metadata=metadata,
        distances=distances.tolist()
    )


@router.get("/total_embedding", response_model=TotalEmbeddingSchema)
async def total_embedding():
    total =  vector_db.total_embedding()
    return TotalEmbeddingSchema(total_embedding=total)


@router.get('/llm')
def llm():
    return {"status": "llm endpoint"}


