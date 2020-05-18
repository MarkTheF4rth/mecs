import requests
import json
from data_dump import data_dump
from requests.exceptions import ConnectionError
import time

URL = "http://localhost:5000/addEvent"

def load_data():
    try:
        loaded_data = data_dump()
        # return empty list and true value if the loaded_data is empty
        if not loaded_data:
            print('No data has been loaded')
            return [], True
        # otherwise return the list and false value
        else:
            return loaded_data, False
    except FileNotFoundError:
        print(""" Couldn't locate the file, no data loaded """)

def send_data(data):
    for element in data:
        try:
            # delay by time_dif attribute in miliseconds
            time.sleep(element['time_dif']/1000)

            del element['time_dif']
            element['time'] = time.time()
            requests.post(URL, data = json.dumps(element))

            print('[x] Sent Event: ', element)
        except ConnectionError as e:
            print(""" Couldn't connect to the API, server down? """)
            print(e)
        
data, isEmpty = load_data()
# makes sure list is not empty
if not isEmpty:
    print('Establishing connection with the API')
    send_data(data)
else:
    print(""" Couldn't send an empty list """)