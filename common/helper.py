from datetime import datetime
import time
import json


def datetime_from_timestamp(unix_timestamp):
    return datetime.fromtimestamp(int(unix_timestamp)).strftime('%Y-%m-%d %H:%M:%S')


def datetime_now():
    return datetime_from_timestamp(time.time())


def load_json(file_name):
    with open(file_name, 'r') as json_file:
        return json.loads(json_file.read())


def save_json(file_name, data):
    with open(file_name, 'w') as json_file:
        return json_file.write(json.dumps(data))
