"""
web_tool.py — ვებ-წვდომის ინსტრუმენტი Cici-ს აგენტისთვის.

ორი ფუნქცია:
  - web_search(query)  -> ვეძებთ DuckDuckGo-ს HTML ვერსიაზე (API key არ სჭირდება)
  - fetch_url(url)     -> ვხსნით კონკრეტულ გვერდს და ვბრუნებთ სუფთა ტექსტს

დამოკიდებულებები: httpx, beautifulsoup4
    pip install httpx beautifulsoup4 --break-system-packages
"""

import httpx
from bs4 import BeautifulSoup

from config import WEB_MAX_RESULTS, WEB_TIMEOUT_SECONDS

SEARCH_URL = "https://html.duckduckgo.com/html/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CiciAgent/1.0)"
}
TIMEOUT = WEB_TIMEOUT_SECONDS


async def web_search(query: str, max_results: int = WEB_MAX_RESULTS) -> list[dict]:
    """
    აბრუნებს სიას: [{"title": ..., "url": ..., "snippet": ...}, ...]
    """
    async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS, follow_redirects=True) as client:
        resp = await client.post(SEARCH_URL, data={"q": query})
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    for result in soup.select(".result")[:max_results]:
        title_tag = result.select_one(".result__a")
        snippet_tag = result.select_one(".result__snippet")

        if not title_tag:
            continue

        url = title_tag.get("href", "")
        title = title_tag.get_text(strip=True)
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

        results.append({"title": title, "url": url, "snippet": snippet})

    return results


async def fetch_url(url: str, max_chars: int = 4000) -> str:
    """
    ხსნის კონკრეტულ URL-ს და აბრუნებს გასუფთავებულ ტექსტს (script/style ამოღებულია).
    max_chars -- რამდენი სიმბოლო დაუბრუნდეს მოდელს (კონტექსტის დასაზოგად).
    """
    async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS, follow_redirects=True) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    lines = [line for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)

    if len(clean_text) > max_chars:
        clean_text = clean_text[:max_chars] + "\n...[შეკვეცილია]"

    return clean_text