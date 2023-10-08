import streamlit as st 
import os 
import requests
from datetime import datetime, timedelta
from base64 import b64encode
import pytz 

email, password = st.secrets["email"], st.secrets['password']

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


def sort_function(record):
    """
    Sort entries by date in reverse chronological order. 
    If two entries are in the same day, sort them by time in chronological order. 
    """
    date, time = record[1].split(' ')
    # The negative sign in front of date is to sort the days in reverse chronological order
    # We don't need a negative sign for time since within each day we want them in chronological order
    return (-int(date.replace('-', '')), time)


def format_record(record):
    project, start_time, end_time, duration, description = record
    hours, remainder = divmod(int(duration[:-1]), 3600)
    minutes = remainder // 60
    return f"{project}: {description}, from {start_time} to {end_time}, duration {hours} hours {minutes} minutes"


def get_time_entries(last_n_days = 30):
    # do not retrieve more than 30 days of data 
    days = min(30, last_n_days)

    auth_token = b64encode(f"{email}:{password}".encode()).decode("ascii")

    end_date = datetime.utcnow().strftime('%Y-%m-%d')
    start_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')

    url = f'https://api.track.toggl.com/api/v9/me/time_entries?start_date={start_date}&end_date={end_date}'

    data = requests.get(url, headers={'content-type': 'application/json', 'Authorization' : f'Basic {auth_token}'})
    data_json = data.json()

    entries = []
    for entry in data_json:
        # only send time entries that run more than 2 minutes 
        if entry['project_id'] in project_id_mapping and entry['duration'] > 120:
            project_name = project_id_mapping[entry['project_id']]
            start_time = utc_to_pst(entry['start'].replace('+00:00', '').replace('Z', '').replace('T', ' '))
            stop_time = utc_to_pst(entry['stop'].replace('+00:00', '').replace('Z', '').replace('T', ' '))
            entries.append([project_name, start_time, stop_time, str(entry['duration']) + 's', entry['description']])

    sorted_entries = sorted(entries, key=sort_function)

    current_date = None
    output_string = ""

    for record in sorted_entries:
        record_date = record[1].split(' ')[0]
        
        # Check if the date has changed or is the first record
        if record_date != current_date:
            output_string += record_date + "\n"
            current_date = record_date
        
        output_string += format_record(record) + "\n"

    return output_string


def utc_to_pst(utc_time_str, input_format="%Y-%m-%d %H:%M:%S"):
    """
    Convert UTC time string to PST time string.
    
    Args:
    - utc_time_str (str): Input UTC time in string format.
    - input_format (str, optional): Format of the input UTC time string. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
    - str: PST time string in the same format as the input.
    """
    
    utc_time = datetime.strptime(utc_time_str, input_format)
    utc_time = pytz.utc.localize(utc_time)

    pst_time = utc_time.astimezone(pytz.timezone('US/Pacific'))

    return pst_time.strftime(input_format)


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
                start_time_utc = data_json[i]['start'].replace('+00:00', '').replace('T', ' ').replace('Z', '')
                start_time = utc_to_pst(start_time_utc)
                stop_time_utc = data_json[i]['stop'].replace('+00:00', '').replace('T', ' ').replace('Z', '') if data_json[i]['stop'] is not None else 'now'
                stop_time = utc_to_pst(stop_time_utc) if stop_time_utc != "now" else "now"

                project = project_id_mapping[data_json[i]['project_id']]
                if data_json[i]['description'] is not None:
                    description = ': ' + data_json[i]['description']
                else:
                    description = ''
                msg = [
                    "from *{start}* to *{stop}*,".format(start = start_time, stop = stop_time), 
                    "zhouyao is spending her time on:",
                    ":orange[<< {task} >>]".format(task = project + description)
                ]
                return msg 
    except Exception:
        return err_msg 