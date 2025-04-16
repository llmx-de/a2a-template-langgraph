import logging
import fastapi
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uvicorn
from a2a_service.models import AgentCapabilities, AgentSkill, AgentCard, SendTaskRequest, TaskSendParams, SendTaskStreamingRequest, Message, TextPart

logger = logging.getLogger(__name__)

class A2AServer:
    """A server for A2A (Agent-to-Agent) communication."""
    
    def __init__(self, agent_card: AgentCard, task_manager, host: str = "0.0.0.0", port: int = 10000):
        """Initialize the server.
        
        Args:
            agent_card: Information about the agent.
            task_manager: Manager for handling agent tasks.
            host: Host to bind the server.
            port: Port to bind the server.
        """
        self.agent_card = agent_card
        self.task_manager = task_manager
        self.host = host
        self.port = port
        
        # Create FastAPI app
        self.app = FastAPI(title=f"{agent_card.name} API", version=agent_card.version)
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes()
        
    def _register_routes(self):
        """Register API routes."""
        
        @self.app.get("/")
        async def get_agent_info():
            """Return information about the agent."""
            return self.agent_card
            
        @self.app.get("/.well-known/agent.json")
        async def get_agent_json():
            """Serve the agent card at the .well-known location."""
            return self.agent_card
            
        def _process_message(message_data):
            """Helper method to process message data into proper Message object."""
            if "parts" in message_data and isinstance(message_data["parts"], list):
                # The message already has parts, use as is
                return message_data
            else:
                # Create a default text part if message is a simple string or doesn't have parts
                text = ""
                if isinstance(message_data, str):
                    text = message_data
                elif isinstance(message_data, dict) and "text" in message_data:
                    text = message_data["text"]
                
                if text:
                    # Create a proper Message object with text part
                    return Message(
                        role="user", 
                        parts=[{"type": "text", "text": text}]
                    )
            return None
                        
        @self.app.post("/")
        async def send_task(request: Request):
            """Handle send_task requests."""
            body = await request.json()
            
            # Debug logging
            logger.info(f"Received request body: {body}")
            
            # Convert the dict to a properly structured SendTaskRequest object
            
            # Extract parameters from the request body
            request_id = body.get("id", "")
            params_data = body.get("params", {})
            
            # Create TaskSendParams object
            params = TaskSendParams(
                id=params_data.get("id", ""),
                sessionId=params_data.get("sessionId", ""),
                historyLength=params_data.get("historyLength", 10),
                acceptedOutputModes=params_data.get("acceptedOutputModes", ["text"]),
                pushNotification=params_data.get("pushNotification", None)
            )
            
            # Add message if present
            if "message" in params_data:
                message_data = params_data["message"]
                logger.info(f"Message found in params: {message_data}")
                params.message = _process_message(message_data)
                if params.message:
                    logger.info(f"Processed message: {params.message}")
            else:
                logger.warning("No message found in request params")
                
            # Create SendTaskRequest object
            request_obj = SendTaskRequest(id=request_id, params=params)
            
            return await self.task_manager.on_send_task(request_obj)
            
        @self.app.post("/send_task_subscribe")
        async def send_task_subscribe(request: Request):
            """Handle streaming task requests."""
            body = await request.json()
            
            # Debug logging
            logger.info(f"Received streaming request body: {body}")
            
            # Convert the dict to a properly structured SendTaskStreamingRequest object
            
            # Extract parameters from the request body
            request_id = body.get("id", "")
            params_data = body.get("params", {})
            
            # Create TaskSendParams object
            params = TaskSendParams(
                id=params_data.get("id", ""),
                sessionId=params_data.get("sessionId", ""),
                historyLength=params_data.get("historyLength", 10),
                acceptedOutputModes=params_data.get("acceptedOutputModes", ["text"]),
                pushNotification=params_data.get("pushNotification", None)
            )
            
            # Add message if present
            if "message" in params_data:
                message_data = params_data["message"]
                logger.info(f"Message found in params: {message_data}")
                params.message = _process_message(message_data)
                if params.message:
                    logger.info(f"Processed message: {params.message}")
            else:
                logger.warning("No message found in request params")
                
            # Create SendTaskStreamingRequest object
            request_obj = SendTaskStreamingRequest(id=request_id, params=params)
            
            return await self.task_manager.on_send_task_subscribe(request_obj)
            
    def start(self):
        """Start the server."""
        uvicorn.run(self.app, host=self.host, port=self.port) 