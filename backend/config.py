"""
config.py — ერთი ცენტრალური ადგილი ყველა კონფიგურაციისთვის.

ადრე მისამართები (Ollama URL და ა.შ.) hardcoded იყო რამდენიმე ფაილში
ცალ-ცალკე (services/ollama.py, services/ollama_service.py, core/setting.py) —
ერთმანეთისგან დამოუკიდებლად, ზოგჯერ სხვადასხვა მნიშვნელობით. ეს ცვლადები
ახლა აქედან იკითხება ყველგან.

გარემოს ცვლადები იტვირთება რეპოს root-ში მდებარე .env ფაილიდან
(იხ. .env.example ნიმუშისთვის). თუ .env არ არსებობს, ქვემოთ მოცემული
default მნიშვნელობები გამოიყენება.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    # repo root/.env — ეს ფაილი ორი დონით ზემოთაა (backend/config.py -> repo root)
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    # python-dotenv არასავალდებულოა: თუ არ დაყენდა, უბრალოდ
    # სისტემურ გარემოს ცვლადებზე (ან default-ებზე) ვეყრდნობით.
    pass


def _get_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


# --- Ollama (ლოკალური LLM) ---
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen3:4b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "300"))

# --- Agent loop (orchestrator.py) ---
MAX_STEPS = int(os.getenv("MAX_STEPS", "5"))

# --- Memory (memory/store.py) ---
MAX_TURNS_IN_CONTEXT = int(os.getenv("MAX_TURNS_IN_CONTEXT", "10"))

# --- Code tool (tools/code_tool.py) ---
CODE_TIMEOUT_SECONDS = int(os.getenv("CODE_TIMEOUT_SECONDS", "10"))
CODE_MAX_RETRIES = int(os.getenv("CODE_MAX_RETRIES", "3"))

# --- Web tool (tools/web_tool.py) ---
WEB_TIMEOUT_SECONDS = float(os.getenv("WEB_TIMEOUT_SECONDS", "15"))
WEB_MAX_RESULTS = int(os.getenv("WEB_MAX_RESULTS", "5"))

# --- OpenHands (რთული, მრავალფაილიანი საინჟინრო ამოცანებისთვის) ---
# იხ. backend/tools/openhands_tool.py და README-ს "OpenHands ინტეგრაცია" სექცია.
OPENHANDS_ENABLED = _get_bool("OPENHANDS_ENABLED", False)
OPENHANDS_BASE_URL = os.getenv("OPENHANDS_BASE_URL", "http://127.0.0.1:3000")
OPENHANDS_API_KEY = os.getenv("OPENHANDS_API_KEY", "")
OPENHANDS_TIMEOUT = float(os.getenv("OPENHANDS_TIMEOUT", "600"))

# --- CORS / frontend ---
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
