import streamlit as st
from chatbot import ask_chatgpt, init_chat_history


# Page configuration
st.set_page_config(
    page_title="zhouyao's time - ask gpt",
    page_icon="🏄",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'About': "zhouyao's time"
    }
)

# create sidebar
st.sidebar.title("about")
st.sidebar.markdown("""
i've been using Toggl to track my productivity hours for years.  
recent advancements in LLM have made it possible to interact with these records in new and exciting ways.  
""")

st.sidebar.title("learn more")
st.sidebar.markdown("""
> [project repo](https://github.com/ZhouyaoXie/how-im-spending-my-time)  
> [zhouyao's website](https://xiezhouyao.site)  
> [zhouyao's blog](https://zhouyao.substack.com/)  """)

# Initialize chat history
if 'messages' not in st.session_state:
    init_chat_history()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🦦" if message['role'] == 'user' else "🦀"):
        st.markdown(message["content"])

# take in user input
prompt = st.chat_input(f"Try: what did Zhouyao do today?")
if prompt:
    # add user input to message history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # display user input
    with st.chat_message("user", avatar="🦦"):
        st.markdown(prompt)

    # display GPT response as stream
    with st.chat_message("assistant", avatar="🦀"):
        message_placeholder = st.empty()
        full_response = ""
        for response in ask_chatgpt():
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response})

    reset_button = st.button(
        "reset chat history", help="clears model memory", on_click=init_chat_history)
