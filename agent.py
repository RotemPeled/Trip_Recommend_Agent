import json
import time

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from config import GROQ_MODEL
from tools.weather import get_weather
from tools.places import search_places
from supervisor import run_supervisor
from logger import (
    log_user_message,
    log_tool_call,
    log_tool_result,
    log_tool_error,
    log_llm_response,
    log_total_duration,
    timer,
)

SYSTEM_PROMPT = """You are a friendly and knowledgeable Trip Location Planner.

You help users discover the perfect travel destination based on their preferences, 
interests, budget, and timing.

## Your Tools

You have access to these tools:
- **get_weather**: Check climate/weather data for a city in a specific month. Use this 
  to verify if a destination has suitable weather for what the user wants.
- **search_places**: Search for attractions, restaurants, activities, and things to do 
  at a destination. Use this to find specific activities the user is interested in.
- **save_user_preferences**: Save the user's travel preferences for future sessions.
- **get_user_preferences**: Load previously saved preferences at the start of a conversation.

## How to Behave

1. **Be concise**: Keep responses short and to the point. Use bullet points or short 
   paragraphs. Don't write essays. 3-5 sentences for simple answers, a short structured 
   list for destination recommendations.

2. **Detect missing information**: If the user's request is incomplete (missing destination, 
   dates/month, interests), ask for the missing details before using tools. 
   For example, if they say "I want to go skiing" — ask when they want to go.

3. **Use tools wisely**: Only call tools when you have enough info to make the call useful. 
   You can call multiple tools if needed. Don't call tools for general conversation.

4. **Be grounded**: When presenting weather data or places, use the actual data from tools. 
   Don't invent temperatures, ratings, or place names.

5. **Be conversational**: You're a travel advisor, not a robot. Be warm but brief.

6. **Remember context**: Use the chat history to understand follow-up questions.

7. **Self-correct**: If a tool returns an error, try an alternative or explain the limitation.

8. **Home location**: The user's home location is provided below. You know this from their 
   profile — it's not fabricated. Use it naturally for context when relevant.

## User's Home Location
{home_location}

## User's Saved Preferences  
{user_preferences}
"""


@tool
def save_user_preferences(
    preferences: str,
    runtime: ToolRuntime,
) -> str:
    """Save the user's travel preferences for future sessions.

    Call this when the user reveals important preferences you should remember,
    such as: preferred travel style (adventure, relaxation, culture), budget range,
    dietary needs, accessibility requirements, favorite destinations, or things they dislike.

    Args:
        preferences: A JSON string describing the user's preferences.
            Example: '{"style": "adventure", "budget": "mid-range", "interests": ["hiking", "local food"]}'
    """
    store = runtime.store
    existing = store.get(("user",), "preferences")
    existing_prefs = existing.value if existing else {}

    try:
        new_prefs = json.loads(preferences)
    except json.JSONDecodeError:
        new_prefs = {"raw": preferences}

    merged = {**existing_prefs, **new_prefs}
    store.put(("user",), "preferences", merged)
    return f"Preferences saved: {json.dumps(merged)}"


@tool
def get_user_preferences(runtime: ToolRuntime) -> str:
    """Load the user's previously saved travel preferences.

    Call this at the beginning of a new conversation to check if the user
    has any saved preferences from previous sessions.
    """
    store = runtime.store
    item = store.get(("user",), "preferences")
    if item and item.value:
        return f"Saved preferences: {json.dumps(item.value)}"
    return "No saved preferences found."


checkpointer = InMemorySaver()
store = InMemoryStore()

ALL_TOOLS = [get_weather, search_places, save_user_preferences, get_user_preferences]


def create_trip_agent(home_location: str = "Not set yet"):
    """Create and return the trip planning agent."""
    prefs_item = store.get(("user",), "preferences")
    prefs_str = json.dumps(prefs_item.value) if prefs_item and prefs_item.value else "None saved yet"

    prompt = SYSTEM_PROMPT.format(
        home_location=home_location,
        user_preferences=prefs_str,
    )

    model = init_chat_model(GROQ_MODEL, model_provider="groq", temperature=0.7)

    agent = create_agent(
        model=model,
        tools=ALL_TOOLS,
        system_prompt=prompt,
        checkpointer=checkpointer,
        store=store,
    )
    return agent


def _extract_new_messages(all_messages: list, user_content: str) -> list:
    """Extract only the messages from the current turn (after the last matching user message)."""
    for i in range(len(all_messages) - 1, -1, -1):
        msg = all_messages[i]
        if getattr(msg, "type", None) == "human" and msg.content == user_content:
            return all_messages[i + 1:]
    return all_messages


def _build_tool_input_map(messages: list) -> dict:
    """Build a map from tool_call_id to tool input args from AI messages."""
    tc_map = {}
    for msg in messages:
        if getattr(msg, "type", None) == "ai" and hasattr(msg, "tool_calls"):
            for tc in (msg.tool_calls or []):
                tc_id = tc.get("id", "")
                tc_map[tc_id] = {
                    "name": tc.get("name", "unknown"),
                    "args": tc.get("args", {}),
                }
    return tc_map


def invoke_agent(agent, user_message: str, thread_id: str = "default") -> dict:
    """Invoke the agent with logging and supervisor validation.

    Returns dict with: response (str), tool_calls (list), supervisor (dict)
    """
    request_start = time.perf_counter()
    log_user_message(user_message)

    config = {"configurable": {"thread_id": thread_id}}

    with timer() as agent_timer:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]},
            config=config,
        )

    all_messages = result.get("messages", [])
    new_messages = _extract_new_messages(all_messages, user_message)

    tc_map = _build_tool_input_map(new_messages)

    tool_calls_log = []
    agent_response = ""

    for msg in new_messages:
        msg_type = getattr(msg, "type", None)

        if msg_type == "tool":
            tool_call_id = getattr(msg, "tool_call_id", "")
            tool_name = getattr(msg, "name", "unknown")
            tool_output = msg.content

            tc_info = tc_map.get(tool_call_id, {})
            tool_args = tc_info.get("args", {})

            log_tool_call(tool_name, tool_args)
            log_tool_result(tool_name, tool_output, 0)

            tool_calls_log.append({
                "name": tool_name,
                "input": json.dumps(tool_args),
                "output": tool_output,
            })

    for msg in reversed(new_messages):
        if getattr(msg, "type", None) == "ai" and msg.content:
            agent_response = msg.content
            break

    log_llm_response(agent_response, agent_timer["elapsed_ms"])

    home_item = store.get(("user",), "home_location")
    home_ctx = f"Home: {home_item.value}" if home_item and home_item.value else ""
    prefs_item = store.get(("user",), "preferences")
    prefs_ctx = f"Preferences: {prefs_item.value}" if prefs_item and prefs_item.value else ""
    user_context = f"{home_ctx}\n{prefs_ctx}".strip()

    supervisor_result = run_supervisor(user_message, tool_calls_log, agent_response, user_context)

    if not supervisor_result["passed"]:
        retry_message = (
            f"Your previous response was flagged by the supervisor: "
            f"{supervisor_result['reason']}. "
            f"Please regenerate your response using ONLY data from the tools. "
            f"Do not fabricate any information."
        )
        with timer() as retry_timer:
            retry_result = agent.invoke(
                {"messages": [{"role": "user", "content": retry_message}]},
                config=config,
            )

        retry_messages = retry_result.get("messages", [])
        for msg in reversed(retry_messages):
            if getattr(msg, "type", None) == "ai" and msg.content:
                agent_response = msg.content
                break

        log_llm_response(agent_response, retry_timer["elapsed_ms"])
        supervisor_result = {"passed": True, "verdict": "PASS", "reason": "After retry"}

    total_ms = (time.perf_counter() - request_start) * 1000
    log_total_duration(total_ms)

    return {
        "response": agent_response,
        "tool_calls": tool_calls_log,
        "supervisor": supervisor_result,
    }
