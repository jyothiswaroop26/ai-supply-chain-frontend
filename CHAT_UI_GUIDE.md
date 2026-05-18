# Chat UI Component - Integration Guide

## Overview
The Chat UI component provides a fully functional chat interface for the AI Supply Chain Dashboard. It includes message history, user/assistant message rendering, export functionality, and customizable settings.

## Features

### Core Features
- 💬 **Message Display**: Formatted chat messages for users and AI assistant
- 📝 **Message History**: Persistent chat history during session
- 🎨 **Styled Messages**: Different styling for user, assistant, and system messages
- ⚙️ **Settings Panel**: Customize response behavior and context
- 📊 **Chat Statistics**: View message counts and conversation metrics
- 📥 **Export Functionality**: Download chat history as CSV

### UI Components
- **Chat Display Area**: Scrollable container for message history
- **Message Input Field**: Text input with send button
- **Control Buttons**: Clear chat, export chat, save chat
- **Settings Tab**: Response mode, creativity level, context options
- **Statistics**: Message counts by role

## Integration Steps

### 1. Import the Component
```python
from components.chat_ui import render_chat_ui
```

### 2. Add to Main App
In `app/streamlit_app.py`, add the chat UI to the navigation:

```python
from components.chat_ui import render_chat_ui

with st.sidebar:
    st.header("Navigation")
    section = st.radio(
        "Select section",
        [
            "Overview",
            "Data Upload",
            "Filters & Search",
            "Data Visualization",
            "Forecasting",
            "KPI Dashboard",
            "Chat Assistant",  # Add this line
        ]
    )

# Add this to the main content area
if section == "Chat Assistant":
    render_chat_ui()
```

### 3. Customize Response Generator
The `generate_ai_response()` function is a placeholder. Replace it with your actual AI backend:

```python
# Option A: Call an external API
def generate_ai_response(user_input: str) -> str:
    response = requests.post(
        "https://your-api.com/chat",
        json={"message": user_input},
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    return response.json()["reply"]

# Option B: Use a local ML model
def generate_ai_response(user_input: str) -> str:
    from transformers import pipeline
    nlp = pipeline("text-generation", model="gpt2")
    result = nlp(user_input, max_length=100)
    return result[0]["generated_text"]

# Option C: Integrate with LangChain
def generate_ai_response(user_input: str) -> str:
    from langchain.llms import OpenAI
    llm = OpenAI(temperature=0.7)
    response = llm(user_input)
    return response
```

## API Reference

### Main Function
```python
render_chat_ui()
```
Renders the complete chat interface with tabs for chat and settings.

### Supporting Functions

#### `initialize_chat_session()`
Initializes session state for storing messages.
```python
initialize_chat_session()
```

#### `add_message(role, content, metadata=None)`
Adds a message to chat history.
```python
add_message("user", "What are the forecasts?")
add_message("assistant", "Based on the data...", {"source": "ML Model"})
add_message("system", "Chat cleared", {"action": "clear"})
```

#### `render_chat_message(message)`
Renders a single message with proper styling.
```python
message = {
    "role": "assistant",
    "content": "Here are the supply chain insights...",
    "timestamp": "14:30:00"
}
render_chat_message(message)
```

#### `render_chat_history()`
Displays all messages in the chat history.
```python
render_chat_history()
```

#### `export_chat_as_csv()`
Exports chat history as a downloadable CSV file.
```python
export_chat_as_csv()
```

#### `generate_ai_response(user_input)`
Generates AI response (placeholder - should be customized).
```python
response = generate_ai_response("What are my supply chain risks?")
```

## Styling

The chat UI uses CSS classes defined in `app/styles/custom.css`:

### CSS Classes
- `.chat-message-user` - User message styling
- `.chat-message-assistant` - Assistant message styling
- `.chat-message-system` - System message styling
- `.chat-container` - Main chat display area
- `.chat-input-area` - Input field container
- `.chat-send-button` - Send button styling
- `.chat-controls` - Control buttons container
- `.chat-header` - Chat header styling
- `.chat-settings-card` - Settings panel styling

### Customization
To customize colors, edit `app/styles/custom.css`:

```css
/* Change assistant message color */
.chat-message-assistant {
  background: rgba(50, 150, 200, 0.1);
  border-left: 4px solid #3296c8;
}

/* Change send button color */
.chat-send-button {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF5252 100%);
}
```

## Session State Variables

The component uses the following session state variables:

```python
st.session_state.chat_messages  # List of message dictionaries
st.session_state.chat_input_key  # Counter for input field regeneration
```

### Message Dictionary Structure
```python
{
    "role": "user|assistant|system",
    "content": "Message text",
    "timestamp": "HH:MM:SS",
    # Optional metadata
    "source": "ML Model",
    "confidence": 0.95,
    ...
}
```

## Example: Full Integration

```python
# streamlit_app.py
import streamlit as st
from components.chat_ui import render_chat_ui, add_message, generate_ai_response

st.set_page_config(page_title="AI Supply Chain", layout="wide")

with st.sidebar:
    section = st.radio("Select", ["Dashboard", "Chat", "Analytics"])

if section == "Chat":
    render_chat_ui()

# Or use in another component:
if section == "Dashboard":
    st.header("Dashboard")
    
    # Add quick chat button
    if st.button("💬 Get AI Insight"):
        add_message("user", "What's the inventory status?")
        response = generate_ai_response("What's the inventory status?")
        add_message("assistant", response)
        st.rerun()
```

## Tips & Best Practices

1. **Data Integration**: Connect `generate_ai_response()` with your actual data:
   ```python
   def generate_ai_response(user_input: str) -> str:
       if "uploaded_df" in st.session_state:
           df = st.session_state.uploaded_df
           # Use df to generate contextual responses
   ```

2. **Persistent Storage**: Save chat history to database:
   ```python
   if st.button("💾 Save Chat"):
       db.save_chat(st.session_state.chat_messages, user_id)
   ```

3. **Rate Limiting**: Add rate limiting for API calls:
   ```python
   import time
   if "last_request" not in st.session_state:
       st.session_state.last_request = 0
   
   if time.time() - st.session_state.last_request < 1:
       st.warning("Please wait before sending another message")
   ```

4. **Error Handling**: Add error handling in response generation:
   ```python
   try:
       response = generate_ai_response(user_input)
   except Exception as e:
       add_message("system", f"Error: {str(e)}")
   ```

## Troubleshooting

### Messages not appearing
- Check that `initialize_chat_session()` is called
- Verify session state is persisting across reruns

### Styling not applied
- Ensure `load_custom_css()` is called in main app
- Check browser cache (Ctrl+Shift+Delete)

### Input field clearing unexpectedly
- The `chat_input_key` counter handles this automatically
- If issues persist, check session state initialization

## Files Modified
- ✅ `app/components/chat_ui.py` - Main component (created)
- ✅ `app/styles/custom.css` - Added chat styling
- ✅ `app/components/__init__.py` - Added imports

## Next Steps
1. Integrate with your AI backend (OpenAI, Hugging Face, etc.)
2. Add data context to responses
3. Implement persistent storage (database)
4. Add message rate limiting
5. Enable audio input/output for accessibility
