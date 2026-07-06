"""
orchestrator.py — Cici-ს აგენტის "ტვინი" (ReAct-ის მსგავსი მარყუჟი).

ლოგიკა:
  1. მოდელს ვაძლევთ მომხმარებლის კითხვას + სპეციალიზებული ქვე-აგენტების სიას
  2. მოდელი პასუხობს მკაცრი JSON ფორმატით: რომელი ქვე-აგენტი გამოვიძახოთ
  3. ჩვენ ვასრულებთ ქვე-აგენტს (რეალურად, არა მოდელის თავში)
  4. შედეგს ვუბრუნებთ მოდელს კონტექსტში და ვიმეორებთ, სანამ არ გვექნება საბოლოო პასუხი

ეს ამცირებს ჰალუცინაციას: მოდელი პასუხობს არა "მეხსიერებიდან", არამედ
რეალურად მიღებულ ქვე-აგენტების შედეგებზე დაყრდნობით.

⚠️ ეს ფაილი მხოლოდ მაშინ ეშვება, თუ API-ის route (api/agent_routes.py)
რეალურად მას იძახებს run_agent()-ის საშუალებით — და არა პირდაპირ Ollama-ს.
"""

import json
import logging
import re
from dataclasses import dataclass, field

from agents.coder_agent import run_coder
from agents.openhands_agent import run_openhands
from agents.planner_agent import make_plan
from agents.researcher_agent import research
from config import DEFAULT_MODEL, MAX_STEPS
from memory.store import get_history_as_text, save_turn
from prompts.system_prompts import AGENT_SYSTEM_PROMPT, build_context_prompt
from services.ollama import ask_ollama
from tools.web_tool import fetch_url

logger = logging.getLogger("cici.orchestrator")


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


async def _execute_action(action: str, decision: dict, model: str) -> str:
    """
    ერთი ნაბიჯის რეალურად შესრულება. განზრახ გამოცალკევებულია run_agent-სგან
    და try/except-ითაა დაცული: ერთი ხელსაწყოს ჩავარდნამ (მაგ. ქსელის
    შეცდომა web_search-ში) მთელი agent loop არ უნდა ჩამოაგდოს — model-მა
    უნდა დაინახოს რეალური შეცდომა და თვითონ გადაწყვიტოს რა გააკეთოს შემდეგ.
    """
    try:
        if action == "make_plan":
            request = decision.get("request", "")
            plan_steps = await make_plan(request, model=model)
            return json.dumps(plan_steps, ensure_ascii=False)

        if action == "delegate_researcher":
            query = decision.get("query", "")
            return await research(query, model=model)

        if action == "delegate_coder":
            task = decision.get("task", "")
            result = await run_coder(task, model=model)
            return json.dumps(result, ensure_ascii=False)

        if action == "delegate_openhands":
            task = decision.get("task", "")
            repo_url = decision.get("repo_url")
            result = await run_openhands(task, repo_url=repo_url)
            return json.dumps(result, ensure_ascii=False)

        if action == "fetch_url":
            url = decision.get("url", "")
            return await fetch_url(url)

        return f"უცნობი action: '{action}'. გამოიყენე მხოლოდ სისტემურ prompt-ში ჩამოთვლილი action-ები."

    except Exception as e:  # noqa: BLE001 — განზრახ ფართო: ნებისმიერი tool-ის ჩავარდნა უნდა დაიჭიროს
        logger.exception("Tool execution failed for action=%s", action)
        return f"ხელსაწყომ ('{action}') გამოიწვია რეალური შეცდომა: {e}"


async def run_agent(
    user_message: str,
    model: str = DEFAULT_MODEL,
    session_id: str = "default",
) -> AgentResult:
    save_turn(session_id, "user", user_message)

    past_context = get_history_as_text(session_id)
    history = build_context_prompt(AGENT_SYSTEM_PROMPT, past_context, user_message)
    steps: list[AgentStep] = []

    for step_num in range(1, MAX_STEPS + 1):
        raw = await ask_ollama(history, model=model)
        decision = _parse_action(raw)
        action = decision.get("action", "final_answer")

        if action == "final_answer":
            answer = decision.get("answer", raw.strip())
            steps.append(AgentStep(action="final_answer", input=decision, output=answer))
            save_turn(session_id, "assistant", answer)
            return AgentResult(final_answer=answer, steps=steps)

        output = await _execute_action(action, decision, model)
        steps.append(AgentStep(action=action, input=decision, output=output))

        logger.info("[%s] ნაბიჯი %d/%d: %s", session_id, step_num, MAX_STEPS, action)

        history += (
            f"\n\nშენ აირჩიე: {json.dumps(decision, ensure_ascii=False)}"
            f"\nქვე-აგენტის რეალური შედეგი: {output}"
            "\nახლა ან გამოიძახე შემდეგი ქვე-აგენტი, ან თუ საკმარისია, დააბრუნე final_answer. "
            "მხოლოდ JSON."
        )

    fallback = "ვერ მოხერხდა საბოლოო პასუხის მიღება ნაბიჯების ლიმიტში (MAX_STEPS). სცადე მოთხოვნის გამარტივება."
    save_turn(session_id, "assistant", fallback)
    return AgentResult(final_answer=fallback, steps=steps)
