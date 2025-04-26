import csv
from io import StringIO
from fastapi import UploadFile, HTTPException

class CSVFileValidator:
    """Helper class for validating CSV files"""
    @staticmethod
    async def validate_csv_file(file: UploadFile, required_header: str):
 
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")
    
        contents = await file.read()
        file_size = len(contents)
        data = []
        
        try:
            text_content = contents.decode('utf-8')
            csv_file = StringIO(text_content)
            csv_to_dict = csv.DictReader(csv_file)

            for row in csv_to_dict:
                print('@@@@@@ row @@@@@@@')
                print(row[required_header])
                if row[required_header]:
                    data.append(row[required_header])
            
            await file.seek(0)
            return data, file_size
            
        except UnicodeDecodeError:
            await file.seek(0)  # Reset file pointer
            raise HTTPException(status_code=400, detail="File is not a valid UTF-8 encoded CSV file.")
        except csv.Error:
            await file.seek(0)  # Reset file pointer
            raise HTTPException(status_code=400, detail="Invalid CSV format.")
