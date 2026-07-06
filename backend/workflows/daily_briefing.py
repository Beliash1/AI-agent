"""
workflows/daily_briefing.py — მაგალითი, კონკრეტული workflow-ს დასაწერად.

ეს ფაილი აჩვენებს, როგორ შეიძლება საკუთარი, ფიქსირებული სცენარის აწყობა
runner.py-ის base-ზე. თავისუფლად ჩაანაცვლე query-ები შენი საჭიროებით,
ან დაამატე ახალი ნაბიჯები.

გაშვება: python -m backend.workflows.daily_briefing
"""

import asyncio

from .runner import run_workflow


DAILY_BRIEFING_STEPS = [
    {"type": "research", "query": "ბოლო AI სიახლეები დღეს"},
    {"type": "research", "query": "დღევანდელი USD/GEL კურსი"},
]


async def run_daily_briefing() -> str:
    result = await run_workflow(DAILY_BRIEFING_STEPS)
    return result.summary_text()


if __name__ == "__main__":
    summary = asyncio.run(run_daily_briefing())
    print(summary)
