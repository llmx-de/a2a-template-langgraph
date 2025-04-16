from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, ToolMessage
from typing import Any, Dict, AsyncIterable, Literal, List, Optional, Union
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from a2a_service.models.response import ResponseFormat
from a2a_service.tools import search_web

# Memory saver for maintaining conversation state
memory = MemorySaver()


class Agent:
    """A production-ready agent implementation using LangGraph."""

    SYSTEM_INSTRUCTION = """
    You are a helpful AI assistant that can answer questions on a wide range of topics.
    Your goal is to provide accurate, helpful information to the user.
    
    When responding, use the following guidelines:
    - Provide clear, concise answers based on factual information
    - Use the available tools when appropriate to gather information
    - If you don't know the answer, say so rather than making up information
    - If the user request is unclear, ask for clarification
    - Set response status to input-required if the user needs to provide more information
    - Set response status to error if there is an error while processing the request
    - Set response status to completed if the request is complete
    """
     
    def __init__(self, model_name: str = "gpt-4.1", tools: Optional[List[Any]] = None):
        """Initialize the agent with a model and tools.
        
        Args:
            model_name: The name of the LLM model to use.
            tools: Optional list of tools. If None, default tools will be used.
        """
        # Initialize the LLM model
        self.model = ChatOpenAI(
            model=model_name,
            temperature=0.1,
            streaming=True
        )
        
        # Use provided tools or default to the included tools
        self.tools = tools or [search_web]

        # Create the agent graph using LangGraph
        self.graph = create_react_agent(
            self.model, 
            tools=self.tools, 
            checkpointer=memory, 
            prompt=self.SYSTEM_INSTRUCTION, 
            response_format=ResponseFormat
        )

    def invoke(self, query: str, session_id: str) -> Dict[str, Any]:
        """Synchronous invocation of the agent.
        
        Args:
            query: The user query.
            session_id: A unique session identifier for maintaining conversation context.
            
        Returns:
            A structured response containing the agent's answer.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Agent received query: '{query}' with session_id: {session_id}")
        
        if not query or query.strip() == "":
            logger.warning("Empty query received, returning default response")
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "content": "I didn't receive any message. How can I help you?"
            }
            
        config = {"configurable": {"thread_id": session_id}}
        self.graph.invoke({"messages": [("user", query)]}, config)
        
        response = self.get_agent_response(config)
        logger.info(f"Agent returning response: {response}")
        return response

    async def stream(self, query: str, session_id: str) -> AsyncIterable[Dict[str, Any]]:
        """Asynchronous streaming invocation of the agent.
        
        Args:
            query: The user query.
            session_id: A unique session identifier for maintaining conversation context.
            
        Yields:
            Intermediate and final responses from the agent.
        """
        inputs = {"messages": [("user", query)]}
        config = {"configurable": {"thread_id": session_id}}

        for item in self.graph.stream(inputs, config, stream_mode="values"):
            message = item["messages"][-1]
            
            # When the agent is thinking about using a tool
            if (
                isinstance(message, AIMessage)
                and message.tool_calls
                and len(message.tool_calls) > 0
            ):
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": "Thinking...",
                }
            # When a tool is being executed
            elif isinstance(message, ToolMessage):
                yield {
                    "is_task_complete": False,
                    "require_user_input": False,
                    "content": "Processing information...",
                }            
        
        # Final response after processing
        yield self.get_agent_response(config)

    def get_agent_response(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured response from the agent.
        
        Args:
            config: The configuration dictionary with thread_id.
            
        Returns:
            A structured response with task completion status and content.
        """
        current_state = self.graph.get_state(config)        
        structured_response = current_state.values.get('structured_response')
        
        if structured_response and isinstance(structured_response, ResponseFormat): 
            if structured_response.status == "input-required":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.message
                }
            elif structured_response.status == "error":
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "content": structured_response.message
                }
            elif structured_response.status == "completed":
                return {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "content": structured_response.message
                }

        # Default response if structured_response is not available
        return {
            "is_task_complete": False,
            "require_user_input": True,
            "content": "We are unable to process your request at the moment. Please try again.",
        }

    # Content types supported by this agent
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"] 