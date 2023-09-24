import sys

import streamlit as st  # type: ignore

from backend import  get_current_entry

# Page configuration
st.set_page_config(
    page_title="zhouyao's time",
    page_icon="🦦",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "how im spending my time"
    }
)


for ln in get_current_entry():
    st.header(ln)
st.text('\n\n\n\n')
st.markdown("*Explore the sidebar > to learn more.*")


# This will create a sidebar
st.sidebar.title("how im spending my time 🏄")
st.sidebar.empty()
st.sidebar.markdown("""
About Me
> [my website](https://xiezhouyao.site)  
> [my blog](https://zhouyao.substack.com/)"""
)