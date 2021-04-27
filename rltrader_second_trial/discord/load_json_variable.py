import json

def get_token():
    with open('parameter.json', 'r') as file:
        json_data = json.load(file)

    file.close()
    return json_data['bot-token']

