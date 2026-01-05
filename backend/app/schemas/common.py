"""Common Schemas"""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """错误响应"""

    error: str
    message: str
