import streamlit as st
from huggingface_hub import InferenceClient
from langchain.memory import ConversationBufferMemory

# ----------------------------
# Initialize memory & LLM
# ----------------------------
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory()

if "client" not in st.session_state:
    st.session_state.client = InferenceClient(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        token="REPLACE YOUR HF-Token HERE"  # <-- replace with your token
    )

# ----------------------------
# Centered title
# ----------------------------
st.markdown("<h1 style='text-align: center;'>🤖 ORION 🤖</h1>", unsafe_allow_html=True)

# ----------------------------
# Persona selection
# ----------------------------
persona = st.selectbox(
    "Choose a Bot Persona:",
    ["Normal Bot", "RoastBot", "ShakespeareBot", "EmojiBot"]
)

def apply_persona(user_input, persona):
    """Modify the input based on persona."""
    if persona == "RoastBot":
        return (
            "You are RoastBot, an AI that ALWAYS roasts the user in a witty, sarcastic, "
            "funny, and slightly savage way. Never be polite or generic. "
            f"User said: {user_input}"
        )
    elif persona == "ShakespeareBot":
        return f"Respond in Shakespearean English: {user_input}"
    elif persona == "EmojiBot":
        return f"Translate the response into emojis ONLY nothing else: {user_input}"
    else:  # NormalBot
        return user_input

# ----------------------------
# Scrollable conversation container with auto-scroll
# ----------------------------
st.subheader("Conversation:")
conv_box = st.empty()  # Placeholder for dynamic content

def render_conversation():
    conversation_html = "<div style='height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px;'>"
    for msg in st.session_state.memory.chat_memory.messages:
        role = "👤 You" if msg.type == "human" else "🤖 Bot"
        conversation_html += f"<p><b>{role}:</b> {msg.content}</p>"
    conversation_html += "</div>"
    conv_box.markdown(conversation_html, unsafe_allow_html=True)

# Initial render
render_conversation()

# ----------------------------
# Input + Send button using form
# ----------------------------
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4,1])
    with col1:
        user_input = st.text_input("Type your message here...", key="input_text", placeholder="Say something...")
    with col2:
        submit_button = st.form_submit_button("Send")

# ----------------------------
# Handle sending
# ----------------------------
if submit_button and user_input:
    # Save user message
    st.session_state.memory.chat_memory.add_user_message(user_input)

    # Apply persona
    persona_input = apply_persona(user_input, persona)

    # Build messages for Hugging Face
    messages = []
    for msg in st.session_state.memory.chat_memory.messages:
        messages.append({
            "role": "user" if msg.type == "human" else "assistant",
            "content": msg.content
        })
    messages.append({"role": "user", "content": persona_input})

    # Get response
    response = st.session_state.client.chat_completion(
        messages,
        max_tokens=512,
        temperature=1.0  # increase for RoastBot creativity
    )
    bot_reply = response.choices[0].message["content"]

    # Save bot reply
    st.session_state.memory.chat_memory.add_ai_message(bot_reply)

    # Re-render conversation including new messages
    render_conversation()

