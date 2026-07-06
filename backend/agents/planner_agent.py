"""
agents/planner_agent.py — რთულ მოთხოვნას ანაწილებს თანმიმდევრულ ნაბიჯებად.

გამოიყენება, როცა მომხმარებლის მოთხოვნა ერთზე მეტ ქმედებას მოითხოვს
(მაგ. "მოძებნე X და გამომითვალე Y და დამიწერე Z").
"""

import json
import re

from services.ollama import ask_ollama
from prompts.system_prompts import PLANNER_AGENT_PROMPT


async def make_plan(user_message: str, model: str = "qwen3:4b") -> list[str]:
    prompt = f"{PLANNER_AGENT_PROMPT}\n\nმომხმარებლის მოთხოვნა: {user_message}"
    raw = await ask_ollama(prompt, model=model)

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            steps = data.get("steps")
            if isinstance(steps, list) and steps:
                return steps
        except json.JSONDecodeError:
            pass

    # თუ დაგეგმვა ვერ დაიშალა, ვასრულებთ როგორც ერთ ნაბიჯს
    return [user_message]
