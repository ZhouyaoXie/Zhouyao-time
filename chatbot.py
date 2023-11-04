import os
import openai
import streamlit as st
import json
from datetime import datetime
import logging

from backend import get_time_entries, get_current_entry, utc_to_pst

openai.api_key = st.secrets["OPENAI_API_KEY"]

# truncation logic:
# one record approx 40 tokens, task description = 300 tokens, user question = 200 tokens
# response = 600 tokens
# num of records = (16000 - 300 - 200 - 600) // 40 = 372


def init_chat_history():
    st.session_state.messages = []


def ask_chatgpt():
    global time_entries

    system_msg = """You are a personal time management and productivity AI assistant for Zhouyao. Today's date is {d}.
Your job is to analyze Zhouyao's time tracking data, summarize behavioral patterns, and provide valuable insights that could help users better understand how Zhouyao is spending her time. 
You must provide factual informaton based on Zhouyao's time tracking records, which you may obtain by calling the `get_time_entries` function with the relevant `start_time` and `end_time` input parameters. 
If you make up non-existent time records, the user will suffer greatly due to misinformation. Cite specific time tracking records if necessary. Limit your response to 100 words.""".format(d=utc_to_pst(datetime.utcnow().strftime('%Y-%m-%d'), '%Y-%m-%d'))

    functions = [
        {
            "name": "get_time_entries",
            "description": "Get Zhouyao's time tracking records within a specified date range. Date range can't exceed 30 days.",
            "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "start date for time records (inclusive), in YYYY-MM-DD format",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "start date for time records (inclusive), in YYYY-MM-DD format",
                        },
                    },
                "required": ["start_date", "end_date"],
            },
        },
    ]

    messages = [{"role": "system", "content": system_msg}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        functions=functions,
        function_call="auto",
        temperature=0.2,
        stream=True,
    )

    for response_chunk in completion:
        print(f"Response chunk: {response_chunk}")

        # check if GPT wanted to call a function
        response_message = response_chunk["choices"][0]["delta"]
        if "function_call" in response_message:
            valid_args = True 
            available_functions = {
                "get_time_entries": get_time_entries,
            }

            try:
                # get input parameters for function calling
                function_name = response_message["function_call"]["name"]
                function_to_call = available_functions[function_name]
                function_args = json.loads(
                    response_message["function_call"]["arguments"])

            except Exception as e:
                valid_args = False
                logging.warning("failed to extract function name or arguments. Error: {}".format(str(e)))
                function_response = get_time_entries()

            if valid_args:
                logging.info("calling function {}".format(function_name))
                try:
                    function_response = function_to_call(
                        start_date=function_args.get("start_date"),
                        end_date=function_args.get("end_date"),
                    )
                except Exception as e:
                    logging.warning(
                        "function calling failed. Error: {}".format(str(e)))
                    function_response = get_time_entries()

            # extend conversation with assistant's reply
            messages.append(response_message)
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
            second_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                messages=messages,
                temperature=0.2,
                stream=True,
            )  # get a new response from GPT where it can see the function response

            return second_response

    return completion
