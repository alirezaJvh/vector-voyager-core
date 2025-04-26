from pydantic import BaseModel
from fastapi import UploadFile, File, HTTPException


# class UploadFileSchema(BaseModel):
#     """Pydantic model for CSV file upload requests"""
#     required_header: str 

class QuerySchema(BaseModel):
    query: str
    top_k: int = 2
