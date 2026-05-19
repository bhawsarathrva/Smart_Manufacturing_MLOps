"""
Streamlit Chat UI for Smart Manufacturing GenAI Assistant
Embed this as a page in your existing Streamlit dashboard
"""

import streamlit as st
import requests
import uuid
from datetime import datetime

# Config 
GENAI_API_URL = "http://localhost:8001"  

INTENT_ICONS = {
    "anomaly_query": "🔴",
    "maintenance_query": "🔧",
    "quality_query": "✅",
    "energy_query": "⚡",
    "model_performance": "🤖",
    "live_metrics": "📊",
    "alert_explanation": "⚠️",
    "action_recommendation": "💡",
    "general_manufacturing": "🏭",
    "greeting": "👋",
    "unknown": "💬",
}


# Page Config 
def setup_page():
    st.set_page_config(
        page_title="MAIA - Manufacturing AI Assistant",
        page_icon="🤖",
        layout="wide"
    )
    st.markdown("""
    <style>
    .chat-container { max-height: 600px; overflow-y: auto; }
    .user-msg {
        background: #1a73e8; color: white; border-radius: 18px 18px 4px 18px;
        padding: 10px 16px; margin: 4px 0; max-width: 75%; float: right; clear: both;
    }
    .bot-msg {
        background: #2d2d2d; color: #f0f0f0; border-radius: 18px 18px 18px 4px;
        padding: 10px 16px; margin: 4px 0; max-width: 80%; float: left; clear: both;
    }
    .source-badge {
        background: #333; color: #aaa; border-radius: 4px;
        padding: 2px 8px; font-size: 11px; margin-right: 4px;
    }
    .stTextInput > div > div > input { border-radius: 24px; }
    </style>
    """, unsafe_allow_html=True)


# Session State 
def init_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "show_sources" not in st.session_state:
        st.session_state.show_sources = True


# API Calls 
def send_message(message: str) -> dict:
    """Send message to GenAI API."""
    try:
        response = requests.post(
            f"{GENAI_API_URL}/chat",
            json={"message": message, "session_id": st.session_state.session_id},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {
            "response": "⚠️ Cannot connect to the GenAI API. Make sure `api_server.py` is running on port 8001.",
            "intent": "unknown", "sources": [], "message_count": 0,
            "timestamp": datetime.now().isoformat(), "session_id": st.session_state.session_id
        }
    except Exception as e:
        return {
            "response": f"❌ Error: {str(e)}",
            "intent": "unknown", "sources": [],
            "message_count": 0, "timestamp": datetime.now().isoformat(),
            "session_id": st.session_state.session_id
        }


def get_suggestions() -> list:
    try:
        r = requests.get(f"{GENAI_API_URL}/chat/suggestions", timeout=5)
        return r.json().get("suggestions", [])
    except:
        return [
            "What anomalies were detected today?",
            "Which machines need maintenance?",
            "Show current production KPIs",
            "Which ML models need retraining?",
        ]


# UI Components 
def render_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/factory.png", width=60)
        st.title("MAIA Assistant")
        st.caption("Manufacturing AI Assistant powered by Gemini")
        st.divider()

        # Session info
        st.markdown("**Session**")
        st.code(st.session_state.session_id[:12] + "...", language=None)
        st.caption(f"Messages: {len(st.session_state.messages)}")

        st.divider()

        # Settings
        st.markdown("**Settings**")
        st.session_state.show_sources = st.toggle("Show Sources", value=True)

        st.divider()

        # Quick actions
        st.markdown("**Quick Actions**")
        if st.button("🆕 New Conversation"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

        if st.button("📥 Export Chat"):
            if st.session_state.messages:
                chat_text = "\n\n".join([
                    f"[{m['role'].upper()}] {m['content']}"
                    for m in st.session_state.messages
                ])
                st.download_button(
                    "Download .txt",
                    data=chat_text,
                    file_name=f"maia_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                )

        st.divider()

        # Upload document
        st.markdown("**📄 Add to Knowledge Base**")
        uploaded = st.file_uploader(
            "Upload SOP / Manual (.txt)",
            type=["txt"],
            help="Enrich MAIA with your manufacturing documents"
        )
        if uploaded:
            text = uploaded.read().decode("utf-8")
            try:
                r = requests.post(
                    f"{GENAI_API_URL}/rag/upload",
                    files={"file": (uploaded.name, text.encode(), "text/plain")},
                    timeout=60
                )
                if r.status_code == 200:
                    st.success(r.json().get("message", "Uploaded!"))
                else:
                    st.error("Upload failed")
            except:
                st.error("Cannot connect to API")


def render_chat_messages():
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center; padding: 40px; color: #888;">
            <h2>👋 Welcome to MAIA</h2>
            <p>Your Manufacturing AI Assistant powered by Google Gemini</p>
        </div>
        """, unsafe_allow_html=True)
        return

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])
                if st.session_state.show_sources and msg.get("sources"):
                    source_badges = " ".join([
                        f"`{s}`" for s in msg["sources"]
                    ])
                    st.caption(f"Sources: {source_badges}")
                if msg.get("intent"):
                    icon = INTENT_ICONS.get(msg["intent"], "💬")
                    st.caption(f"{icon} {msg['intent'].replace('_', ' ').title()}")


def render_suggestions():
    """Show quick suggestion buttons when chat is empty."""
    if len(st.session_state.messages) > 0:
        return

    suggestions = get_suggestions()
    st.markdown("**💡 Try asking:**")
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions[:6]):
        with cols[i % 2]:
            if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                process_user_message(suggestion)
                st.rerun()


def process_user_message(message: str):
    st.session_state.messages.append({"role": "user", "content": message})
    with st.spinner("MAIA is thinking..."):
        result = send_message(message)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "sources": result.get("sources", []),
        "intent": result.get("intent", "unknown"),
        "timestamp": result.get("timestamp")
    })


# Main App 
def main():
    setup_page()
    init_session()
    render_sidebar()

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🤖 MAIA — Manufacturing AI Assistant")
        st.caption("Ask me anything about your production line, anomalies, maintenance, or ML models")
    with col2:
        try:
            r = requests.get(f"{GENAI_API_URL}/health", timeout=3)
            if r.status_code == 200:
                st.success("🟢 API Connected", icon="✅")
            else:
                st.error("🔴 API Error")
        except:
            st.warning("🟡 API Offline")

    st.divider()

    render_chat_messages()
    render_suggestions()

    if prompt := st.chat_input("Ask about anomalies, maintenance, quality, energy, or ML models..."):
        process_user_message(prompt)
        st.rerun()


if __name__ == "__main__":
    main()