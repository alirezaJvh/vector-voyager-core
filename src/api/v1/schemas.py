from pydantic import BaseModel
from fastapi import UploadFile, File, HTTPException
import csv
from io import StringIO


class CSVFileValidator:
    """Helper class for validating CSV files"""
    
    @staticmethod
    async def validate_csv_file(file: UploadFile, required_header: str):
 
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")
    
        contents = await file.read()
        file_size = len(contents)
        
        # Validate CSV structure
        try:
            text_content = contents.decode('utf-8')
            csv_reader = csv.reader(StringIO(text_content))
            # Get the headers
            headers = next(csv_reader, None)  
            
            if not headers:
                # Reset file pointer
                await file.seek(0)
                raise HTTPException(status_code=400, detail="CSV file is empty or has no headers.")
            
            # Validate required header if specified
            if required_header not in headers:
                await file.seek(0)  # Reset file pointer
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required header: {required_header}"
                )
            
            # Reset file pointer for further processing
            await file.seek(0)
            return {
                "headers": headers,
                "content": '\n'.join(text_content.splitlines()[1:]),
                "file_size": file_size
            }
            
        except UnicodeDecodeError:
            await file.seek(0)  # Reset file pointer
            raise HTTPException(status_code=400, detail="File is not a valid UTF-8 encoded CSV file.")
        except csv.Error:
            await file.seek(0)  # Reset file pointer
            raise HTTPException(status_code=400, detail="Invalid CSV format.")


# class UploadFileSchema(BaseModel):
#     """Pydantic model for CSV file upload requests"""
#     required_header: str 
