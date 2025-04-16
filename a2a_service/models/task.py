from typing import Dict, Any, List, Optional

class Message:
    def __init__(self, role: str, parts: List[Dict[str, Any]]):
        self.role = role
        self.parts = parts

class TextPart:
    def __init__(self, text: str):
        self.type = "text"
        self.text = text

class TaskStatus:
    def __init__(self, state: str, message: Optional[Message] = None):
        self.state = state
        self.message = message

class Artifact:
    def __init__(self, parts: List[Dict[str, Any]], index: int = 0, append: bool = False):
        self.parts = parts
        self.index = index
        self.append = append

class Task:
    def __init__(self, id: str, status: TaskStatus, artifacts: List[Artifact] = None):
        self.id = id
        self.status = status
        self.artifacts = artifacts or [] 