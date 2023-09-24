import os
import openai
import streamlit as st 
import json 
from datetime import datetime 

from backend import get_time_entries, get_current_entry, utc_to_pst

openai.api_key = st.secrets["OPENAI_API_KEY"]

# truncation logic: 
# one record approx 40 tokens, task description = 300 tokens, user question = 200 tokens 
# response = 600 tokens 
# num of records = (16000 - 300 - 200 - 600) // 40 = 372
MAX_ENTRIES = 350

# initialize entry information 
current_entry = get_current_entry() 
time_entries = get_time_entries()


def update_entries():
  global current_entry, time_entries
  new_entry = get_current_entry()
  if new_entry != current_entry:
    current_entry = new_entry
    time_entries = get_time_entries()

    # truncate if necessary 
    if len(time_entries.split('\n')) > MAX_ENTRIES:
      time_entries = '\n'.join(time_entries.split('\n')[:MAX_ENTRIES])


def ask_chatgpt():
  global time_entries

  update_entries()

  system_msg = """You are a personal time management and productivity AI assistant for Zhouyao. Today's date is {d}.
Your job is to analyze Zhouyao's time tracking data, summarize behavioral patterns, and provide valuable insights that could help users better understand how Zhouyao is spending her time. 

Zhouyao's last 30 days of time tracking records, in reverse chronological order::
{t}

Answer any question regarding how Zhouyao spends her time in the past 30 days based on the time tracking data above. Provide your answer in less than 80 words. Make sure to only draft your response based on the time entries provided above.

If you are asked to provide suggestions about how to improve her productivity and time management, provide an insightful response considering the following information:

Things Zhouyao would like to focus on: 
- work & learn about machine learning
- read fiction & non-fiction works
- write essays for her blog, Fusion 
- study music theory, songwriting, and music production
- practice guitar and the piano & write songs
- physical exercise and mental wellbeing""".format(d = utc_to_pst(datetime.utcnow().strftime('%Y-%m-%d'), '%Y-%m-%d'), t = time_entries)


  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=[{"role": "system", "content": system_msg}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ],
    stream=True,
  )

  return completion


# print(time_entries)