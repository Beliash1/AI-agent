"""
api/agent_routes.py — HTTP შრე Cici-ს ტვინთან (core/orchestrator.py).

ᲛᲜᲘᲨᲕᲜᲔᲚᲝᲕᲐᲜᲘ: ადრე ეს ფაილი ორქესტრატორს საერთოდ არ იძახებდა — პირდაპირ
Ollama-ს (services/ollama_service.py) მიმართავდა, prompt→პასუხის ლოგიკით.
ეს ნიშნავდა, რომ orchestrator.py-ში აწყობილი მთელი "ტვინი" (ReAct loop,
ქვე-აგენტები, მეხსიერება) რეალურად არასდროს ეშვებოდა. ახლა /agent
route რეალურად run_agent()-ს იძახებს.
"""

from dataclasses import asdict

from fastapi import APIRouter
from pydantic import BaseModel

from config import DEFAULT_MODEL
from core.orchestrator import run_agent
from memory.store import clear_session

router = APIRouter()


class AgentRequest(BaseModel):
    # frontend (App.jsx) "message"-ს გზავნის, დანარჩენი alias-ებია
    # თავსებადობისთვის სხვადასხვა client-თან/მოსახერხებელი ტესტირებისთვის.
    prompt: str | None = None
    message: str | None = None
    input: str | None = None
    text: str | None = None
    model: str = DEFAULT_MODEL
    session_id: str = "default"


@router.post("/agent")
async def agent(req: AgentRequest):
    user_message = req.message or req.prompt or req.input or req.text

    if not user_message:
        return {"error": "შეტყობინება არ არის მოწოდებული (message/prompt/input/text)."}

    result = await run_agent(
        user_message=user_message,
        model=req.model,
        session_id=req.session_id,
    )

    return {
        "answer": result.final_answer,
        # "response"-იც ვაბრუნებთ frontend-ის fallback-თან თავსებადობისთვის
        # (lib/api.js და App.jsx ორივეს ეძებენ).
        "response": result.final_answer,
        "steps": [asdict(step) for step in result.steps],
    }


@router.delete("/agent/session/{session_id}")
async def clear_agent_session(session_id: str):
    """frontend-ს აძლევს საშუალებას გაასუფთაოს კონკრეტული სესიის მეხსიერება
    (მაგ. "ახალი საუბრის დაწყება" ღილაკზე)."""
    clear_session(session_id)
    return {"cleared": session_id}
