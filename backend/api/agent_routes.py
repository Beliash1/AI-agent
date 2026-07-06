from fastapi import APIRouter
from pydantic import BaseModel
from services.ollama_service import ollama_generate

router = APIRouter()

class AgentRequest(BaseModel):
    prompt: str | None = None
    message: str | None = None
    input: str | None = None
    text: str | None = None
    model: str = "qwen3:8b"  # default model

@router.post("/agent")
async def agent(req: AgentRequest):
    # აირჩიე პირველი non‑null ველი
    prompt = req.prompt or req.message or req.input or req.text

    if not prompt:
        return {"error": "No prompt provided"}

    answer = await ollama_generate(prompt, req.model)
    return {"response": answer}
