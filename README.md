# BaaS - Bot-as-a-Service Platform

A lightweight, asynchronous backend service built with Python and FastAPI that dynamically provisions, manages, and runs AI-powered Discord bots in the background.

Unlike standard monolithic chat bots, this project serves as a foundational microservice architecture. It provides a RESTful API to configure bot personalities via a database and utilizes background workers to maintain WebSocket connections with Discord while independently querying Large Language Models (LLMs).

## Key Features

* **REST API Management:** Full CRUD operations to create and configure bot instances with custom system prompts and target platforms.
* **Asynchronous Workers:** Uses FastAPI's `BackgroundTasks` and `asyncio` to run Discord clients concurrently without blocking the main web server thread.
* **Dynamic AI Integration:** Integrated with the Groq API (running LLaMA 3.1) for lightning-fast, context-aware text generation based on database-stored prompts.
* **ORM Database:** Utilizes SQLAlchemy for robust database interactions, currently configured with SQLite for rapid development, but structured for immediate drop-in replacement with PostgreSQL.
* **State Control:** Endpoints to start and gracefully shut down active WebSocket connections on demand.

##  Tech Stack

* **Framework:** FastAPI, Uvicorn
* **Database:** SQLAlchemy (SQLite)
* **AI Engine:** Groq API (`llama-3.1-8b-instant`)
* **Platform Integration:** `discord.py`
* **Environment Management:** `python-dotenv`

## Setup & Installation

1. Clone the repository and navigate to the project directory:
```bash
git clone <your-repo-url>
cd BaaS

2. Create and activate a virtual environment: 

Bash
python -m venv venv
source venv/bin/activate

3. Install dependencies:

Bash
pip install -r requirements.txt

4. Configure environment variables:
Create a .env file in the root directory and add your API keys:

GROQ_API_KEY=your_groq_api_key
DISCORD_BOT_TOKEN=your_discord_bot_token

5. Run the server:

Bash
python -m uvicorn main:app --reload
