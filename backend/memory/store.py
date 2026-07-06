"""
memory/store.py — მარტივი, ფაილზე-დაფუძნებული მეხსიერება Cici-ს აგენტისთვის.

არ ითხოვს ბაზას (Postgres/Redis) — ყოველი სესია ინახება ცალკე JSON
ფაილში `memory/sessions/<session_id>.json`-ში. საკმარისია სანამ
ერთ მანქანაზე მუშაობ; მოგვიანებით ადვილად გადაიტანება SQLite/Redis-ზე
(ინტერფეისი (save_turn/get_history) იგივე დარჩება).
"""

import json
import time
from pathlib import Path

MEMORY_DIR = Path(__file__).parent / "sessions"
MEMORY_DIR.mkdir(exist_ok=True)

MAX_TURNS_IN_CONTEXT = 10  # რამდენი ბოლო შეტყობინება მიეწოდოს მოდელს კონტექსტში


def _session_path(session_id: str) -> Path:
    safe_id = "".join(c for c in session_id if c.isalnum() or c in "-_") or "default"
    return MEMORY_DIR / f"{safe_id}.json"


def save_turn(session_id: str, role: str, content: str) -> None:
    """
    ინახავს ერთ შეტყობინებას (მომხმარებლის ან აგენტის) სესიის ისტორიაში.
    role: "user" | "assistant"
    """
    path = _session_path(session_id)
    history = _load_raw(path)

    history.append({
        "role": role,
        "content": content,
        "timestamp": time.time(),
    })

    path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def get_history(session_id: str, max_turns: int = MAX_TURNS_IN_CONTEXT) -> list[dict]:
    """აბრუნებს ბოლო max_turns შეტყობინებას სესიიდან."""
    path = _session_path(session_id)
    history = _load_raw(path)
    return history[-max_turns:]


def get_history_as_text(session_id: str, max_turns: int = MAX_TURNS_IN_CONTEXT) -> str:
    """ისტორია ფორმატირებული ტექსტად, პირდაპირ prompt-ში ჩასასმელად."""
    turns = get_history(session_id, max_turns)
    lines = []
    for turn in turns:
        speaker = "მომხმარებელი" if turn["role"] == "user" else "Cici"
        lines.append(f"{speaker}: {turn['content']}")
    return "\n".join(lines)


def clear_session(session_id: str) -> None:
    path = _session_path(session_id)
    if path.exists():
        path.unlink()


def _load_raw(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []