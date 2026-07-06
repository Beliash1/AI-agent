"""
agents/coder_agent.py — სპეციალიზებული ქვე-აგენტი კოდის დაწერა/გასწორებისთვის.

რეალურ ლოგიკას tools/code_tool.py ინახავს (subprocess + self-correction) —
ეს ფაილი მხოლოდ "agents" შრეზე ცხადყოფს მას, რომ orchestrator-მა
ერთნაირად შეძლოს ყველა ქვე-აგენტთან მუშაობა (researcher/coder/planner).
"""

from config import DEFAULT_MODEL
from tools.code_tool import self_correcting_run


async def run_coder(task: str, model: str = DEFAULT_MODEL) -> dict:
    """
    აბრუნებს: {"success": bool, "code": str, "output": str, "attempts": int}
    """
    return await self_correcting_run(task, model=model)
