import streamlit as st 
import os 
import requests
from datetime import datetime, timedelta
from base64 import b64encode

email, password = st.secrets["email"], st.secrets['passord']

project_id_mapping = {
    163465351: 'Email', 
    165995370: 'Personal Project', 
    165680665: 'Music', 
    163479096: 'Reading', 
    164908609: 'Personal Growth', 
    192228598: 'Weekly Learning', 
    192299722: 'Workout', 
    165790520: 'Work', 
    163471724: 'Writing',
}


def get_time_entries(api_token, user_agent="api_example"):

    auth_token = b64encode(f"{email}:{password}".encode()).decode("ascii")

    end_date = datetime.utcnow().strftime('%Y-%m-%d')
    start_date = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')

    url = f'https://api.track.toggl.com/api/v9/me/time_entries?start_date={start_date}&end_date={end_date}'

    data = requests.get(url, headers={'content-type': 'application/json', 'Authorization' : f'Basic {auth_token}'})
    data_json = data.json()

    entries = []
    for entry in data_json:
        if entry['project_id'] in project_id_mapping:
            entries.append([project_id_mapping[entry['project_id']],entry['start'].replace('+00:00', '').replace('Z', '').replace('T', ' '), entry['stop'].replace('+00:00', '').replace('Z', '').replace('T', ' '), str(entry['duration']) + 's', entry['description']])

    return entries 


def get_current_entry():
    url = 'https://api.track.toggl.com/api/v9/me/time_entries'
    auth_token = b64encode(f"{email}:{password}".encode()).decode("ascii")
    data = requests.get(url, headers={'content-type': 'application/json', 'Authorization' : f'Basic {auth_token}'})
    data_json = data.json()

    err_msg =  [
        "i am sorry, there's currently no data available.", 
        "zhouyao might be on a vacation with her sea otter friends.",
        "you may also try refreshing this page."
    ]


    try:
        for i in range(len(data_json)):
            if data_json[i]['project_id'] in project_id_mapping:
                start_time = data_json[i]['start'].replace('+00:00', '').replace('T', ' ').replace('Z', '')
                stop_time = data_json[i]['stop'].replace('+00:00', '').replace('T', ' ').replace('Z', '') if data_json[i]['stop'] is not None else 'now'
                project = project_id_mapping[data_json[i]['project_id']]
                description = ': ' + data_json[i]['description'] if data_json[i]['description'] is not None else ''
                msg = [
                    "from *{start}* to *{stop}*,".format(start = start_time, stop = stop_time), 
                    "zhouyao is spending her time on:",
                    ":orange[<< {task} >>]".format(task = project + description)
                ]
                return msg 
    except Exception:
        return err_msg 
    
    return err_msg 