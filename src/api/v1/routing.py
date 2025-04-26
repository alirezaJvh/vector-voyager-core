from fastapi import APIRouter, UploadFile, File
from common.validation import CSVFileValidator
from db.vector_db import VectorDBClient

vector_db = VectorDBClient()
router = APIRouter()

# upload csv file to save it in vector database
@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), required_header: str = None):
    # Validate the CSV file using our Pydantic validator
    data, file_size = await CSVFileValidator.validate_csv_file(
        file=file,
        required_header=required_header,
    )
    print('@@@@@@@@ data @@@@@@@@@')
    print(len(data))
    print('@@@@@@@@ file_size @@@@@@@@@')
    print(file_size)
    # print('@@@@@@@@ text @@@@@@@@@')
    # text = next(data)

    # print(text)
    return {"status": "success"}
    

# get query(text), create vector embeding from it then do similiarity search and return the results
@router.get("/query")
def query():
    return {"status": "query endpoint"}

@router.get('/llm')
def llm():
    return {"status": "llm endpoint"}


