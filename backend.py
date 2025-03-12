import streamlit as st
import os
import requests
from datetime import datetime, timedelta, timezone
from base64 import b64encode
import pytz
import logging

mode = None 
try: 
    email, password = st.secrets["email"], st.secrets['password']
    mode = "streamlit"
except:
    email, password = os.getenv("MY_EMAIL"), os.getenv("MY_PASSWORD")
    mode = "flask"

# list of project ids to analyze 
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
    """ 
    Format a time record as a readable natural language string  
    """
    project, start_time, end_time, duration, description = record
    hours, remainder = divmod(int(duration[:-1]), 3600)
    minutes = remainder // 60
    return f"{project}: {description}, from {start_time} to {end_time}, duration {hours} hours {minutes} minutes"


def get_time_entries(start_date=None, end_date=None):
    if start_date is None:
        start_date = datetime.utcnow().strftime('%Y-%m-%d')
    if end_date is None:
        end_date = datetime.utcnow().strftime('%Y-%m-%d')

    # do not retrieve more than 90 days of data
    if datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date) > timedelta(days=90):
        raise ValueError("Cannot query more than 90 days of time entries. Start date {} to end date {} has exceeded max date range.".format(
            start_date, end_date))

    # Toggle API is in UTC timezone, so need to convert timestamp to UTC first 
    start_datetime = convert_to_rfc3339(start_date, "start")
    end_datetime = convert_to_rfc3339(end_date, "end")

    logging.info('start datetime {}, end datetime {}'.format(start_datetime, end_datetime))

    auth_token = b64encode(f"{email}:{password}".encode()).decode("ascii")
    url = f'https://api.track.toggl.com/api/v9/me/time_entries?start_date={start_datetime}&end_date={end_datetime}'
    data = requests.get(url, headers={
                        'content-type': 'application/json', 'Authorization': f'Basic {auth_token}'})
    data_json = data.json()

    try:
        entries = []
        for entry in data_json:
            # only send time entries that run more than 5 minutes
            if entry['project_id'] in project_id_mapping and entry['duration'] > 300:
                project_name = project_id_mapping[entry['project_id']]
                start_time = utc_to_pst(entry['start'].replace(
                    '+00:00', '').replace('Z', '').replace('T', ' '))
                stop_time = utc_to_pst(entry['stop'].replace(
                    '+00:00', '').replace('Z', '').replace('T', ' '))
                entries.append([project_name, start_time, stop_time, str(
                    entry['duration']) + 's', entry['description']])

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

    # if there's any error in post-processing retrieved time entries
    # return the raw request response instead and let GPT decides what to do 
    except Exception as e:
        logging.error("Error parsing Toggl API request response, Error {}".format(str(e)))
        return data_json 


def convert_to_rfc3339(date_string, type, datetime_format = "%Y-%m-%d"):
    try:
        # Convert string to datetime object
        date_object = datetime.strptime(date_string, datetime_format)

        # Set the time to 12:00 AM if it's the start time, 11:59 PM if it's end time
        if type == 'start':
            date_object = date_object.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            date_object = date_object.replace(
                hour=23, minute=59, second=59).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        return date_object

    except ValueError as e:
        return str(e)


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
    """
    Retrieve the latest time entry from Toggl API 
    """
    url = 'https://api.track.toggl.com/api/v9/me/time_entries'
    auth_token = b64encode(f"{email}:{password}".encode()).decode("ascii")
    data = requests.get(url, headers={
                        'content-type': 'application/json', 'Authorization': f'Basic {auth_token}'})
    data_json = data.json()

    try:
        for i in range(len(data_json)):
            if data_json[i]['project_id'] in project_id_mapping:
                start_time_utc = data_json[i]['start'].replace(
                    '+00:00', '').replace('T', ' ').replace('Z', '')
                start_time = utc_to_pst(start_time_utc)
                stop_time_utc = data_json[i]['stop'].replace('+00:00', '').replace(
                    'T', ' ').replace('Z', '') if data_json[i]['stop'] is not None else 'now'
                stop_time = utc_to_pst(
                    stop_time_utc) if stop_time_utc != "now" else "now"

                project = project_id_mapping[data_json[i]['project_id']]
                if data_json[i]['description'] is not None:
                    description = ': ' + data_json[i]['description']
                else:
                    description = ''
                if mode == "streamlit":
                    msg = [
                        "from *{start}* to *{stop}*,".format(
                            start=start_time, stop=stop_time),
                        "zhouyao is spending her time on:",
                        ":orange[<< {task} >>]".format(task=project + description)
                    ]
                elif mode == "flask":
                    msg = [
                        "from {start} to {stop},".format(
                            start=start_time, stop=stop_time),
                        "zhouyao is spending her time on:",
                        "『 {task} 』".format(task=project + description)
                    ]
                return msg
    except Exception:
        return [
            "i am sorry, there's currently no data available.",
            "zhouyao might be on a vacation with her sea otter friends.",
            "you may also try refreshing this page."
        ]
