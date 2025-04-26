from fastapi import APIRouter, UploadFile, File
from common.validation import CSVFileValidator
from db.vector_db import VectorDBClient

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
    
    print('@@@@@ data @@@@')
    print(data)

    # Extract column data
    # data = [row[review_header] for row in data_dict 
    #         if review_header in row and row[review_header]]

    # print('@@@@@@@@ data @@@@@@@@@')
    # print(len(csv_reader))
    # print('@@@@@@@@ file_size @@@@@@@@@')
    # print(file_size)

    # print(text)
    return {"status": "success"}
    

# get query(text), create vector embeding from it then do similiarity search and return the results
@router.get("/query")
def query():
    return {"status": "query endpoint"}

@router.get('/llm')
def llm():
    return {"status": "llm endpoint"}


