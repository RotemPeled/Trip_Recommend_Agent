import json
import uuid
import streamlit as st

from agent import create_trip_agent, invoke_agent, store
from tools.weather import validate_city
from ui.styles import CUSTOM_CSS
from ui.components import render_tool_trace, render_supervisor_badge, render_preferences_sidebar
from logger import setup_logging

setup_logging()

st.set_page_config(
    page_title="Trip Planner AI",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="expanded",
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


def _render_sidebar():
    with st.sidebar:
        st.markdown("### Trip Planner AI")

        if st.session_state.home_location:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown(f"**Home Location**")
            loc = st.session_state.home_location
            st.markdown(f"{loc['name']}, {loc['country']}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**Saved Preferences**")
        prefs_item = store.get(("user",), "preferences")
        prefs = prefs_item.value if prefs_item and prefs_item.value else {}
        render_preferences_sidebar(prefs)
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        if st.button("New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()

        if st.button("Reset Everything", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def _render_onboarding():
    st.markdown(
        '<div class="main-header">'
        "<h1>Trip Planner AI</h1>"
        "<p>Your intelligent travel destination advisor</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="onboarding-card">', unsafe_allow_html=True)
    st.markdown("## Welcome!")
    st.markdown("Let's start by setting your home location so I can give you personalized recommendations.")

    col1, col2 = st.columns(2)
    with col1:
        city = st.text_input("City", placeholder="e.g., Tel Aviv")
    with col2:
        country = st.text_input("Country", placeholder="e.g., Israel")

    if st.button("Get Started", use_container_width=True, type="primary"):
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

    st.markdown("</div>", unsafe_allow_html=True)


def _render_chat():
    st.markdown(
        '<div class="main-header">'
        "<h1>Trip Planner AI</h1>"
        "<p>Ask me about travel destinations, weather, things to do, and more</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                if msg.get("tool_calls"):
                    render_tool_trace(msg["tool_calls"])
                if msg.get("supervisor"):
                    render_supervisor_badge(msg["supervisor"])

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

            if result.get("tool_calls"):
                render_tool_trace(result["tool_calls"])
            if result.get("supervisor"):
                render_supervisor_badge(result["supervisor"])

        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"],
            "tool_calls": result.get("tool_calls", []),
            "supervisor": result.get("supervisor"),
        })


_render_sidebar()

if st.session_state.home_location is None:
    _render_onboarding()
else:
    if st.session_state.agent is None:
        loc = st.session_state.home_location
        home_str = f"{loc['name']}, {loc['country']}"
        st.session_state.agent = create_trip_agent(home_str)
    _render_chat()
