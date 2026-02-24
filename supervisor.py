from langchain.chat_models import init_chat_model

from logger import log_supervisor, timer

SUPERVISOR_MODEL = "llama-3.1-8b-instant"

SUPERVISOR_PROMPT = """You check if an assistant fabricated specific data that should have come from tools.

ONLY FAIL if the assistant invented specific numbers (temperatures, precipitation, snowfall) 
that contradict or don't appear in the tool outputs.

PASS for everything else, including:
- General travel advice and knowledge
- Place names from tool outputs (even from addresses)
- The user's home location
- High-level destination suggestions

When in doubt, PASS.

Respond EXACTLY:
VERDICT: PASS or FAIL
REASON: one sentence
"""


_supervisor_model = None


def _get_model():
    global _supervisor_model
    if _supervisor_model is None:
        _supervisor_model = init_chat_model(
            SUPERVISOR_MODEL, model_provider="groq", temperature=0
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

    try:
        with timer() as t:
            model = _get_model()
            result = model.invoke([
                {"role": "system", "content": SUPERVISOR_PROMPT},
                {"role": "user", "content": check_prompt},
            ])
    except Exception as e:
        log_supervisor("SKIP", f"Supervisor error: {str(e)[:100]}", 0)
        return {"passed": True, "verdict": "SKIP", "reason": "Supervisor unavailable"}

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
