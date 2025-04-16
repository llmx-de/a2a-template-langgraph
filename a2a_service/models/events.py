from a2a_service.models.task import TaskStatus, Artifact

class TaskArtifactUpdateEvent:
    def __init__(self, id: str, artifact: Artifact):
        self.id = id
        self.artifact = artifact

class TaskStatusUpdateEvent:
    def __init__(self, id: str, status: TaskStatus, final: bool = False):
        self.id = id
        self.status = status
        self.final = final 