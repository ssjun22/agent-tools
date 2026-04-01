---
name: fastapi-llm-templates
description: Create production-ready FastAPI projects optimized for LLM integration, async streaming, and stateless service patterns. Use when building LLM inference servers, prompt gateways, or AI-powered microservices that do not require a local database.
---

# FastAPI LLM Server Templates

Production-ready FastAPI project structures specifically designed for LLM (Large Language Model) applications. Focuses on async non-blocking I/O, streaming responses, prompt management, and external API integration.

## When to Use This Skill

- Building LLM-powered APIs (OpenAI, Anthropic, Local LLMs)
- Implementing real-time streaming chat interfaces
- Creating stateless AI microservices
- Setting up prompt engineering and management gateways
- Developing high-performance AI agents without database overhead

## Core Concepts

### 1. Stateless Project Structure

**Recommended Layout:**

```
app/
├── api/                    # API routes
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── chat.py     # Main LLM logic
│   │   │   └── models.py   # Model info/meta
│   │   └── router.py
│   └── dependencies.py     # Shared dependencies (Auth, Clients)
├── core/                   # Core configuration
│   ├── config.py           # API Keys, Model settings
│   ├── security.py         # API Key validation
│   └── logger.py           # LLM I/O logging
├── schemas/                # Pydantic schemas (Data Validation)
│   ├── chat.py             # Message, Request, Response
│   └── model.py            # Model parameters
├── services/               # Business logic & LLM Integration
│   ├── llm_service.py      # LLM provider orchestration
│   └── prompt_manager.py   # Prompt templates & logic
└── main.py                 # Application entry
```

### 2. Async Streaming

LLM responses can be slow. Using `StreamingResponse` and `async/await` is critical to prevent blocking the server and provide a better UX.

### 3. Service Layer Pattern

Encapsulates complex LLM provider logic (OpenAI, LangChain, etc.) away from the API routes, making the code testable and modular.

---

## Implementation Patterns

### Pattern 1: Complete LLM Application Setup

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router

app = FastAPI(
    title="LLM Inference API",
    version="1.0.0",
)

# CORS middleware for Frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings and secrets."""
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str | None = None
    DEFAULT_MODEL: str = "gpt-4-turbo"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### Pattern 2: LLM Service with Streaming

```python
# services/llm_service.py
import json
from openai import AsyncOpenAI
from app.core.config import get_settings

settings = get_settings()

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def stream_chat_completion(self, messages: list, model: str = None):
        """Streams LLM responses token by token."""
        response = await self.client.chat.completions.create(
            model=model or settings.DEFAULT_MODEL,
            messages=messages,
            stream=True
        )

        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content

llm_service = LLMService()
```

### Pattern 3: API Endpoints (Stateless)

```python
# api/v1/endpoints/chat.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.services.llm_service import llm_service
from app.api.dependencies import validate_api_key

router = APIRouter()

@router.post("/completions", dependencies=[Depends(validate_api_key)])
async def create_completion(request: ChatRequest):
    """Endpoint for streaming LLM chat completions."""
    try:
        return StreamingResponse(
            llm_service.stream_chat_completion(
                messages=[m.dict() for m in request.messages],
                model=request.model
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Pattern 4: Pydantic Schemas for LLM I/O

```python
# schemas/chat.py
from pydantic import BaseModel, Field
from typing import List, Optional

class Message(BaseModel):
    role: str # 'system', 'user', 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0, le=2)

class ChatResponse(BaseModel):
    id: str
    content: str
    usage: Optional[dict] = None
```

---

## Testing (Mocking LLM)

```python
# tests/test_chat.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_chat_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/chat/completions",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "model": "gpt-4"
            }
        )
    assert response.status_code == 200
    # Add logic to verify streaming chunks if necessary
```

---

## Best Practices

1.  **Async/Await Everywhere**: Never use blocking code (`requests`, `time.sleep`) in LLM routes.
2.  **Streaming Response**: Always prefer `StreamingResponse` for long-running LLM tasks to minimize perceived latency.
3.  **Prompt Separation**: Keep prompts in `services/prompt_manager.py` or external YAML files, not hardcoded in routes.
4.  **Error Propagation**: Handle LLM provider timeouts and rate limits gracefully.
5.  **Environment Variables**: Use `pydantic-settings` to manage API keys securely.
6.  **Stateless Design**: Since there is no DB, ensure all necessary state (like conversation history) is passed via the request schema.

## Common Pitfalls

- **Blocking the Event Loop**: Running heavy local model inference on the main thread. (Use `run_in_executor` or separate worker).
- **Insecure API Keys**: Hardcoding keys in the codebase.
- **Large Context Overload**: Not validating the size of input messages, leading to expensive API calls or context window errors.
- **Missing Timeouts**: Waiting indefinitely for an LLM response that might never come.
