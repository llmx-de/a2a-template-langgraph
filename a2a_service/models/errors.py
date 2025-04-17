from typing import Any

class InternalError:
    def __init__(self, message: str, code: int = -32603):
        self.code = code
        self.message = message

class InvalidParamsError:
    def __init__(self, message: str, code: int = -32602):
        self.code = code
        self.message = message

class JSONRPCResponse:
    def __init__(self, id: str, error: Any = None):
        self.id = id
        self.error = error 