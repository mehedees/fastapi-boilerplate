from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response schema.
    Attributes:
        success (bool): Indicates if the API request was successful.
        message (str | None): Optional message providing additional information about the response.
        data (T | None): The actual data returned by the API, of generic type T.
    """

    success: bool = True
    message: str | None = None
    data: T | None = None
