
import csv
from io import StringIO
from fastapi import UploadFile

from db.vector_db import VectorDBClient
from exceptions.handler import CSVValidatorExceptionError, ErrorEnum


async def _validate_csv_file(file, required_header: list[str] = []):
    """
    Validate the CSV file.
    
    Args:
        file: The uploaded file.
        required_header: List of required headers.
    
    Returns:
        tuple: A tuple containing the list of data and the file size.
    
    Raises:
        CSVValidatorExceptionError: If the file is not a CSV file.
        CSVValidatorExceptionError: If the file is empty.
        CSVValidatorExceptionError: If the required header is not found.
        CSVValidatorExceptionError: If the file is not a valid CSV format.
    """
    if not file.filename.endswith(".csv"):
        raise CSVValidatorExceptionError(ErrorEnum.CSVValidatorError.CSV_FILE_NOT_FOUND)

    contents = await file.read()
    file_size = len(contents)

    try:
        text_content = contents.decode("utf-8")
        csv_file = StringIO(text_content)
        csv_to_dict = csv.DictReader(csv_file)
        data = list(csv_to_dict)
        await file.seek(0)

        if not data:
            raise CSVValidatorExceptionError(ErrorEnum.CSVValidatorError.CSV_FILE_EMPTY)

        if len(required_header):
            for header in required_header:
                if header not in data[0]:
                    raise CSVValidatorExceptionError(
                        ErrorEnum.CSVValidatorError.CSV_HEADER_NOT_FOUND
                    )

        return data, file_size

    except UnicodeDecodeError:
        await file.seek(0)  # Reset file pointer
        raise CSVValidatorExceptionError(ErrorEnum.CSVValidatorError.CSV_INVALID_ENCODING)
    except csv.Error:
        await file.seek(0)  # Reset file pointer
        raise CSVValidatorExceptionError(ErrorEnum.CSVValidatorError.CSV_INVALID_FORMAT)


async def save_csv_as_vector(
    file: UploadFile,
    review_header: str,
    product_id_header: str,
    vector_db: VectorDBClient
):
    """
    Save the CSV file as vector embeddings.
    
    Args:
        file: The uploaded file.
        review_header: The header for the review text.
        product_id_header: The header for the product ID.
    
    Returns:
        tuple: A tuple containing the total number of processed reviews and the file size.
    
    Raises:
        CSVValidatorExceptionError: If the file is not a CSV file.
        CSVValidatorExceptionError: If the file is empty.
        CSVValidatorExceptionError: If the required header is not found.
        CSVValidatorExceptionError: If the file is not a valid CSV format.
    """
    data, file_size = await _validate_csv_file(
        file=file, required_header=[review_header, product_id_header]
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
        batch_reviews = reviews[idx : idx + batch_size]
        batch_product_ids = product_ids[idx : idx + batch_size]

        # add embedding to vector database
        indices = await vector_db.add_embedding_batch(batch_reviews, batch_product_ids)
        total_processed += len(indices)

    return total_processed, file_size
