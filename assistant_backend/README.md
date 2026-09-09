# Local Assistant Backend

Phase 1 of the local-first personal AI assistant. 
This project uses FastAPI, SQLAlchemy (SQLite), and provides a clean foundation for extending into a full assistant backend.

## Structure
- `app/api`: FastAPI routers and endpoints.
- `app/core`: Core configurations, exceptions, logging.
- `app/database`: SQLAlchemy session and base models.
- `app/models`: SQLAlchemy DB models (empty for now).
- `app/schemas`: Pydantic schemas (empty for now).
- `app/services`: Business logic (empty for now).
- `app/tools`: Tools for the AI (empty for now).
- `tests`: Pytest tests.

## Setup
1. **Ensure Ollama is installed and running**
   You can download Ollama from [ollama.com](https://ollama.com/).
   Pull your desired model, for example:
   ```bash
   ollama run llama3
   ```

2. **Create a virtual environment and install dependencies:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure the environment:**
```bash
cp .env.example .env
```
Edit `.env` to match your Ollama setup if needed (default is `http://localhost:11434` with model `llama3`).

## Run the Server
```bash
uvicorn app.main:app --reload
```

## Run Tests
```bash
pytest
```

## API Examples

### Chat (Create or Continue Conversation)

**Create a new conversation:**
```json
POST /api/chat
{
  "message": "My name is Alex"
}
```

**Continue an existing conversation:**
```json
POST /api/chat
{
  "conversation_id": "your-uuid-here",
  "message": "What is my name?"
}
```

### Conversations Management

**List all conversations:**
```
GET /api/conversations
```

**Retrieve a specific conversation (with messages):**
```
GET /api/conversations/{conversation_id}
```

**Delete a conversation:**
```
DELETE /api/conversations/{conversation_id}
```
