import uuid
from typing import Dict

import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.core.config import settings
from app.services.llm_service import LLMService

app = FastAPI(
    title="LLM Experimentation Platform",
    description="A platform for experimenting with LLMs using Ollama",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

llm_service = LLMService()


@app.get("/")
async def root():
    return {
        "message": "Welcome to the LLM Experimentation Platform",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.get("/health")
async def health_check() -> Dict:
    """Health check endpoint that verifies Ollama connection and model availability."""
    try:
        # Check Ollama API
        ollama_url = f"http://{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}/api/tags"
        response = requests.get(ollama_url, timeout=5)
        response.raise_for_status()

        # Check if our default model is available
        models = [model["name"] for model in response.json().get("models", [])]
        model_status = settings.DEFAULT_MODEL in models

        return {
            "status": "healthy",
            "ollama_status": "connected",
            "default_model_available": model_status,
            "default_model": settings.DEFAULT_MODEL,
        }
    except requests.RequestException as e:
        return {"status": "unhealthy", "error": str(e), "ollama_status": "disconnected"}


@app.on_event("startup")
async def startup_event():
    """Verify Ollama connection and pull the default model if not available."""
    try:
        health_status = await health_check()
        if not health_status.get("default_model_available"):
            # Pull the default model
            ollama_url = (
                f"http://{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}/api/pull"
            )
            response = requests.post(
                ollama_url,
                json={"name": settings.DEFAULT_MODEL},
                timeout=300,  # Allow 5 minutes for model download
            )
            response.raise_for_status()
    except Exception as e:
        print(f"Startup check failed: {str(e)}")
        # Don't raise the error - let the app start anyway
        # The health check endpoint will show the actual status


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    conversation_id = None
    session_id = None
    user_id = None
    try:
        while True:
            data = await websocket.receive_json()
            prompt = data.get("prompt")
            model = data.get("model")
            temperature = data.get("temperature")
            max_tokens = data.get("max_tokens")
            system_prompt = data.get("system_prompt")
            context = data.get("context")
            session_id = data.get("session_id") or session_id or str(uuid.uuid4())
            user_id = data.get("user_id") or user_id
            conversation_id = data.get("conversation_id") or conversation_id
            use_training_context = data.get("use_training_context", False)

            # If no conversation_id, create one in Django
            if not conversation_id:
                try:
                    conv_resp = requests.post(
                        f"http://{settings.DJANGO_ADMIN_HOST}:{settings.DJANGO_ADMIN_PORT}/chat/conversations/create/",
                        json={
                            "title": "Web Chat",
                            "session_id": session_id,
                            "user_id": user_id,
                        },
                        timeout=5,
                    )
                    if conv_resp.status_code == 201:
                        conversation_id = conv_resp.json().get("id")
                except Exception as e:
                    await websocket.send_json(
                        {"error": f"Failed to create conversation: {str(e)}"}
                    )
                    continue

            try:
                result = llm_service.generate_response(
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_prompt,
                    context=context,
                    session_id=session_id,
                    user_id=user_id,
                    use_training_context=use_training_context,
                    conversation_id=conversation_id,
                )
                # Log interaction to Django with conversation
                try:
                    admin_url = f"http://{settings.DJANGO_ADMIN_HOST}:{settings.DJANGO_ADMIN_PORT}/chat/llm-interactions/log/"
                    llm_data = {
                        "prompt": prompt,
                        "response": result["message"]["content"],
                        "model_name": model,
                        "temperature": temperature,
                        "top_p": None,
                        "frequency_penalty": None,
                        "presence_penalty": None,
                        "context": context,
                        "retrieved_documents": None,
                        "streamed": False,
                        "session_id": session_id,
                        "user": user_id,
                        "conversation": conversation_id,
                    }
                    requests.post(admin_url, json=llm_data, timeout=5)
                except Exception:
                    pass  # Don't block user on logging error
                await websocket.send_json(
                    {
                        "response": result["message"]["content"],
                        "model": result["model"],
                        "usage": result.get("usage", {}),
                        "conversation_id": conversation_id,
                        "session_id": session_id,
                    }
                )
            except Exception as e:
                await websocket.send_json({"error": str(e)})
    except WebSocketDisconnect:
        pass
