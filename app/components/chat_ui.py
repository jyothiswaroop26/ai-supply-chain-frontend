import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from typing import Optional, List, Dict
from services.api_client import send_query

# Directory to persist chat history files
CHAT_HISTORY_DIR = os.path.join(os.path.dirname(__file__), "..", "chat_history")
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)


def initialize_chat_session():
    """Initialize chat session state if not already present."""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_input_key" not in st.session_state:
        st.session_state.chat_input_key = 0
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "current_session_name" not in st.session_state:
        st.session_state.current_session_name = "New Conversation"


# ---------------------------------------------------------------------------
# Persistent chat history helpers
# ---------------------------------------------------------------------------

def _session_file(session_id: str) -> str:
    """Return the JSON file path for a session ID."""
    return os.path.join(CHAT_HISTORY_DIR, f"{session_id}.json")


def save_chat_history(session_name: Optional[str] = None) -> str:
    """
    Save the current conversation to a JSON file.

    Returns the session ID that was saved.
    """
    if not st.session_state.chat_messages:
        st.warning("Nothing to save — the conversation is empty.")
        return ""

    # Reuse existing session ID or create a new one
    session_id = st.session_state.current_session_id
    if not session_id:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.current_session_id = session_id

    name = session_name or st.session_state.current_session_name or "Untitled"
    st.session_state.current_session_name = name

    payload = {
        "session_id": session_id,
        "session_name": name,
        "saved_at": datetime.now().isoformat(),
        "messages": st.session_state.chat_messages,
    }

    with open(_session_file(session_id), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return session_id


def load_all_sessions() -> List[Dict]:
    """
    Return a list of session metadata dicts sorted newest-first.
    Each dict contains: session_id, session_name, saved_at, message_count.
    """
    sessions = []
    for fname in os.listdir(CHAT_HISTORY_DIR):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(CHAT_HISTORY_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            sessions.append({
                "session_id": data.get("session_id", fname[:-5]),
                "session_name": data.get("session_name", "Untitled"),
                "saved_at": data.get("saved_at", ""),
                "message_count": len(data.get("messages", [])),
            })
        except Exception:
            continue
    sessions.sort(key=lambda s: s["saved_at"], reverse=True)
    return sessions


def load_session(session_id: str) -> bool:
    """
    Load a saved session into st.session_state.

    Returns True on success, False otherwise.
    """
    fpath = _session_file(session_id)
    if not os.path.exists(fpath):
        st.error(f"Session '{session_id}' not found.")
        return False
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        st.session_state.chat_messages = data.get("messages", [])
        st.session_state.current_session_id = data.get("session_id", session_id)
        st.session_state.current_session_name = data.get("session_name", "Untitled")
        st.session_state.chat_input_key += 1
        return True
    except Exception as exc:
        st.error(f"Failed to load session: {exc}")
        return False


def delete_session(session_id: str) -> bool:
    """Delete a saved session file. Returns True on success."""
    fpath = _session_file(session_id)
    if os.path.exists(fpath):
        os.remove(fpath)
        # If the deleted session was active, reset state
        if st.session_state.current_session_id == session_id:
            st.session_state.current_session_id = None
            st.session_state.current_session_name = "New Conversation"
        return True
    return False


def start_new_conversation():
    """Clear the current conversation and start fresh."""
    st.session_state.chat_messages = []
    st.session_state.current_session_id = None
    st.session_state.current_session_name = "New Conversation"
    st.session_state.chat_input_key += 1


def add_message(role: str, content: str, metadata: Optional[dict] = None):
    """
    Add a message to the chat history.
    
    Args:
        role: "user", "assistant", or "system"
        content: The message content
        metadata: Optional metadata (timestamp, source, etc.)
    """
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }
    if metadata:
        message.update(metadata)
    st.session_state.chat_messages.append(message)


def render_chat_message(message: dict):
    """Render a single chat message as a styled chat bubble."""
    role = message.get("role", "assistant")
    content = message.get("content", "")
    timestamp = message.get("timestamp", "")

    if role == "user":
        bubble_class = "chat-bubble-user"
        row_class = "chat-row-user"
        avatar = "👤"
        label = "You"
    elif role == "assistant":
        bubble_class = "chat-bubble-assistant"
        row_class = "chat-row-assistant"
        avatar = "🤖"
        label = "AI Assistant"
    else:
        bubble_class = "chat-bubble-system"
        row_class = "chat-row-system"
        avatar = "⚙️"
        label = "System"

    # Escape HTML special chars in content, then re-allow newlines as <br>
    import html as _html
    safe_content = _html.escape(content).replace("\n", "<br>")

    bubble_html = f"""
<div class="chat-row {row_class}">
  <div class="chat-avatar">{avatar}</div>
  <div class="chat-bubble-wrap">
    <div class="chat-bubble-meta">
      <span class="chat-bubble-label">{label}</span>
      <span class="chat-bubble-time">{timestamp}</span>
    </div>
    <div class="chat-bubble {bubble_class}">{safe_content}</div>
  </div>
</div>
"""
    st.markdown(bubble_html, unsafe_allow_html=True)


def render_chat_history():
    """Render the chat message history."""
    if not st.session_state.chat_messages:
        st.info(
            "💬 No messages yet. Start a conversation by typing a message below.",
            icon="ℹ️"
        )
    else:
        for message in st.session_state.chat_messages:
            render_chat_message(message)


def render_chat_controls():
    """Render chat control buttons."""
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        if st.button("➕ New Chat", key="new_chat_btn", use_container_width=True):
            start_new_conversation()
            st.rerun()

    with col2:
        if st.button("🔄 Clear Chat", key="clear_chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    with col3:
        if st.button("📋 Export CSV", key="export_chat", use_container_width=True):
            export_chat_as_csv()

    with col4:
        if st.button("💾 Save Chat", key="save_chat", use_container_width=True):
            sid = save_chat_history()
            if sid:
                st.success(f"✅ Saved as '{st.session_state.current_session_name}'")


def export_chat_as_csv():
    """Export chat history as CSV."""
    if not st.session_state.chat_messages:
        st.warning("No messages to export.")
        return
    
    df = pd.DataFrame(st.session_state.chat_messages)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download Chat as CSV",
        data=csv,
        file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        key="download_chat_csv"
    )


def render_history_panel():
    """
    Render the Chat History panel: list saved sessions with load / delete actions.
    """
    st.subheader("📂 Saved Conversations")

    # ---- Save current conversation with a custom name ----
    with st.expander("💾 Save current conversation", expanded=False):
        default_name = st.session_state.get("current_session_name", "New Conversation")
        save_name = st.text_input(
            "Conversation name",
            value=default_name,
            key="save_name_input",
        )
        if st.button("Save", key="history_save_btn"):
            sid = save_chat_history(session_name=save_name)
            if sid:
                st.success(f"Saved as **{save_name}**")
                st.rerun()

    st.divider()

    sessions = load_all_sessions()

    if not sessions:
        st.info("No saved conversations yet.")
        return

    for session in sessions:
        sid = session["session_id"]
        sname = session["session_name"]
        saved_at = session["saved_at"][:16].replace("T", " ") if session["saved_at"] else "—"
        msg_count = session["message_count"]
        is_active = sid == st.session_state.current_session_id

        label = f"{'🟢 ' if is_active else ''}**{sname}**"
        with st.container(border=True):
            st.markdown(label)
            st.caption(f"🕐 {saved_at}  •  💬 {msg_count} messages")
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button(
                    "📂 Load",
                    key=f"load_{sid}",
                    use_container_width=True,
                    disabled=is_active,
                ):
                    if load_session(sid):
                        st.success(f"Loaded **{sname}**")
                        st.rerun()
            with action_col2:
                if st.button(
                    "🗑️ Delete",
                    key=f"del_{sid}",
                    use_container_width=True,
                    type="secondary",
                ):
                    if delete_session(sid):
                        st.success(f"Deleted **{sname}**")
                        st.rerun()


def render_chat_ui():
    """Main chat UI component."""
    # Initialize session
    initialize_chat_session()

    st.markdown('<div class="section-header"><span class="section-header-accent"></span>AI Chat Assistant</div>', unsafe_allow_html=True)
    st.write("Interact with the AI assistant to get supply chain insights and recommendations.")

    # Session name badge
    st.caption(
        f"📁 Current conversation: **{st.session_state.current_session_name}**"
        + (f"  |  ID: `{st.session_state.current_session_id}`" if st.session_state.current_session_id else "  |  *(unsaved)*")
    )

    # Create tabs for different chat views
    chat_tab, history_tab, settings_tab = st.tabs(["Chat", "History", "Settings"])
    
    with history_tab:
        render_history_panel()

    with chat_tab:
        # Chat display container
        st.subheader("Conversation")
        
        # Display chat history in a scrollable container
        chat_container = st.container(height=500, border=True)
        with chat_container:
            render_chat_history()
        
        # Chat input section
        st.subheader("Send Message")
        input_cols = st.columns([0.9, 0.1])
        
        with input_cols[0]:
            user_input = st.text_input(
                "Type your message...",
                placeholder="Ask about supply chain metrics, forecasts, or recommendations...",
                key=f"chat_input_{st.session_state.chat_input_key}",
                label_visibility="collapsed"
            )
        
        with input_cols[1]:
            send_button = st.button("📤 Send", use_container_width=True)
        
        # Process user input
        if send_button and not user_input.strip():
            st.warning("Please type a message before sending.")

        if send_button and user_input.strip():
            # Add user message
            add_message("user", user_input)

            # Send message through API client helper
            try:
                with st.spinner("AI assistant is thinking..."):
                    response = send_query(
                        query=user_input,
                        session_id=st.session_state.current_session_id,
                    )
            except Exception as exc:
                response = {
                    "success": False,
                    "error": f"Chat API request failed: {exc}",
                }

            if response.get("success"):
                backend_session_id = response.get("session_id")
                if backend_session_id:
                    st.session_state.current_session_id = backend_session_id

                ai_response = (
                    response.get("response")
                    or response.get("message")
                    or response.get("reply")
                    or response.get("answer")
                    or ""
                )
                if not ai_response.strip():
                    st.warning("The backend returned an empty response.")
                    ai_response = "I received your message, but no response content was returned."
                add_message("assistant", ai_response)
            else:
                err = response.get("error") or "The assistant could not be reached."
                st.error(err)
                add_message(
                    "system",
                    f"{err} Please try again in a moment.",
                )
            
            # Reset input
            st.session_state.chat_input_key += 1
            st.rerun()
        
        # Chat controls
        st.divider()
        render_chat_controls()
    
    with settings_tab:
        st.subheader("Chat Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Chat Behavior**")
            mode = st.radio(
                "Response Mode:",
                ["Concise", "Detailed", "Technical"],
                label_visibility="collapsed"
            )
            
            temperature = st.slider(
                "Creativity Level:",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1
            )
        
        with col2:
            st.markdown("**Context Settings**")
            use_data = st.checkbox(
                "Use uploaded data for context",
                value=True
            )
            
            use_history = st.checkbox(
                "Use chat history",
                value=True
            )
        
        st.divider()
        
        st.markdown("**Chat Statistics**")
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        
        with stat_col1:
            st.metric(
                label="Total Messages",
                value=len(st.session_state.chat_messages),
            )
        
        with stat_col2:
            user_msgs = len([m for m in st.session_state.chat_messages if m["role"] == "user"])
            st.metric(
                label="Your Messages",
                value=user_msgs,
            )
        
        with stat_col3:
            ai_msgs = len([m for m in st.session_state.chat_messages if m["role"] == "assistant"])
            st.metric(
                label="AI Responses",
                value=ai_msgs,
            )


def generate_ai_response(user_input: str) -> str:
    """
    Generate AI response through backend API helper.
    
    Args:
        user_input: The user's message
        
    Returns:
        AI-generated response string
    """
    response = send_query(
        query=user_input,
        session_id=st.session_state.get("current_session_id"),
    )
    if response.get("success"):
        return (
            response.get("response")
            or response.get("message")
            or "I could not parse a response from the backend."
        )
    return response.get("error") or "The assistant could not be reached."


# Export functions for use in main app
__all__ = [
    "render_chat_ui",
    "initialize_chat_session",
    "add_message",
    "render_chat_message",
    "render_chat_history",
    "render_history_panel",
    "export_chat_as_csv",
    "generate_ai_response",
    "save_chat_history",
    "load_all_sessions",
    "load_session",
    "delete_session",
    "start_new_conversation",
]
