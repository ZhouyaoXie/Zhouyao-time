import sys
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.add_vertical_space import add_vertical_space

import streamlit as st  # type: ignore

from backend import get_current_entry

# Page configuration
st.set_page_config(
    page_title="zhouyao's time - now",
    page_icon="🏄",
    layout="wide",
    initial_sidebar_state="auto",  # "collapsed",
    menu_items={
        'About': "zhouyao's time"
    }
)

for ln in get_current_entry():
    st.header(ln)
add_vertical_space(5)
st.markdown(
    "*want to learn more about how zhouyao has been spending her time recently?*")

want_to_contribute = st.button("*ask GPT!*")
if want_to_contribute:
    switch_page("ask_gpt_about_zhouyaos_time")


# This will create a sidebar
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