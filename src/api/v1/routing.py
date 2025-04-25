from fastapi import APIRouter, UploadFile, File
from .schemas import CSVFileValidator
router = APIRouter()

# upload csv file to save it in vector database
@router.post("/upload/{required_header}")
async def upload_csv(file: UploadFile = File(...), required_header: str = None):
    # Validate the CSV file using our Pydantic validator
    validation_result = await CSVFileValidator.validate_csv_file(
        file=file,
        required_header=required_header,
    )
    print('@@@@@@@@ validation_result @@@@@@@@@')
    print(validation_result)
    return {"status": "success"}
    # return {
    #     "status": "success",
    #     "file": file.filename,
    #     "headers": headers,
    #     "size": validation_result["file_size"]
    # }

# get query(text), create vector embeding from it then do similiarity search and return the results
@router.get("/query")
def query():
    return {"status": "query endpoint"}

@router.get('llm')
def llm():
    return {"status": "llm endpoint"}


