"""
tools/openhands_tool.py — კავშირი დამოუკიდებელ OpenHands Agent Server-თან
(https://github.com/OpenHands/OpenHands).

რატომ OpenHands ცალკეა code_tool.py-სგან:
  - code_tool.py (self_correcting_run) წერს და უშვებს ᲛᲝᲙᲚᲔ, დამოუკიდებელ
    python სკრიპტს ერთ subprocess-ში — კარგია გამოთვლებისთვის, უბრალო
    ამოცანებისთვის, მარტივი ავტომატიზაციისთვის.
  - OpenHands არის სრული საინჟინრო აგენტი: მუშაობს რეალურ ფაილურ სისტემაზე
    (ან რეპოზიტორიაზე), გახსნის/ჩაწერს მრავალ ფაილს, გაუშვებს ტესტებს,
    თავად გაასწორებს თავის კოდს ბევრ იტერაციაში. სჭირდება მხოლოდ მაშინ,
    როცა ამოცანა სცდება ერთი სკრიპტის ფარგლებს (refactor, bug fix
    კონკრეტულ repo-ში, ახალი ფუნქციონალის დამატება არსებულ პროექტში).

წინაპირობა: OpenHands Agent Server ცალკე, დამოუკიდებლად უნდა გქონდეს
გაშვებული (docker-ით) — ეს ფაილი მხოლოდ მასთან HTTP საუბრობს, თავად
OpenHands-ს არ უშვებს. იხ. README-ს "OpenHands ინტეგრაცია" სექცია
დაყენების ინსტრუქციისთვის.

.env-ში საჭირო ცვლადები:
    OPENHANDS_ENABLED=true
    OPENHANDS_BASE_URL=http://127.0.0.1:3000
    OPENHANDS_API_KEY=...   (თუ შენი დაყენება ითხოვს)

⚠️ მნიშვნელოვანი: OpenHands-ის REST API-ს endpoint-ების სქემა დროთა
განმავლობაში იცვლება (მაგ. 2026 დასაწყისში v0 → v1 გადასვლა მოხდა).
თუ ეს ფაილი შენს კონკრეტულ დაყენებულ ვერსიასთან არ მუშაობს, გადაამოწმე
START_ENDPOINT/სტატუსის ველების სახელები აქ ოფიციალურ დოკუმენტაციასთან
(https://docs.openhands.dev) მიმართებაში — თავად HTTP პოლინგის ლოგიკა
უცვლელი დარჩება.
"""

import asyncio

import httpx

from config import (
    OPENHANDS_API_KEY,
    OPENHANDS_BASE_URL,
    OPENHANDS_ENABLED,
    OPENHANDS_TIMEOUT,
)

START_ENDPOINT = "/api/conversations"
POLL_INTERVAL_SECONDS = 3
DONE_STATUSES = {"finished", "completed", "stopped", "error"}


def _headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if OPENHANDS_API_KEY:
        headers["Authorization"] = f"Bearer {OPENHANDS_API_KEY}"
    return headers


async def run_openhands_task(task: str, repo_url: str | None = None) -> dict:
    """
    უშვებს ერთ ავტონომიურ OpenHands საინჟინრო ამოცანას და ელოდება მის
    დასრულებას (polling).

    აბრუნებს: {"success": bool, "result": str, "conversation_id": str | None}
    """
    if not OPENHANDS_ENABLED:
        return {
            "success": False,
            "result": (
                "OpenHands ინტეგრაცია გამორთულია. ჩართე .env-ში "
                "OPENHANDS_ENABLED=true და დარწმუნდი, რომ OpenHands "
                "Agent Server გაშვებულია (README, 'OpenHands ინტეგრაცია')."
            ),
            "conversation_id": None,
        }

    payload: dict = {"initial_user_msg": task}
    if repo_url:
        payload["repository"] = repo_url

    async with httpx.AsyncClient(
        base_url=OPENHANDS_BASE_URL, headers=_headers(), timeout=30.0
    ) as client:
        try:
            start_resp = await client.post(START_ENDPOINT, json=payload)
            start_resp.raise_for_status()
        except httpx.HTTPError as e:
            return {
                "success": False,
                "result": f"OpenHands-თან დაკავშირება ვერ მოხერხდა: {e}",
                "conversation_id": None,
            }

        start_data = start_resp.json()
        conversation_id = start_data.get("conversation_id") or start_data.get("id")

        if not conversation_id:
            return {
                "success": False,
                "result": f"OpenHands-მა მოულოდნელი პასუხი დააბრუნა: {start_data}",
                "conversation_id": None,
            }

        elapsed = 0.0
        while elapsed < OPENHANDS_TIMEOUT:
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
            elapsed += POLL_INTERVAL_SECONDS

            try:
                status_resp = await client.get(f"{START_ENDPOINT}/{conversation_id}")
                status_resp.raise_for_status()
            except httpx.HTTPError:
                continue  # დროებითი ქსელური ბზარი — ვცდით კვლავ შემდეგ იტერაციაზე

            status_data = status_resp.json()
            status = status_data.get("status")

            if status in DONE_STATUSES:
                return {
                    "success": status in ("finished", "completed"),
                    "result": (
                        status_data.get("summary")
                        or status_data.get("last_message")
                        or str(status_data)
                    ),
                    "conversation_id": conversation_id,
                }

        return {
            "success": False,
            "result": (
                f"OpenHands ამოცანამ ვერ დაასრულა {int(OPENHANDS_TIMEOUT)}წმ-ში "
                f"(conversation_id={conversation_id}). გაზარდე OPENHANDS_TIMEOUT "
                "თუ ამოცანა ნამდვილად რთულია."
            ),
            "conversation_id": conversation_id,
        }
