from langchain.chat_models import init_chat_model

from config import GROQ_MODEL
from logger import log_supervisor, timer

SUPERVISOR_PROMPT = """You are a Supervisor that validates AI assistant responses for accuracy.

You will receive:
1. The user's original question
2. The user's known context (home location, preferences — this is NOT fabricated)
3. Tool outputs (the evidence/data collected)
4. The assistant's draft response

Your job: check if TOOL-SOURCED claims in the response match the actual tool outputs.
- Temperatures, precipitation, snowfall numbers must match tool data.
- Place names, categories, and addresses must come from tool results.
- The assistant mentioning the user's home location or preferences is FINE — that comes 
  from user context, not tools. Do NOT flag it.
- General travel advice and knowledge is FINE — only flag fabricated SPECIFIC data 
  (numbers, place names, ratings) that should have come from tools but didn't.

If no tools were used, PASS.

Respond with EXACTLY this format:
VERDICT: PASS or FAIL
REASON: Brief explanation (one sentence)
"""


_supervisor_model = None


def _get_model():
    global _supervisor_model
    if _supervisor_model is None:
        _supervisor_model = init_chat_model(
            GROQ_MODEL, model_provider="groq", temperature=0
        )
    return _supervisor_model


def run_supervisor(
    user_message: str,
    tool_outputs: list[dict],
    agent_response: str,
    user_context: str = "",
) -> dict:
    """Validate the agent's response against tool evidence.

    Returns dict with keys: passed (bool), verdict (str), reason (str)
    """
    if not tool_outputs:
        log_supervisor("PASS", "No tools were used — conversational response", 0)
        return {"passed": True, "verdict": "PASS", "reason": "No tools used"}

    tool_evidence = "\n\n".join(
        f"Tool: {t['name']}\nInput: {t['input']}\nOutput: {t['output']}"
        for t in tool_outputs
    )

    check_prompt = (
        f"USER QUESTION:\n{user_message}\n\n"
        f"USER CONTEXT (known, not fabricated):\n{user_context}\n\n"
        f"TOOL EVIDENCE:\n{tool_evidence}\n\n"
        f"ASSISTANT RESPONSE:\n{agent_response}\n\n"
        f"Are the tool-sourced claims in the response grounded in the tool evidence?"
    )

    with timer() as t:
        model = _get_model()
        result = model.invoke([
            {"role": "system", "content": SUPERVISOR_PROMPT},
            {"role": "user", "content": check_prompt},
        ])

    response_text = result.content.strip()
    verdict = "PASS"
    reason = ""

    for line in response_text.split("\n"):
        line = line.strip()
        if line.upper().startswith("VERDICT:"):
            verdict = line.split(":", 1)[1].strip().upper()
        elif line.upper().startswith("REASON:"):
            reason = line.split(":", 1)[1].strip()

    passed = verdict == "PASS"
    log_supervisor(verdict, reason, t["elapsed_ms"])

    return {"passed": passed, "verdict": verdict, "reason": reason}
