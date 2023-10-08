import os
import openai
import streamlit as st 
import json 
from datetime import datetime 

from backend import get_time_entries, get_current_entry, utc_to_pst
from what_is_zhouyao_doing import TEST 

openai.api_key = st.secrets["OPENAI_API_KEY"]

# truncation logic: 
# one record approx 40 tokens, task description = 300 tokens, user question = 200 tokens 
# response = 600 tokens 
# num of records = (16000 - 300 - 200 - 600) // 40 = 372
MAX_ENTRIES = 350

# initialize entry information 
current_entry = get_current_entry() 
time_entries = get_time_entries()


def init_chat_history():
  st.session_state.messages = []


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

  if TEST: return [m['role'] + ': ' + m['content'] for m in st.session_state.messages]

  update_entries()

  system_msg = """You are a personal time management and productivity AI assistant for Zhouyao. Today's date is {d}.
Your job is to analyze Zhouyao's time tracking data, summarize behavioral patterns, and provide valuable insights that could help users better understand how Zhouyao is spending her time. 

Zhouyao's last 30 days of time tracking records, in reverse chronological order:
{t}

Interact with the user using the following guidelines:
1) Only answer questions related to time management and productivity for Zhouyao. If the user asks irrelevant questions, respond that you are a personal time management AI assistant.
2) Make sure to respond to questions only using the time tracking records provided above. Ask for clarification if necessary.
3) Respond in no more than 100 words.""".format(d = utc_to_pst(datetime.utcnow().strftime('%Y-%m-%d'), '%Y-%m-%d'), t = time_entries)


  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=[{"role": "system", "content": system_msg}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ],
    stream=True,
    temperature=0.5,
  )

  best_response = completion.choices[0].delta.get("content", "")

  return best_response 