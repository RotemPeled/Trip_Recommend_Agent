import json
import time
import logging
from contextlib import contextmanager

logger = logging.getLogger("trip_agent")

SEPARATOR = "═" * 55
THIN_SEP = "─" * 55

_COLORS = {
    "CYAN": "\033[96m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "MAGENTA": "\033[95m",
    "BLUE": "\033[94m",
    "BOLD": "\033[1m",
    "RESET": "\033[0m",
}


def _c(color: str, text: str) -> str:
    return f"{_COLORS.get(color, '')}{text}{_COLORS['RESET']}"


def setup_logging():
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False


def log_user_message(message: str):
    logger.info("")
    logger.info(_c("CYAN", SEPARATOR))
    logger.info(_c("CYAN", f"  [USER MESSAGE] \"{message}\""))
    logger.info(_c("CYAN", SEPARATOR))


def log_tool_call(tool_name: str, tool_input: dict):
    logger.info("")
    logger.info(_c("YELLOW", f"  [TOOL CALL] {tool_name}"))
    try:
        formatted = json.dumps(tool_input, indent=4, ensure_ascii=False)
    except (TypeError, ValueError):
        formatted = str(tool_input)
    logger.info(_c("YELLOW", f"    Input:  {formatted}"))


def log_tool_result(tool_name: str, result: str, duration_ms: float):
    preview = result[:500] + "..." if len(result) > 500 else result
    logger.info(_c("YELLOW", f"    Output: {preview}"))
    logger.info(_c("YELLOW", f"    Duration: {duration_ms:.0f}ms"))


def log_tool_error(tool_name: str, error: str):
    logger.info(_c("RED", f"    ERROR: {error}"))


def log_llm_response(response: str, duration_ms: float):
    logger.info("")
    preview = response[:300] + "..." if len(response) > 300 else response
    logger.info(_c("GREEN", f"  [LLM RESPONSE] {preview}"))
    logger.info(_c("GREEN", f"    Duration: {duration_ms:.0f}ms"))


def log_supervisor(verdict: str, reason: str, duration_ms: float):
    logger.info("")
    color = "GREEN" if verdict == "PASS" else "RED"
    logger.info(_c("MAGENTA", f"  [SUPERVISOR] Checking response against tool data..."))
    logger.info(_c(color, f"    Verdict: {verdict}"))
    if reason:
        logger.info(_c(color, f"    Reason: {reason}"))
    logger.info(_c("MAGENTA", f"    Duration: {duration_ms:.0f}ms"))


def log_total_duration(duration_ms: float):
    logger.info("")
    logger.info(_c("BLUE", f"  Total request time: {duration_ms:.0f}ms"))
    logger.info(_c("BLUE", THIN_SEP))


@contextmanager
def timer():
    """Context manager that yields a dict with elapsed_ms after exit."""
    result = {"elapsed_ms": 0}
    start = time.perf_counter()
    try:
        yield result
    finally:
        result["elapsed_ms"] = (time.perf_counter() - start) * 1000
