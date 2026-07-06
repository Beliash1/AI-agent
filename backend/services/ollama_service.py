import httpx

async def ollama_generate(prompt: str, model: str):
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "think": False,
            }
        )

    data = response.json()

    text = (
        data.get("response")
        or data.get("message")
        or data.get("content")
        or str(data)
    )

    return {"response": text}
