import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional


def initialize_chat_session():
    """Initialize chat session state if not already present."""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_input_key" not in st.session_state:
        st.session_state.chat_input_key = 0


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
    """Render a single chat message with appropriate styling."""
    role = message.get("role", "assistant")
    content = message.get("content", "")
    timestamp = message.get("timestamp", "")
    
    # Define message styles based on role
    if role == "user":
        message_class = "chat-message-user"
        icon = "👤"
        title = "You"
    elif role == "assistant":
        message_class = "chat-message-assistant"
        icon = "🤖"
        title = "AI Assistant"
    else:  # system
        message_class = "chat-message-system"
        icon = "⚙️"
        title = "System"
    
    # Render message container
    with st.container():
        # Message header with role and timestamp
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.markdown(f"<div class='{message_class}'>", unsafe_allow_html=True)
            st.markdown(f"**{icon} {title}**")
        with col2:
            st.caption(timestamp)
        
        # Message content
        st.markdown(content)
        st.markdown("</div>", unsafe_allow_html=True)


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
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Clear Chat", key="clear_chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
    
    with col2:
        if st.button("📋 Export Chat", key="export_chat", use_container_width=True):
            export_chat_as_csv()
    
    with col3:
        if st.button("💾 Save Chat", key="save_chat", use_container_width=True):
            st.success("✅ Chat saved! (Feature: Save to session)")


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


def render_chat_ui():
    """Main chat UI component."""
    # Initialize session
    initialize_chat_session()
    
    st.header("💬 AI Chat Assistant")
    st.write("Interact with the AI assistant to get supply chain insights and recommendations.")
    
    # Create tabs for different chat views
    chat_tab, settings_tab = st.tabs(["Chat", "Settings"])
    
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
        if send_button and user_input.strip():
            # Add user message
            add_message("user", user_input)
            
            # Simulate AI response
            ai_response = generate_ai_response(user_input)
            add_message("assistant", ai_response)
            
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
    Generate AI response based on user input.
    
    This is a placeholder that should be integrated with actual AI backend.
    Replace with actual API calls or ML model inference.
    
    Args:
        user_input: The user's message
        
    Returns:
        AI-generated response string
    """
    # Placeholder responses based on keywords
    input_lower = user_input.lower()
    
    response_map = {
        "forecast": "📊 Based on the uploaded data, I can help you with demand forecasting. Please specify which metrics you'd like me to forecast and the time horizon.",
        "optimization": "🎯 Supply chain optimization involves multiple factors. Would you like me to focus on cost reduction, delivery time, or inventory levels?",
        "risk": "⚠️ I can analyze supply chain risks from your data. What specific risks are you concerned about (supplier, demand, logistics)?",
        "metrics": "📈 I can help you understand key supply chain metrics. Which metrics are most important to your business?",
        "recommendation": "💡 Based on the data patterns, here are some initial recommendations... (Please provide more context)",
        "data": "📁 I can help analyze your uploaded data. What specific insights are you looking for?",
        "help": "🆘 I'm here to help! You can ask me about:\n- Data analysis\n- Forecasting\n- Optimization recommendations\n- Risk assessment\n- Metrics interpretation",
    }
    
    # Check for keyword matches
    for keyword, response in response_map.items():
        if keyword in input_lower:
            return response
    
    # Default response
    return (
        "Thank you for your question! I'm processing your request. To provide better insights, "
        "I can help you with:\n\n"
        "• **Data Analysis** - Understand patterns in your supply chain data\n"
        "• **Forecasting** - Predict future demand or supply trends\n"
        "• **Optimization** - Find ways to reduce costs or improve efficiency\n"
        "• **Risk Management** - Identify and mitigate supply chain risks\n\n"
        "Please specify what you'd like help with, and I'll provide detailed recommendations!"
    )


# Export functions for use in main app
__all__ = [
    "render_chat_ui",
    "initialize_chat_session",
    "add_message",
    "render_chat_message",
    "render_chat_history",
    "export_chat_as_csv",
    "generate_ai_response",
]
