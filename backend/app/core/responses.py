from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def envelope(data: Any = None, message: str = "OK", status_code: int = 200) -> JSONResponse:
    """Standardized response envelope: { data, message, status_code }."""
    return JSONResponse(
        status_code=status_code,
        content={
            "data": jsonable_encoder(data),
            "message": message,
            "status_code": status_code,
        },
    )


class ApiError(Exception):
    """Domain error carrying an HTTP status code, rendered via the global handler."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(message)
