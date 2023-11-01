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

# This will create a sidebar
st.sidebar.title("about")
st.sidebar.empty()
st.sidebar.markdown("""
> [project repo](https://github.com/ZhouyaoXie/how-im-spending-my-time)  
> [zhouyao's website](https://xiezhouyao.site)  
> [zhouyao's blog](https://zhouyao.substack.com/)  
>   
> built with Toggl API, OpenAI API, & Streamlit    """
                    )

# TODO: add info 


# Initialize chat history
if 'messages' not in st.session_state:
    init_chat_history()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🦦" if message['role'] == 'user' else "🦀"):
        st.markdown(message["content"])

if prompt := st.chat_input("Try: what did Zhouyao do today?"):
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
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response})

    reset_button = st.button(
        "reset chat history", help="clears model's memory about the conversation above", on_click=init_chat_history)
