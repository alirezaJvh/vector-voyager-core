from enum import Enum, unique


class ErrorEnum:
    """
    A collection of enums for categorizing different types of errors.
    """

    @unique
    class CSVValidatorError(Enum):
        """
        An enum for categorizing errors that occur during CSV validation.
        """

        CSV_FILE_NOT_FOUND = "CSV File Not Found"
        CSV_FILE_EMPTY = "CSV File Empty"
        CSV_HEADER_NOT_FOUND = "CSV Header Not Found"
        CSV_INVALID_FORMAT = "CSV Invalid Format"
        CSV_INVALID_ENCODING = "CSV Invalid Encoding"
