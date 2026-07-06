"""
services/ollama.py — ერთადერთი, გაერთიანებული Ollama კლიენტი.

ადრე ორი ცალკეული ფაილი არსებობდა:
  - services/ollama.py         (sync, urllib, orchestrator/agents იყენებდნენ)
  - services/ollama_service.py (async, httpx, api/agent_routes.py იყენებდა)

ეს ორი, ერთმანეთისგან დამოუკიდებელი კოდი, სხვადასხვა default მოდელით და
timeout-ით — სწორედ ერთ-ერთი მიზეზი იყო, რის გამოც API-ს და "ტვინს"
(orchestrator) შორის კავშირი დაშლილი იყო. ახლა ორივე მომხმარებელი ერთსა
და იმავე, კონფიგურირებად, async ფუნქციას იძახებს.
"""

import httpx

from config import DEFAULT_MODEL, OLLAMA_TIMEOUT, OLLAMA_URL


async def ask_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    უგზავნის prompt-ს Ollama-ს /api/generate endpoint-ს და აბრუნებს
    სუფთა ტექსტურ პასუხს (string).

    ყოველთვის async — orchestrator-ის ReAct loop-ში sync/ბლოკირებადი
    ქსელური გამოძახება event loop-ს გააჩერებდა.
    """
    url = f"{OLLAMA_URL.rstrip('/')}/api/generate"

    async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
        try:
            response = await client.post(
                url,
                json={"model": model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            return (
                f"შეცდომა: Ollama-სთან დაკავშირება ვერ მოხერხდა ({e}). "
                "დარწმუნდი, რომ 'ollama serve' გაშვებულია და OLLAMA_URL სწორია."
            )

    data = response.json()
    return data.get("response") or data.get("message") or data.get("content") or str(data)
