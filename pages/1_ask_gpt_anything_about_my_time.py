import streamlit as st 
from chatbot import ask_chatgpt

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🦦" if message['role'] == 'user' else "🦀"):
        st.markdown(message["content"])

if prompt := st.chat_input("Try: what did Zhouyao do yesterday?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🦦"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🦀"):
        message_placeholder = st.empty()
        full_response = ""
        for response in ask_chatgpt():
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
