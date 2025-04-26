from fastapi import APIRouter, UploadFile, File
from .schemas import CSVFileValidator
from db.vector_db import get_embedding
router = APIRouter()

# upload csv file to save it in vector database
@router.post("/upload/{required_header}")
async def upload_csv(file: UploadFile = File(...), required_header: str = None):
    # Validate the CSV file using our Pydantic validator
    _, data, file_size = await CSVFileValidator.validate_csv_file(
        file=file,
        required_header=required_header,
    )
    print('@@@@@@@@ data @@@@@@@@@')
    print(data)
    print('@@@@@@@@ file_size @@@@@@@@@')
    print(file_size)
    return {"status": "success"}
    

# get query(text), create vector embeding from it then do similiarity search and return the results
@router.get("/query")
def query():
    return {"status": "query endpoint"}

@router.get('/llm')
def llm():
    return {"status": "llm endpoint"}


