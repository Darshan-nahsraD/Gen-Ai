# from dotenv import load_dotenv
# load_dotenv()

# from langchain_groq import ChatGroq
# llm = ChatGroq(model="openai/gpt-oss-120b")

# from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
# click=int(input("choose ai mode : "))
# if click==1 :
#     mode="you are a funny AI agent. you respond with humor and jokes."
# elif click==2 :
#     mode="you are a angry AI agent. you respond with aggressively and impatiently."
# elif click==3 :
#     mode="you are a funny AI agent. you respond in a depressed and emotional tone."
# history=[
#     SystemMessage(content = mode)
# ]

# # print("----------------------------- HELLO!! WHAT'S UP !! HOW CAN I CHANGE YOUR MOOD -----------------------------------")

# while(1):
#     querry = input("YOU : ")
#     if(querry=="exit") : 
#         print("Thank you nice to see you again!!!!!!!")
#         break
#     history.append(HumanMessage(content=querry))

#     response=llm.invoke(history)

#     history.append(AIMessage(content=response.content))
#     print("BOT : ", response.content)
#     print()
#     print()
#     print()
#     print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! print exit to stop !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


# claude
# import streamlit as st
# from dotenv import load_dotenv
# load_dotenv()

# import streamlit as st
# from langchain_groq import ChatGroq
# from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

# st.set_page_config(page_title="Funny AI Chatbot", page_icon="😄")


# @st.cache_resource
# def get_llm():
#     return ChatGroq(model="openai/gpt-oss-120b")


# llm = get_llm()

# # Same history and system role as the terminal version
# if "history" not in st.session_state:
#     st.session_state.history = [
#         SystemMessage(content="you are a funny AI agent")
#     ]

# st.title("😄 Funny AI Chatbot")
# st.caption("HELLO!! WHAT'S UP !! HOW CAN I CHANGE YOUR MOOD")

# # Show past messages (the system message is not displayed)
# for msg in st.session_state.history:
#     if isinstance(msg, HumanMessage):
#         with st.chat_message("user"):
#             st.markdown(msg.content)
#     elif isinstance(msg, AIMessage):
#         with st.chat_message("assistant"):
#             st.markdown(msg.content)

# query = st.chat_input("YOU : ")

# if query:
#     st.session_state.history.append(HumanMessage(content=query))
#     with st.chat_message("user"):
#         st.markdown(query)

#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             response = llm.invoke(st.session_state.history)
#         st.markdown(response.content)

#     st.session_state.history.append(AIMessage(content=response.content))


## claude

# from dotenv import load_dotenv
# load_dotenv()

# import streamlit as st
# from langchain_groq import ChatGroq
# from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

# MODEL_NAME = "openai/gpt-oss-120b"
# SYSTEM_PROMPT = "you are a funny AI agent"

# st.set_page_config(page_title="Angry AI Chatbot", page_icon="😄", layout="centered")

# # ---------- Styling ----------
# st.markdown(
#     """
#     <style>
#     #MainMenu, footer, .stDeployButton {visibility: hidden;}
#     .block-container {padding-top: 2rem; max-width: 800px;}

#     .hero-title {
#         font-size: 2.6rem; font-weight: 800; margin-bottom: 0;
#         background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb);
#         -webkit-background-clip: text; -webkit-text-fill-color: transparent;
#     }
#     .hero-sub {opacity: 0.7; margin-top: 0.2rem; margin-bottom: 1.5rem; letter-spacing: 0.5px;}

#     [data-testid="stChatMessage"] {
#         border-radius: 16px; padding: 1rem 1.2rem; margin-bottom: 0.7rem;
#         border: 1px solid rgba(128, 128, 128, 0.2);
#     }
#     .stButton > button {
#         border-radius: 12px; width: 100%; padding: 0.7rem;
#         border: 1px solid rgba(128, 128, 128, 0.35);
#     }
#     .stButton > button:hover {border-color: #feca57; color: #feca57;}
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


# @st.cache_resource
# def get_llm():
#     return ChatGroq(model=MODEL_NAME)


# llm = get_llm()

# # Same history and system role as the terminal version
# if "history" not in st.session_state:
#     st.session_state.history = [SystemMessage(content=SYSTEM_PROMPT)]

# # ---------- Sidebar ----------
# with st.sidebar:
#     st.markdown("### 😄 Funny AI Chatbot")
#     st.caption(f"Model: `{MODEL_NAME}`")
#     st.caption(f"Role: *{SYSTEM_PROMPT}*")
#     st.divider()
#     st.metric("Messages", len(st.session_state.history) - 1)
#     if st.button("🗑️ New chat"):
#         st.session_state.history = [SystemMessage(content=SYSTEM_PROMPT)]
#         st.rerun()

# # ---------- Header ----------
# st.markdown('<p class="hero-title">Funny AI Chatbot</p>', unsafe_allow_html=True)
# st.markdown(
#     '<p class="hero-sub">HELLO!! WHAT\'S UP !! HOW CAN I CHANGE YOUR MOOD</p>',
#     unsafe_allow_html=True,
# )

# pending = st.session_state.pop("pending", None)

# # ---------- Past messages (system message is not shown) ----------
# for msg in st.session_state.history:
#     if isinstance(msg, HumanMessage):
#         with st.chat_message("user", avatar="🧑"):
#             st.markdown(msg.content)
#     elif isinstance(msg, AIMessage):
#         with st.chat_message("assistant", avatar="😄"):
#             st.markdown(msg.content)

# # ---------- Empty-state suggestions ----------
# if len(st.session_state.history) == 1 and not pending:
#     st.markdown("##### Try one of these")
#     col1, col2, col3 = st.columns(3)
#     suggestions = ["Tell me a joke", "Roast my coding skills", "Cheer me up"]
#     for col, text in zip((col1, col2, col3), suggestions):
#         if col.button(text):
#             st.session_state.pending = text
#             st.rerun()

# # ---------- Chat input ----------
# query = st.chat_input("Type your message...") or pending

# if query:
#     st.session_state.history.append(HumanMessage(content=query))
#     with st.chat_message("user", avatar="🧑"):
#         st.markdown(query)

#     with st.chat_message("assistant", avatar="😄"):
#         try:
#             with st.spinner("Thinking of something funny..."):
#                 response = llm.invoke(st.session_state.history)
#             st.markdown(response.content)
#             st.session_state.history.append(AIMessage(content=response.content))
#         except Exception as e:
#             st.session_state.history.pop()  # remove the unanswered message
#             st.error(f"Something went wrong: {e}")

# gemini
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Multi-Mode AI Agent", page_icon="🤖")
st.title("Multi-Mode AI Agent 🤖")

# Initialize the LLM
@st.cache_resource
def get_llm():
    return ChatGroq(model="openai/gpt-oss-120b")

llm = get_llm()

# Define the modes and their corresponding system prompts
MODES = {
    "Funny": "you are a funny AI agent. you respond with humor and jokes.",
    "Angry": "you are an angry AI agent. you respond aggressively and impatiently.",
    "Depressed": "you are a depressed AI agent. you respond in a depressed and emotional tone."
}

# --- Sidebar Configuration ---
st.sidebar.title("⚙️ Settings")

# Callback function to clear the chat when the mode is changed
def reset_chat():
    st.session_state.history = []

# Mode selection in the sidebar
selected_mode = st.sidebar.radio(
    "Choose AI Personality Mode:",
    options=list(MODES.keys()),
    on_change=reset_chat # Clears history when a new mode is selected
)

st.sidebar.markdown(f"**Current Prompt:**\n_{MODES[selected_mode]}_")
st.sidebar.button("Clear Chat History", on_click=reset_chat)

# --- Chat Interface ---

# Initialize chat history if it doesn't exist or if it was just cleared
if "history" not in st.session_state or len(st.session_state.history) == 0:
    st.session_state.history = [
        SystemMessage(content=MODES[selected_mode])
    ]

# Display existing chat messages (skipping the hidden SystemMessage)
for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# Chat input area
query = st.chat_input(f"Talk to the {selected_mode} agent...")

if query:
    # 1. Display user message in UI
    with st.chat_message("user"):
        st.markdown(query)
    
    # 2. Add user message to session history
    st.session_state.history.append(HumanMessage(content=query))
    
    # 3. Generate and display AI response
    with st.chat_message("assistant"):
        with st.spinner(f"Agent is typing in {selected_mode.lower()} mode..."):
            response = llm.invoke(st.session_state.history)
            st.markdown(response.content)
            
    # 4. Add AI response to session history
    st.session_state.history.append(AIMessage(content=response.content))