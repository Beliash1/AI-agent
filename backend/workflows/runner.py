"""
workflows/runner.py — ავტომატური, წინასწარ განსაზღვრული სცენარების გამშვები.

განსხვავება orchestrator.py-სგან: orchestrator ყოველ ჯერზე მოდელს
ეკითხება "რა გავაკეთო შემდეგ", ხოლო workflow — ეს არის ᲬᲘᲜᲐᲡᲬᲐᲠ ცნობილი,
ფიქსირებული ნაბიჯების მიმდევრობა (მაგ. "ყოველ დილას გააკეთე ეს სამი რამ").
გამოსადეგია განმეორებადი, cron-ისნაირი ამოცანებისთვის.

ნაბიჯის ტიპები:
  {"type": "research", "query": "..."}
  {"type": "code", "task": "..."}
  {"type": "fetch_url", "url": "..."}
"""

import json
from dataclasses import dataclass, field

from ..agents.researcher_agent import research
from ..agents.coder_agent import run_coder
from ..tools.web_tool import fetch_url


@dataclass
class WorkflowStepResult:
    type: str
    input: dict
    output: str


@dataclass
class WorkflowResult:
    steps: list[WorkflowStepResult] = field(default_factory=list)

    def summary_text(self) -> str:
        lines = []
        for i, s in enumerate(self.steps, start=1):
            lines.append(f"[{i}] {s.type}: {s.output}")
        return "\n\n".join(lines)


async def run_workflow(steps: list[dict], model: str = "qwen3:4b") -> WorkflowResult:
    """
    ასრულებს ნაბიჯებს თანმიმდევრობით და აბრუნებს ყველა შედეგს ერთად.
    ნაბიჯებს შორის შეცდომა არ აჩერებს მთელ workflow-ს — გაგრძელდება
    შემდეგ ნაბიჯზე, შეცდომა კი output-ში აისახება.
    """
    result = WorkflowResult()

    for step in steps:
        step_type = step.get("type")

        try:
            if step_type == "research":
                output = await research(step.get("query", ""), model=model)

            elif step_type == "code":
                run_result = await run_coder(step.get("task", ""), model=model)
                output = json.dumps(run_result, ensure_ascii=False)

            elif step_type == "fetch_url":
                output = await fetch_url(step.get("url", ""))

            else:
                output = f"უცნობი ნაბიჯის ტიპი: {step_type}"

        except Exception as e:
            output = f"შეცდომა ამ ნაბიჯზე: {e}"

        result.steps.append(WorkflowStepResult(type=step_type, input=step, output=output))

    return result
