import os
import logging
from dotenv import load_dotenv
from a2a_service.server import A2AServer
from a2a_service.models import AgentCapabilities, AgentSkill, AgentCard
from a2a_service.agent import Agent
from a2a_service.task_managers.db_task_manager import DatabaseTaskManager

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 10000))
MODEL = os.getenv("OPENAI_MODEL", "o4-mini")

# Create agent capabilities and skills
capabilities = AgentCapabilities(streaming=False, pushNotifications=False)

skill = AgentSkill(
    id="information_retrieval",
    name="Information Retrieval",
    description="Answers questions using search tools",
    tags=["search", "information", "questions"],
    examples=["What is the capital of France?", "Who won the World Cup in 2018?"],
)

# Create agent card
agent_card = AgentCard(
    name="LangGraph Agent",
    description="A versatile agent that can answer questions using search tools",
    url=f"http://{HOST}:{PORT}/",
    version="1.0.0",
    defaultInputModes=Agent.SUPPORTED_CONTENT_TYPES,
    defaultOutputModes=Agent.SUPPORTED_CONTENT_TYPES,
    capabilities=capabilities,
    skills=[skill],
)

def main():
    """Creates and starts the A2A LangGraph Agent server."""
    try:
        # Initialize agent with specified model
        agent = Agent(model_name=MODEL)
        
        # Create database-backed task manager
        task_manager = DatabaseTaskManager(agent=agent)
        
        # Create and start server
        server = A2AServer(
            agent_card=agent_card,
            task_manager=task_manager,
            host=HOST,
            port=PORT,
        )

        logger.info(f"Starting LangGraph Agent server on {HOST}:{PORT}")
        server.start()
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)

if __name__ == "__main__":
    main()
