"""
orchestrator.py — Cici-ს აგენტის "ტვინი".

ლოგიკა (ReAct-ის მსგავსი მარყუჟი):
  1. მოდელს ვაძლევთ მომხმარებლის კითხვას + სპეციალიზებული ქვე-აგენტების სიას
  2. მოდელი პასუხობს მკაცრი JSON ფორმატით: რომელი ქვე-აგენტი გამოვიძახოთ
  3. ჩვენ ვასრულებთ ქვე-აგენტს (რეალურად, არა მოდელის თავში)
  4. შედეგს ვუბრუნებთ მოდელს კონტექსტში და ვიმეორებთ, სანამ არ გვექნება საბოლოო პასუხი

ეს ამცირებს ჰალუცინაციას: მოდელი პასუხობს არა "მეხსიერებიდან", არამედ
რეალურად მიღებულ ქვე-აგენტების შედეგებზე დაყრდნობით.
"""

import json
import re
from dataclasses import dataclass, field

from services.ollama import ask_ollama
from tools.web_tool import fetch_url
from agents.researcher_agent import research
from agents.coder_agent import run_coder
from agents.planner_agent import make_plan
from memory.store import save_turn, get_history_as_text
from prompts.system_prompts import AGENT_SYSTEM_PROMPT, build_context_prompt

MAX_STEPS = 5
DEFAULT_MODEL = "qwen3:4b"


@dataclass
class AgentStep:
    action: str
    input: dict
    output: str


@dataclass
class AgentResult:
    final_answer: str
    steps: list[AgentStep] = field(default_factory=list)


def _parse_action(raw: str) -> dict:
    """მოდელის პასუხიდან ვაძებთ JSON-ს (ხანდახან ტექსტში გახვეულია)."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"action": "final_answer", "answer": raw.strip()}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"action": "final_answer", "answer": raw.strip()}


async def run_agent(
    user_message: str,
    model: str = DEFAULT_MODEL,
    session_id: str = "default",
) -> AgentResult:
    save_turn(session_id, "user", user_message)

    past_context = get_history_as_text(session_id)
    history = build_context_prompt(AGENT_SYSTEM_PROMPT, past_context, user_message)
    steps: list[AgentStep] = []

    for _ in range(MAX_STEPS):
        raw = ask_ollama(history, model=model)
        decision = _parse_action(raw)
        action = decision.get("action", "final_answer")

        if action == "make_plan":
            request = decision.get("request", user_message)
            plan_steps = await make_plan(request, model=model)
            output = json.dumps(plan_steps, ensure_ascii=False)

        elif action == "delegate_researcher":
            query = decision.get("query", "")
            output = await research(query, model=model)

        elif action == "delegate_coder":
            task = decision.get("task", "")
            result = await run_coder(task, model=model)
            output = json.dumps(result, ensure_ascii=False)

        elif action == "fetch_url":
            url = decision.get("url", "")
            output = await fetch_url(url)

        else:  # final_answer
            answer = decision.get("answer", raw.strip())
            steps.append(AgentStep(action="final_answer", input=decision, output=answer))
            save_turn(session_id, "assistant", answer)
            return AgentResult(final_answer=answer, steps=steps)

        steps.append(AgentStep(action=action, input=decision, output=output))
        history += (
            f"\n\nშენ აირჩიე: {json.dumps(decision, ensure_ascii=False)}"
            f"\nქვე-აგენტის რეალური შედეგი: {output}"
            "\nახლა ან გამოიძახე შემდეგი ქვე-აგენტი, ან თუ საკმარისია, დააბრუნე final_answer. "
            "მხოლოდ JSON."
        )

    fallback = "ვერ მოხერხდა საბოლოო პასუხის მიღება ნაბიჯების ლიმიტში."
    save_turn(session_id, "assistant", fallback)
    return AgentResult(final_answer=fallback, steps=steps)
