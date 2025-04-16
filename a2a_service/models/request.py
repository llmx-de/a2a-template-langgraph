from typing import Any, List

class TaskSendParams:
    def __init__(self, id: str, sessionId: str, historyLength: int = 10, 
                 acceptedOutputModes: List[str] = None, pushNotification = None):
        self.id = id
        self.sessionId = sessionId
        self.historyLength = historyLength
        self.acceptedOutputModes = acceptedOutputModes or ["text"]
        self.pushNotification = pushNotification
        self.message = None  # This would hold user input message

class SendTaskRequest:
    def __init__(self, id: str, params: TaskSendParams):
        self.id = id
        self.params = params

class SendTaskStreamingRequest:
    def __init__(self, id: str, params: TaskSendParams):
        self.id = id
        self.params = params

class SendTaskResponse:
    def __init__(self, id: str, result: Any = None, error: Any = None):
        self.id = id
        self.result = result
        self.error = error

class SendTaskStreamingResponse:
    def __init__(self, id: str, result: Any = None, error: Any = None):
        self.id = id
        self.result = result
        self.error = error 