from typing import Literal
from pydantic import BaseModel

class ResponseFormat(BaseModel):
    """Respond to the user in this format."""
    status: Literal["input-required", "completed", "error"] = "input-required"
    message: str 