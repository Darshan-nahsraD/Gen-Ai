
from dotenv import load_dotenv
load_dotenv()

import os
import requests
import streamlit as st

from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
    SystemMessage,
)
from tavily import TavilyClient


# =========================
# Streamlit Configuration
# =========================

st.set_page_config(
    page_title="Weather and News Agent",
    page_icon="🌦️",
)

st.title("🌦️ Weather and News Agent")
st.caption("Ask about weather or search for news on any topic.")


# =========================
# API Key Validation
# =========================

if not os.getenv("GROQ_API_KEY"):
    st.error("Please add GROQ_API_KEY to your .env file.")
    st.stop()

if not os.getenv("TAVILY_API_KEY"):
    st.error("Please add TAVILY_API_KEY to your .env file.")
    st.stop()


# =========================
# LLM Setup
# =========================

llm = ChatGroq(model="openai/gpt-oss-120b")

tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


# =========================
# Weather Tool
# =========================

@tool
def get_weather(city: str) -> str:
    """Get the current weather of a city in India."""

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return "OPENWEATHER_API_KEY is missing from the .env file."

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city},IN&appid={api_key}&units=metric"
    )

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if str(data.get("cod")) != "200":
            return f"Weather error: {data.get('message', 'Unknown error')}"

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]

        return f"Weather in {city}: {desc}, {temp}°C"

    except requests.RequestException as e:
        return f"Could not fetch weather: {e}"


# =========================
# News Tool
# =========================

@tool
def get_news(topic: str, city: str = "") -> str:
    """Search for latest news about a topic, optionally in a city or location."""

    if city:
        search_query = f"latest {topic} news in {city}"
    else:
        search_query = f"latest news about {topic}"

    try:
        response = tavily_client.search(
            query=search_query,
            search_depth="basic",
            max_results=5,
        )

        results = response.get("results", [])

        if not results:
            return f"No news found for {topic}."

        news_list = []

        for item in results:
            title = item.get("title", "No title")
            url = item.get("url", "")
            snippet = item.get("content", "")

            news_list.append(
                f"Title: {title}\n"
                f"Link: {url}\n"
                f"Summary: {snippet[:200]}"
            )

        location_text = f" in {city}" if city else ""

        return (
            f"Latest news about {topic}{location_text}:\n\n"
            + "\n\n".join(news_list)
        )

    except Exception as e:
        return f"News search failed: {e}"


# =========================
# Bind Tools
# =========================

llm = llm.bind_tools([get_weather, get_news])

tooldic = {
    "get_weather": get_weather,
    "get_news": get_news,
}


# =========================
# Session State
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(
            content=(
                "You are a helpful assistant. "
                "Use the weather and news tools when necessary. "
                "For news, identify the topic and optional location "
                "from the user's question."
            )
        )
    ]

if "pending_tool_calls" not in st.session_state:
    st.session_state.pending_tool_calls = []

if "pending_ai_message" not in st.session_state:
    st.session_state.pending_ai_message = None


# =========================
# Display Chat History
# =========================

for message in st.session_state.messages:

    if isinstance(message, SystemMessage):
        continue

    if isinstance(message, ToolMessage):
        continue

    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)

    elif isinstance(message, AIMessage):
        if message.content:
            with st.chat_message("assistant"):
                st.write(message.content)


# =========================
# Tool Approval
# =========================

if st.session_state.pending_tool_calls:

    st.warning("The assistant wants to use a tool.")

    for i, tool_call in enumerate(
        st.session_state.pending_tool_calls
    ):
        st.write(f"**Tool:** {tool_call['name']}")
        st.write(f"**Arguments:** {tool_call['args']}")

        st.radio(
            f"Allow this tool call? ({tool_call['name']})",
            options=["No", "Yes"],
            index=0,
            horizontal=True,
            key=f"permission_{i}",
        )

    if st.button("Confirm permissions", type="primary"):

        with st.spinner("Executing approved tools..."):

            for i, tool_call in enumerate(
                st.session_state.pending_tool_calls
            ):
                name = tool_call["name"]
                keyword = tooldic[name]

                permission = st.session_state[
                    f"permission_{i}"
                ]

                if permission == "Yes":
                    result = keyword.invoke(tool_call)
                else:
                    result = "Tool call denied by user."

                st.session_state.messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )

        # Clear completed approvals
        st.session_state.pending_tool_calls = []
        st.session_state.pending_ai_message = None

        # Ask the LLM to interpret tool results
        with st.spinner("Generating the final answer..."):
            response = llm.invoke(
                st.session_state.messages
            )

        st.session_state.messages.append(response)

        # Handle another tool request if the LLM needs one
        if response.tool_calls:
            st.session_state.pending_ai_message = response
            st.session_state.pending_tool_calls = (
                response.tool_calls
            )

        st.rerun()


# =========================
# Chat Input
# =========================

query = st.chat_input(
    "Ask about weather, protests, cricket, AI news...",
    disabled=bool(st.session_state.pending_tool_calls),
)

if query:

    st.session_state.messages.append(
        HumanMessage(content=query)
    )

    with st.spinner("Thinking..."):
        response = llm.invoke(
            st.session_state.messages
        )

    if response.tool_calls:

        # Preserve the AI's tool-call request
        st.session_state.messages.append(response)

        st.session_state.pending_ai_message = response
        st.session_state.pending_tool_calls = (
            response.tool_calls
        )

        st.rerun()

    else:
        st.session_state.messages.append(response)
        st.rerun()
