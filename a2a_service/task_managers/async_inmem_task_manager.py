from typing import AsyncIterable, Union, Dict, Any, List, Optional
import asyncio
import logging
import traceback
from a2a_service.agent import Agent
from a2a_service.models import (
    TaskState,
    Message,
    TaskStatus,
    Artifact,
    Task,
    TaskSendParams,
    SendTaskRequest,
    SendTaskStreamingRequest,
    SendTaskResponse,
    SendTaskStreamingResponse,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
    InternalError,
    InvalidParamsError,
    JSONRPCResponse
)
from a2a_service.task_managers import InMemoryTaskManager


class AgentTaskManager(InMemoryTaskManager):
    def __init__(self, agent: Agent):
        super().__init__()
        self.agent = agent
        self.logger = logging.getLogger(__name__)

    async def _run_streaming_agent(self, request: SendTaskStreamingRequest):
        """Runs the agent in streaming mode and updates the task status and artifacts."""
        task_send_params: TaskSendParams = request.params
        query = self._get_user_query(task_send_params)

        try:
            async for item in self.agent.stream(query, task_send_params.sessionId):
                is_task_complete = item["is_task_complete"]
                require_user_input = item["require_user_input"]
                artifact = None
                message = None
                parts = [{"type": "text", "text": item["content"]}]
                end_stream = False

                if not is_task_complete and not require_user_input:
                    # Agent is still working
                    task_state = TaskState.WORKING
                    message = Message(role="agent", parts=parts)
                elif require_user_input:
                    # Agent needs more input from the user
                    task_state = TaskState.INPUT_REQUIRED
                    message = Message(role="agent", parts=parts)
                    end_stream = True
                else:
                    # Agent has completed the task
                    task_state = TaskState.COMPLETED
                    artifact = Artifact(parts=parts, index=0, append=False)
                    end_stream = True

                task_status = TaskStatus(state=task_state, message=message)
                latest_task = await self.update_store(
                    task_send_params.id,
                    task_status,
                    None if artifact is None else [artifact],
                )

                # If there's an artifact, send it as an event
                if artifact:
                    task_artifact_update_event = TaskArtifactUpdateEvent(
                        id=task_send_params.id, artifact=artifact
                    )
                    await self.enqueue_events_for_sse(
                        task_send_params.id, task_artifact_update_event
                    )                    
                
                # Send status update event
                task_update_event = TaskStatusUpdateEvent(
                    id=task_send_params.id, status=task_status, final=end_stream
                )
                await self.enqueue_events_for_sse(
                    task_send_params.id, task_update_event
                )

        except Exception as e:
            self.logger.error(f"An error occurred while streaming the response: {e}")
            await self.enqueue_events_for_sse(
                task_send_params.id,
                InternalError(message=f"An error occurred while streaming the response: {e}")                
            )

    def _validate_request(
        self, request: Union[SendTaskRequest, SendTaskStreamingRequest]
    ) -> JSONRPCResponse | None:
        """Validates the task request."""
        task_send_params: TaskSendParams = request.params
        
        # Check if the agent's content types are compatible with the accepted output modes
        if not self._are_modalities_compatible(
            task_send_params.acceptedOutputModes, self.agent.SUPPORTED_CONTENT_TYPES
        ):
            self.logger.warning(
                "Unsupported output mode. Received %s, Support %s",
                task_send_params.acceptedOutputModes,
                self.agent.SUPPORTED_CONTENT_TYPES,
            )
            return self._new_incompatible_types_error(request.id)
        
        return None
    
    def _are_modalities_compatible(
        self, accepted_modes: List[str], supported_modes: List[str]
    ) -> bool:
        """Check if at least one of the accepted modes is supported."""
        return any(mode in supported_modes for mode in accepted_modes)
    
    def _new_incompatible_types_error(self, request_id: str) -> JSONRPCResponse:
        """Creates an error response for incompatible content types."""
        return JSONRPCResponse(
            id=request_id, 
            error=InvalidParamsError(message="Incompatible content types")
        )
        
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """Handles the 'send task' request."""
        validation_error = self._validate_request(request)
        if validation_error:
            return SendTaskResponse(id=request.id, error=validation_error.error)

        await self.upsert_task(request.params)
        task = await self.update_store(
            request.params.id, TaskStatus(state=TaskState.WORKING), None
        )

        task_send_params: TaskSendParams = request.params
        query = self._get_user_query(task_send_params)
        self.logger.info(f"Extracted query for agent: '{query}'")
        
        if not query:
            self.logger.warning("Empty query extracted, setting to default")
            query = "Hello"
        
        try:
            self.logger.info(f"Invoking agent with query: '{query}' and session: {task_send_params.sessionId}")
            agent_response = self.agent.invoke(query, task_send_params.sessionId)
            self.logger.info(f"Agent response: {agent_response}")
        except Exception as e:
            self.logger.error(f"Error invoking agent: {e}")
            return SendTaskResponse(
                id=request.id,
                error=InternalError(message=f"Error invoking agent: {e}")
            )
            
        return await self._process_agent_response(request, agent_response)

    async def on_send_task_subscribe(
        self, request: SendTaskStreamingRequest
    ) -> AsyncIterable[SendTaskStreamingResponse] | JSONRPCResponse:
        """Handles the 'send task subscribe' request for streaming responses."""
        try:
            error = self._validate_request(request)
            if error:
                return error

            await self.upsert_task(request.params)

            task_send_params: TaskSendParams = request.params
            sse_event_queue = await self.setup_sse_consumer(task_send_params.id, False)            

            asyncio.create_task(self._run_streaming_agent(request))

            return self.dequeue_events_for_sse(
                request.id, task_send_params.id, sse_event_queue
            )
        except Exception as e:
            self.logger.error(f"Error in SSE stream: {e}")
            print(traceback.format_exc())
            return JSONRPCResponse(
                id=request.id,
                error=InternalError(
                    message="An error occurred while streaming the response"
                ),
            )

    async def _process_agent_response(
        self, request: SendTaskRequest, agent_response: dict
    ) -> SendTaskResponse:
        """Processes the agent's response and updates the task store."""
        task_send_params: TaskSendParams = request.params
        task_id = task_send_params.id
        task_status = None

        parts = [{"type": "text", "text": agent_response["content"]}]
        artifact = None
        
        if agent_response["require_user_input"]:
            task_status = TaskStatus(
                state=TaskState.INPUT_REQUIRED,
                message=Message(role="agent", parts=parts),
            )
        else:
            task_status = TaskStatus(state=TaskState.COMPLETED)
            artifact = Artifact(parts=parts)
            
        task = await self.update_store(
            task_id, task_status, None if artifact is None else [artifact]
        )
        
        return SendTaskResponse(
            id=request.id,
            result={
                "id": task_id,
                "status": task.status,
                "artifacts": task.artifacts
            }
        )

    def _get_user_query(self, task_send_params: TaskSendParams) -> str:
        """Extracts the user query from the task parameters."""
        self.logger.info(f"Extracting query from task params: {task_send_params.__dict__}")
        
        if not task_send_params.message:
            self.logger.warning("No message found in task params")
            return ""
            
        self.logger.info(f"Message object: {task_send_params.message}")
        
        # Handle case where message is a dict (instead of Message object)
        if isinstance(task_send_params.message, dict) and "parts" in task_send_params.message:
            parts = task_send_params.message["parts"]
            self.logger.info(f"Found message parts (dict): {parts}")
            
            for part in parts:
                if part.get("type") == "text":
                    text = part.get("text", "")
                    self.logger.info(f"Extracted text from part: {text}")
                    return text
        # Handle case where message is a Message object with parts attribute
        elif hasattr(task_send_params.message, "parts"):
            parts = task_send_params.message.parts
            self.logger.info(f"Found message parts (object): {parts}")
            
            for part in parts:
                if part.get("type") == "text":
                    text = part.get("text", "")
                    self.logger.info(f"Extracted text from part: {text}")
                    return text
                    
        self.logger.warning("No text parts found in message")
        return "" 