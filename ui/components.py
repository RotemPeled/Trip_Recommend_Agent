import json
import streamlit as st


def render_tool_trace(tool_calls: list[dict]):
    """Render expandable tool call trace in the chat."""
    if not tool_calls:
        return

    with st.expander("View tool calls", expanded=False):
        for tc in tool_calls:
            name = tc.get("name", "unknown")
            try:
                inp = json.loads(tc.get("input", "{}"))
                inp_str = json.dumps(inp, indent=2)
            except (json.JSONDecodeError, TypeError):
                inp_str = tc.get("input", "")

            output = tc.get("output", "")
            preview = output[:400] + "..." if len(output) > 400 else output

            st.markdown(f"**{name}**")
            st.code(f"Input: {inp_str}", language="json")
            st.code(f"Output: {preview}", language="text")
            st.divider()


def render_supervisor_badge(supervisor: dict):
    """Render the supervisor verdict as a badge."""
    if not supervisor:
        return

    verdict = supervisor.get("verdict", "PASS")
    reason = supervisor.get("reason", "")

    if verdict == "PASS":
        st.markdown(
            f'<span class="supervisor-badge supervisor-pass">Supervisor: PASS</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<span class="supervisor-badge supervisor-fail">Supervisor: FAIL — {reason}</span>',
            unsafe_allow_html=True,
        )


def render_preferences_sidebar(preferences: dict):
    """Render user preferences in the sidebar."""
    if not preferences:
        st.caption("No preferences saved yet. Chat with the agent and it will remember your preferences!")
        return

    for key, value in preferences.items():
        if isinstance(value, list):
            val_str = ", ".join(str(v) for v in value)
        else:
            val_str = str(value)
        st.markdown(
            f'<span class="preference-chip">{key}: {val_str}</span>',
            unsafe_allow_html=True,
        )
