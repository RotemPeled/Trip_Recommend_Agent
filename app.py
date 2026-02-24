import uuid
import streamlit as st

from agent import create_trip_agent, invoke_agent, store
from tools.weather import validate_city
from ui.styles import CUSTOM_CSS

from logger import setup_logging

setup_logging()

st.set_page_config(
    page_title="Trip Planner AI",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _init_session():
    if "home_location" not in st.session_state:
        st.session_state.home_location = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "agent" not in st.session_state:
        st.session_state.agent = None


_init_session()


def _render_onboarding():
    st.markdown(
        '<div class="main-header">'
        "<h1>Trip Planner AI</h1>"
        "<p>Your intelligent travel destination advisor</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown("#### Where are you based?")
        st.caption("This helps me give you personalized travel recommendations.")

        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input("City", placeholder="e.g., Tel Aviv", label_visibility="collapsed")
        with col2:
            country = st.text_input("Country", placeholder="e.g., Israel", label_visibility="collapsed")

        if st.button("Get Started →", use_container_width=True, type="primary"):
            if not city or not country:
                st.error("Please enter both city and country.")
            else:
                with st.spinner("Validating location..."):
                    result = validate_city(city, country)
                if not result:
                    st.error(
                        f"Could not find '{city}, {country}'. "
                        "Please check the spelling and try again."
                    )
                elif result["country"].lower() != country.strip().lower():
                    st.error(
                        f"'{city}' was found in **{result['country']}**, not in "
                        f"**{country}**. Please check the city and country."
                    )
                else:
                    st.session_state.home_location = result
                    home_str = f"{result['name']}, {result['country']}"
                    st.session_state.agent = create_trip_agent(home_str)
                    store.put(("user",), "home_location", result)
                    st.rerun()


def _render_chat():
    loc = st.session_state.home_location
    home_label = f"{loc['name']}, {loc['country']}" if loc else ""

    col_title, col_actions = st.columns([5, 1])
    with col_title:
        st.markdown(
            '<div class="chat-header">'
            '<h1>Trip Planner AI</h1>'
            f'<span class="home-badge">📍 {home_label}</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    with col_actions:
        if st.button("↻ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()

    st.markdown('<div class="chat-divider"></div>', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown(
            '<div class="empty-state">'
            '<p>Ask me about travel destinations, weather, things to do, and more.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Where would you like to go?"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = invoke_agent(
                    st.session_state.agent,
                    prompt,
                    st.session_state.thread_id,
                )

            st.markdown(result["response"])

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"],
            "tool_calls": result.get("tool_calls", []),
            "supervisor": result.get("supervisor"),
        })


if st.session_state.home_location is None:
    _render_onboarding()
else:
    if st.session_state.agent is None:
        loc = st.session_state.home_location
        home_str = f"{loc['name']}, {loc['country']}"
        st.session_state.agent = create_trip_agent(home_str)
    _render_chat()
