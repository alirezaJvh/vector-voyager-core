from typing import Optional

from src.exceptions.enums import ErrorEnum


class CSVValidatorExceptionError(Exception):
    """Exception raised for errors in the CSV validator."""

    def __init__(
        self,
        error: ErrorEnum.CSVValidatorError,
        message: Optional[str] = None,
    ):
        self.error = error
        self.message = message if message is not None else error.value
        super().__init__(self.message)
