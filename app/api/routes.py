from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.llm_service import LLMService, Message

router = APIRouter()
llm_service = LLMService()


class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    context: Optional[List[Message]] = None
    session_id: Optional[str] = None
    user_id: Optional[int] = None


class GenerateResponse(BaseModel):
    response: str
    model: str
    usage: dict


@router.post("/generate", response_model=GenerateResponse)
async def generate_response(request: GenerateRequest):
    try:
        result = llm_service.generate_response(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt,
            context=request.context,
            session_id=request.session_id,
            user_id=request.user_id,
        )
        return GenerateResponse(
            response=result["message"]["content"],
            model=result["model"],
            usage=result.get("usage", {}),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=List[str])
async def list_models():
    try:
        return llm_service.list_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_name}/pull")
async def pull_model(model_name: str):
    try:
        return llm_service.pull_model(model_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def api_health_check():
    from app.main import health_check

    return await health_check()
