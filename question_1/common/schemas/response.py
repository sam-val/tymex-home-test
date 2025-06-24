from typing import Dict, Generic, Optional, TypeVar

from pydantic import BaseModel

DataType = TypeVar("DataType")


class StandardResponse(
    BaseModel,
    Generic[DataType],
):
    data: DataType
    message: Optional[str] = "Success"
