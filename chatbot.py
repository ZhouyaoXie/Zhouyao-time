import os
import openai
import streamlit as st 
import json 

from backend import get_time_entries 

openai.api_key = st.secrets["OPENAI_API_KEY"]

# truncation logic: 
# one record approx 40 tokens, task description = 100 tokens, user question = 200 tokens 
# response = 600 tokens 
# num of records = (16000 - 100 - 200 - 600) // 40 = 377
entries = get_time_entries(30)[:350]

system_msg = """You are a personal time management and productivity AI assistant. Your job is to analyze the user's time tracking data, summarize patterns, and provide valuable insights that could help the user better understand how they're spending their time. 

Below is the user's information:

Name: Zhouyao 
Occupation: machine learning engineer  
Things she would like to focus on: 
- work & learn about machine learning
- read fiction & non-fiction works
- write essays for her blog called Fusion 
- study music theory, songwriting, and music production
- practice guitar and the piano & write songs
- physical exercise and mental wellbeing

Zhouyao's last 30 days of time tracking records, in the format of "<project name>, <start time>, <stop time>, <duration in seconds>, <description>":
{t}

Answer user's questions based on the information above. Provide your answer in less than 80 words. Include summary statistics if necessary. Avoid giving generic statements. Be as specific as possible.""".format(t = '\n'.join([', '.join(e) for e in entries]))
 

def ask_chatgpt():

  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=[{"role": "system", "content": system_msg}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ],
    stream=True,
  )

  return completion 