import json

def data_dump():
    """ Read the local dump fake data and serialize it"""
    data = []
    with open('./data/fake_data.json', 'r') as file:
        for line in file:
            json_obj = json.loads(line)
            data.append(json_obj)
    return data
