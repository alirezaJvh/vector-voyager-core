from fastapi import APIRouter, UploadFile, File
from common.validation import CSVFileValidator
from db.vector_db import VectorDBClient
from .schemas import QuerySchema

vector_db = VectorDBClient()
router = APIRouter()

# upload csv file to save it in vector database
@router.post("/upload")
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

    reviews = []
    product_ids = []
    for row in data:
        review = row.get(review_header, "").strip()
        product_id = row.get(product_id_header, "").strip()
        if review and product_id:
            reviews.append(review)
            product_ids.append(product_id)

    batch_size = 200
    total_processed = 0

    for idx in range(0, len(reviews), batch_size):
        batch_reviews = reviews[idx:idx + batch_size]
        batch_product_ids = product_ids[idx:idx + batch_size]

        # add embedding to vector database
        indices = await vector_db.add_embedding_batch(batch_reviews, batch_product_ids)
        total_processed += len(indices)

    return {
        "status": "success", 
        "message": f"{total_processed} reviews processed", 
        "total_reviews": total_processed, 
        "file_size": file_size
    }
    


@router.post("/query")
async def query(payload: QuerySchema):

    query, top_k = payload.query, payload.top_k
    if not query:
        raise HTTPException(status_code=400, detail="Query text is required")

    distances, indices = await vector_db.search(query, top_k)

    return {"status": "query endpoint", "text": query, "top_k": top_k, "distances": distances,}

@router.get('/llm')
def llm():
    return {"status": "llm endpoint"}


