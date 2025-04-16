from typing import Any

class InternalError:
    def __init__(self, message: str):
        self.message = message

class InvalidParamsError:
    def __init__(self, message: str):
        self.message = message

class JSONRPCResponse:
    def __init__(self, id: str, error: Any = None):
        self.id = id
        self.error = error 