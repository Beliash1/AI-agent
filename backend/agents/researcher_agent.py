"""
agents/researcher_agent.py — სპეციალიზებული ქვე-აგენტი კვლევისთვის.

აკეთებს ორ რამეს ერთად: ვებ ძებნას და შედეგების ფაქტობრივ შეჯამებას,
ისე რომ მოდელმა არაფერი არ "მოიგონოს" რასაც ძებნის შედეგებში ვერ ხედავს.
"""

import json

from services.ollama import ask_ollama
from tools.web_tool import web_search
from prompts.system_prompts import RESEARCHER_AGENT_PROMPT


async def research(query: str, model: str = "qwen3:4b") -> str:
    results = await web_search(query)

    if not results:
        return f"ვერაფერი ვიპოვე '{query}'-ზე ვებ ძებნით."

    results_text = json.dumps(results, ensure_ascii=False, indent=2)
    prompt = (
        f"{RESEARCHER_AGENT_PROMPT}\n\n"
        f"ძებნის რეალური შედეგები:\n{results_text}\n\n"
        f"კითხვა: {query}"
    )
    return await ask_ollama(prompt, model=model)
