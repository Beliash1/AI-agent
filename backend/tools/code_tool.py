"""
code_tool.py — კოდის შესრულება + თვითშემოწმების (self-correction) მარყუჟი.

run_python_code(code)      -> უსაფრთხოდ (subprocess + timeout) უშვებს კოდს, აბრუნებს stdout/stderr
self_correcting_run(task)  -> სთხოვს მოდელს კოდის დაწერას, უშვებს, შეცდომის შემთხვევაში
                               უბრუნებს ტრასბექს მოდელს გასასწორებლად, მაქს N ჯერ

ჰალუცინაციის რისკის შემცირება: მოდელი ვერაფერს "იგონებს" შედეგზე —
რეალურ stdout/stderr-ს ვუბრუნებთ ყოველ იტერაციაზე, ასე რომ პასუხი
ყოველთვის რეალურ შესრულებაზეა დაფუძნებული, არა მოდელის ვარაუდზე.
"""

import re
import subprocess
import tempfile
import os
from dataclasses import dataclass

from services.ollama import ask_ollama

TIMEOUT_SECONDS = 10
MAX_RETRIES = 3


@dataclass
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    code: str


def run_python_code(code: str) -> ExecutionResult:
    """
    უშვებს python კოდს იზოლირებულ subprocess-ში, timeout-ით.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name

    try:
        proc = subprocess.run(
            ["python3", path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        return ExecutionResult(
            success=(proc.returncode == 0),
            stdout=proc.stdout,
            stderr=proc.stderr,
            code=code,
        )
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            success=False,
            stdout="",
            stderr=f"დრო ამოიწურა ({TIMEOUT_SECONDS}წმ) — შესაძლოა უსასრულო ციკლია.",
            code=code,
        )
    finally:
        os.unlink(path)


def _extract_code_block(text: str) -> str:
    """LLM პასუხიდან ამოღებს ```python ... ``` ბლოკს, ან თუ არ არის — მთელ ტექსტს."""
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


async def self_correcting_run(task_description: str, model: str = "qwen3:4b") -> dict:
    """
    1) სთხოვს მოდელს დაწეროს კოდი task_description-ის მიხედვით
    2) უშვებს კოდს
    3) თუ შეცდომაა — უბრუნებს რეალურ stderr-ს მოდელს გასასწორებლად
    4) მაქს MAX_RETRIES ჯერ იმეორებს

    აბრუნებს: {"success": bool, "code": str, "output": str, "attempts": int}
    """
    prompt = (
        f"დაწერე python კოდი შემდეგი ამოცანისთვის: {task_description}\n"
        "დააბრუნე მხოლოდ კოდი ```python ... ``` ბლოკში, დამატებითი ახსნის გარეშე."
    )

    last_result = None

    for attempt in range(1, MAX_RETRIES + 1):
        llm_response = await ask_ollama(prompt, model=model)
        code = _extract_code_block(llm_response)

        result = run_python_code(code)
        last_result = result

        if result.success:
            return {
                "success": True,
                "code": code,
                "output": result.stdout,
                "attempts": attempt,
            }

        # შეცდომა იყო — ვუბრუნებთ რეალურ ტრასბექს, არა ვარაუდს
        prompt = (
            f"ეს კოდი:\n```python\n{code}\n```\n"
            f"შესრულებისას გამოიწვია ეს რეალური შეცდომა:\n{result.stderr}\n"
            "გაასწორე კოდი ისე, რომ ეს კონკრეტული შეცდომა აღარ განმეორდეს. "
            "დააბრუნე მხოლოდ გასწორებული კოდი ```python ... ``` ბლოკში."
        )

    return {
        "success": False,
        "code": last_result.code if last_result else "",
        "output": last_result.stderr if last_result else "უცნობი შეცდომა",
        "attempts": MAX_RETRIES,
    }