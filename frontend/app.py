import streamlit as st
import requests
import os
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "https://rimandeep-ai-devops-backend.hf.space")

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI DevOps Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Keep the HF Space awake: refresh every 10 minutes ────────────────────
st_autorefresh(interval=10 * 60 * 1000, key="keep_alive_refresh")

# ── Custom CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
  .main { background-color: #0e1117; }
  section[data-testid="stSidebar"] > div:first-child { padding-top: 0rem !important; }
  section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] { padding-top: 0rem !important; }
  .block-container { padding-top: 1rem; padding-left: 3rem; padding-right: 3rem; }
  .stTextArea textarea { font-family: 'Courier New', monospace; font-size: 13px; }
  .tool-badge {
    background-color: #1f6feb;
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
  }
</style>
""", unsafe_allow_html=True)


# ── Session state ────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None


# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 AI DevOps Assistant")
    st.markdown("---")

    st.markdown("### What I can help with")
    st.markdown("""
- 🔴 **CI/CD Errors** — paste a pipeline failure log
- 📋 **Terraform Plans** — paste `terraform plan` output
- 🐳 **Dockerfile Review** — paste your Dockerfile
- 📖 **Runbooks** — describe an incident
- 📊 **Log Analysis** — paste application logs
- 💬 **General DevOps Q&A** — ask anything
    """)

    st.markdown("---")
    st.markdown("### Example prompts")

    examples = [
        "Why is my GitHub Actions workflow failing?",
        "Review this Dockerfile for security issues",
        "Explain what this terraform plan will do",
        "Generate a runbook for a database outage",
        "Analyse these application error logs",
    ]

    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state.prefill = example

    st.markdown("---")

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.rerun()

    # Live metrics
    st.markdown("### 📊 Live metrics")
    try:
        resp = requests.get(f"{BACKEND_URL}/metrics", timeout=3)
        if resp.status_code == 200:
            m = resp.json()
            col1, col2 = st.columns(2)
            col1.metric("Total requests", m["total_requests"])
            col2.metric("Avg response", f"{m['average_response_time_ms']}ms")
    except Exception:
        st.caption("Metrics unavailable")

    # Backend health
    st.markdown("### 🟢 Backend status")
    try:
        h = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if h.status_code == 200:
            st.success("Backend is healthy")
        else:
            st.error("Backend returned an error")
    except Exception:
        st.error("Cannot reach backend")


# ── Main chat area ────────────────────────────────────────────────────────
st.title("AI DevOps Assistant")
st.caption("Powered by LLaMA 3.3 70B via Groq · Built with LangChain + FastAPI · Hosted on HuggingFace Spaces")

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("tool_used"):
            st.markdown(
                f'<span class="tool-badge">🔧 {msg["tool_used"]}</span>',
                unsafe_allow_html=True
            )

# Input box
prefill = st.session_state.pop("prefill", "") if "prefill" in st.session_state else ""
user_input = st.chat_input("Ask me anything about DevOps, or paste an error log, Dockerfile, or Terraform plan...")

if user_input or prefill:
    message = user_input or prefill

    # Add user message to display
    st.session_state.messages.append({"role": "user", "content": message})
    with st.chat_message("user"):
        st.markdown(message)

    # Call backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Build history for the API
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]
                ]

                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={
                        "message": message,
                        "conversation_id": st.session_state.conversation_id,
                        "history": history,
                    },
                    timeout=60,
                )

                if response.status_code == 200:
                    data = response.json()
                    reply = data["reply"]
                    tool_used = data.get("tool_used")
                    st.session_state.conversation_id = data["conversation_id"]

                    st.markdown(reply)
                    if tool_used:
                        st.markdown(
                            f'<span class="tool-badge">🔧 {tool_used}</span>',
                            unsafe_allow_html=True
                        )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": reply,
                        "tool_used": tool_used,
                    })

                else:
                    st.error(f"Backend error: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Is it running?")
            except requests.exceptions.Timeout:
                st.error("Request timed out. The model may be busy — try again.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")