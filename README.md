# A2A LangGraph Agent

**Empower your applications with Agent-to-Agent (A2A) protocol support.**

A production-ready agent server built with [LangGraph](https://github.com/langgraph/langgraph) that implements the Agent-to-Agent (A2A) protocol. Perfect for building advanced, real-time AI workflows and integrating AI capabilities into your applications.

## 🚀 Features
- 🔄 A2A Protocol Support: Full implementation of the Agent-to-Agent protocol.
- 🧠 LangGraph-powered Agent: Flexible agent architecture built on LangGraph's React pattern.
- 🔍 Extensible Tools: Easy integration of custom tools like search, database queries, and more.
- ⚡ Real-Time Streaming: Stream responses for live updates and interactive flows.
- 🗄️ Database-backed State Management: Maintain conversation state across sessions.
- 🌐 FastAPI HTTP Server: Robust HTTP server with proper A2A protocol endpoints.

## 🔧 Quick Start

1. **Clone the repo**
   ```bash
   git clone https://github.com/dmi3coder/a2a_template_langgraph.git
   cd a2a_template_langgraph
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   # or with uv
   uv install
   ```

3. **Set up PostgreSQL**
   Use the included Docker Compose file to start a PostgreSQL instance:
   ```bash
   docker-compose up -d
   ```

4. **Configure**
   Create a `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   HOST=0.0.0.0      # Optional, defaults to 0.0.0.0
   PORT=10000        # Optional, defaults to 10000
   OPENAI_MODEL=o4-mini # Optional, defaults to o4-mini
   ```

5. **Run the server**
   ```bash
   python main.py
   ```

Your agent server will be live on `http://{HOST}:{PORT}`.

## 🛠️ API Endpoints

- **GET /** or **GET /.well-known/agent.json**  
  Returns the agent card information following the A2A protocol.

- **POST /**  
  Send a one-off task to the agent.

- **POST /send_task_subscribe**  
  Stream a task to receive real-time responses.

## 📂 Project Structure

```
.
├── main.py                # Entry point
├── a2a_service/           # Core service package
│   ├── agent.py           # LangGraph agent implementation
│   ├── server.py          # A2A HTTP server
│   ├── database.py        # Database connection setup
│   ├── types.py           # All data types and models for the A2A protocol
│   ├── models/            # Database models 
│   │   └── db_models.py   # SQLAlchemy database models
│   ├── task_managers/     # Task management modules
│   │   ├── __init__.py    # Base task manager interface
│   │   ├── db_task_manager.py  # DB-backed task manager
│   │   └── async_inmem_task_manager.py  # In-memory task manager
│   └── tools/             # Agent tools
│       └── search.py      # Web search tool
├── alembic/               # Database migration scripts
├── alembic.ini            # Alembic configuration
├── pyproject.toml         # Project configuration & dependencies
├── docker-compose.yaml    # Docker setup for PostgreSQL
└── README.md              # This file
```

## 🛠️ Tech Stack

- **Python 3.13+**  
- **[LangGraph](https://github.com/langgraph/langgraph)** for agent orchestration  
- **[LangChain](https://github.com/langchain-ai/langchain)** for LLM components
- **FastAPI** & **Uvicorn** for HTTP server  
- **PostgreSQL** via **SQLAlchemy** & **Alembic** migrations  
- **OpenAI** for LLM capabilities  
- **Pydantic** for data validation and serialization

## 🔌 Extending the Agent

To add custom tools:
1. Create a new Python file in the `a2a_service/tools/` directory
2. Define your tool using the `@tool` decorator from LangChain
3. Import and add your tool to the Agent's tools list in `main.py`

Example:

```python
# a2a_service/tools/my_tool.py
from langchain_core.tools import tool

@tool
def my_custom_tool(param: str) -> str:
    """Description of what this tool does.
    
    Args:
        param: Description of the parameter
        
    Returns:
        Description of the return value
    """
    # Your implementation here
    return f"Processed: {param}"
```

## 💬 Get in touch

- [Website](https://llmx.de)
- [LinkedIn](https://www.linkedin.com/in/dmytro--ch/)
- [X](https://x.com/dmytro__ch)
- [GitHub](https://github.com/llmx-de)
- [Email](mailto:dmytro.de.ch@gmail.com)

---

Feel free to contribute or report issues!

