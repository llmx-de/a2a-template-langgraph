from typing import List
import asyncio
import logging
from a2a_service.agent import Agent
from a2a_service.types import (
    TaskState,
    Message,
    TaskStatus,
    Artifact,
    Task,
    TaskSendParams,
    SendTaskStreamingResponse,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
    InternalError,
)

# Base in-memory task manager
class InMemoryTaskManager:
    def __init__(self):
        self.tasks = {}
        self.sse_queues = {}
        self.logger = logging.getLogger(__name__)

    async def upsert_task(self, task_params: TaskSendParams):
        """Creates or updates a task."""
        self.tasks[task_params.id] = Task(
            id=task_params.id,
            status=TaskStatus(state=TaskState.WORKING),
            artifacts=[]
        )

    async def update_store(self, task_id: str, task_status: TaskStatus, artifacts: List[Artifact] = None) -> Task:
        """Updates a task's status and artifacts in the store."""
        if task_id not in self.tasks:
            self.tasks[task_id] = Task(id=task_id, status=task_status, artifacts=[])
        else:
            self.tasks[task_id].status = task_status
            if artifacts:
                self.tasks[task_id].artifacts.extend(artifacts)
        return self.tasks[task_id]

    async def setup_sse_consumer(self, task_id: str, clear_if_exists: bool = True):
        """Sets up an async queue for SSE events."""
        if task_id in self.sse_queues and clear_if_exists:
            # Clear existing queue
            self.sse_queues[task_id] = asyncio.Queue()
        elif task_id not in self.sse_queues:
            self.sse_queues[task_id] = asyncio.Queue()
        return self.sse_queues[task_id]

    async def enqueue_events_for_sse(self, task_id: str, event):
        """Enqueues events for SSE consumers."""
        if task_id in self.sse_queues:
            await self.sse_queues[task_id].put(event)

    async def dequeue_events_for_sse(self, request_id: str, task_id: str, queue):
        """Dequeues events for SSE consumers."""
        try:
            while True:
                event = await queue.get()
                if isinstance(event, InternalError):
                    yield SendTaskStreamingResponse(id=request_id, error=event)
                elif isinstance(event, TaskStatusUpdateEvent):
                    if event.final:
                        # Final event, close the stream
                        yield SendTaskStreamingResponse(
                            id=request_id, 
                            result={"id": task_id, "status": event.status}
                        )
                        break
                    else:
                        yield SendTaskStreamingResponse(
                            id=request_id, 
                            result={"id": task_id, "status": event.status}
                        )
                elif isinstance(event, TaskArtifactUpdateEvent):
                    yield SendTaskStreamingResponse(
                        id=request_id, 
                        result={"id": task_id, "artifact": event.artifact}
                    )
        except asyncio.CancelledError:
            self.logger.info(f"SSE stream for task {task_id} was cancelled")
        except Exception as e:
            self.logger.error(f"Error in SSE stream for task {task_id}: {e}")
            yield SendTaskStreamingResponse(
                id=request_id,
                error=InternalError(message=f"Stream error: {str(e)}")
            )

