# A2A LangGraph Agent

A production-ready agent server built with LangGraph that communicates using the Agent-to-Agent (A2A) protocol.

## Setup

1. Clone the repository
2. Create a virtual environment and activate it

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
```

3. Install the dependencies

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:

```
OPENAI_API_KEY=your_openai_api_key
HOST=localhost  # Optional, defaults to localhost
PORT=10001  # Optional, defaults to 10001
OPENAI_MODEL=gpt-4o  # Optional, defaults to gpt-4o
```

## Running the server

```bash
python main.py
```

This will start the server on `localhost:10001` (or as configured in your `.env` file).

## Features

- A versatile agent that can answer questions using search tools
- Streaming responses for real-time updates
- Structured conversation state management
- Built with LangGraph for complex reasoning

## API

The server exposes the following endpoints:

- `GET /`: Returns information about the agent
- `POST /send_task`: Handles requests for the agent to perform a task
- `POST /send_task_subscribe`: Handles streaming task requests

## Project Structure

- `a2a_service/`: Main package containing the agent implementation
  - `agent.py`: The LangGraph agent implementation
  - `server.py`: The A2A server implementation
  - `models/`: Data models used by the agent and server
  - `task_managers/`: Task managers for handling agent tasks
  - `tools/`: Tools used by the agent