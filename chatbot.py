import os
import openai
import streamlit as st
import json
from datetime import datetime
import logging

from backend import get_time_entries, get_current_entry, utc_to_pst

openai.api_key = st.secrets["OPENAI_API_KEY"]


def init_chat_history():
    """
    Initialize chat history in session state to empty array  
    """
    st.session_state.messages = []


def ask_chatgpt():
    """
    Call GPT with function calling, which can retrieve time entries in a specific time range from Toggl API. 

    Parse GPT response to decide whether it wants to call the function. 
    If it does, further parse function's input parameters, calls the function, attach the return values to the prompt, then call GPT again.  
    Return the model's response. 
    Note that GPT's API call has `stream` set to True, meaning that the function will return model response as a generator object. 
    """

    # set system message
    system_msg = """You are a personal time management and productivity AI assistant for Zhouyao. The time now is {d}.
Your job is to answer user's questions about Zhouyao's time tracking data, which you may obtain by calling the `get_time_entries` function with the appropriate `start_time` and `end_time` arguments. 
Your response must be factually correct. If you make up non-existent information, the user will suffer greatly due to misinformation. If you decide that the question can not be answered using the information you have, you should ask follow up questions for the user to provide more information.
Limit your response to 100 words.""".format(d=utc_to_pst(datetime.utcnow().strftime('%Y-%m-%d %H:%M, %A'), '%Y-%m-%d %H:%M, %A'))

    # set function definition
    functions = [
        {
            "name": "get_time_entries",
            "description": "Get Zhouyao's time tracking records from specified start_date to specified end_date. Date range can't exceed 45 days. You must provide start_date and end_date as input arguments.",
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

    # compile chat history
    messages = [{"role": "system", "content": system_msg}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # calls GPT with function calling
    response_generator = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=messages,
        functions=functions,
        function_call="auto",
        temperature=0.2,
        stream=True,
    )

    # parse model response to determine whether model wants to call a function
    # code reference: https://community.openai.com/t/functions-calling-with-streaming/305742
    response_text = ""
    function_call_detected = False
    func_call = {"name": "", "arguments": ""}
    for response_chunk in response_generator:
        if "choices" in response_chunk:
            deltas = response_chunk["choices"][0]["delta"]

            # if GPT wants to call function, collect function name and arguments in response stream
            if "function_call" in deltas:
                function_call_detected = True
                if "name" in deltas["function_call"]:
                    func_call["name"] += deltas["function_call"]["name"]
                if "arguments" in deltas["function_call"]:
                    func_call["arguments"] += deltas["function_call"]["arguments"]
            if (
                function_call_detected
                and response_chunk["choices"][0].get("finish_reason") == "function_call"
            ):
                # call function
                available_functions = {
                    "get_time_entries": get_time_entries,
                }
                function_to_call = available_functions[func_call["name"]]
                function_args = json.loads(func_call["arguments"])
                logging.info("calling function {} with parameters {}".format(
                    func_call["name"], func_call['arguments']))
                function_response = function_to_call(
                    start_date=function_args.get("start_date"),
                    end_date=function_args.get("end_date"),
                )

                # extend conversation with assistant's reply
                messages.append(
                    {
                        'role': 'assistant',
                        'content': None,
                        'function_call': func_call
                    }
                )

                # extend conversation with function response
                messages.append(
                    {
                        "role": "function",
                        "name": func_call["name"],
                        "content": function_response,
                    }
                )

                # get a new response from GPT where it can see the function response
                second_response = openai.ChatCompletion.create(
                    model="gpt-4-1106-preview",
                    messages=messages,
                    temperature=0.2,
                    stream=True,
                )

                return second_response

            # return response if GPT did not call function
            elif "content" in deltas and not function_call_detected:
                return response_generator

