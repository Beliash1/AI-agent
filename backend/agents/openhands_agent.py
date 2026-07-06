"""
agents/openhands_agent.py — orchestrator-ისთვის ერთგვაროვანი ინტერფეისი
OpenHands ქვე-აგენტთან (რეალურ ლოგიკას tools/openhands_tool.py ინახავს).

იგივე პატერნი, რაც coder_agent.py/researcher_agent.py-ში: "agents" შრე
მხოლოდ ცხადყოფს ამ ხელსაწყოს orchestrator-ისთვის, ისე რომ ყველა ქვე-აგენტი
ერთნაირად (async ფუნქცია → dict/str შედეგი) გამოიძახებოდეს.
"""

from tools.openhands_tool import run_openhands_task


async def run_openhands(task: str, repo_url: str | None = None) -> dict:
    """
    აბრუნებს: {"success": bool, "result": str, "conversation_id": str | None}
    """
    return await run_openhands_task(task, repo_url=repo_url)
