import csv
from io import StringIO
from fastapi import UploadFile, HTTPException

class CSVFileValidator:
    """Helper class for validating CSV files"""
    @staticmethod
    async def validate_csv_file(file: UploadFile, required_header: list[str] = []):
 
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")
    
        contents = await file.read()
        file_size = len(contents)
        
        try:
            text_content = contents.decode('utf-8')
            csv_file = StringIO(text_content)
            csv_to_dict = csv.DictReader(csv_file)
            data = list(csv_to_dict)
            await file.seek(0)

            if not data:
                raise HTTPException(status_code=400, detail="CSV file is empty")

            if len(required_header):
                for header in required_header:
                    if header not in data[0]:
                        raise HTTPException(status_code=400, detail=f"Header {header} is not found in the CSV file.")

            return data, file_size
            
        except UnicodeDecodeError:
            await file.seek(0)  # Reset file pointer
            raise HTTPException(status_code=400, detail="File is not a valid UTF-8 encoded CSV file.")
        except csv.Error:
            await file.seek(0)  # Reset file pointer
            raise HTTPException(status_code=400, detail="Invalid CSV format.")
