import requests
import json

def get_completion(prompt):
    headers = {'Content-Type': 'application/json'}
    data = {"prompt": prompt}
    # response = requests.post(url='http://36.133.8.100:11171', headers=headers, data=json.dumps(data))
    # response = requests.post(url='http://127.0.0.1:6010', headers=headers, data=json.dumps(data))
    # response = requests.post(url='http://localhost:8801', headers=headers, data=json.dumps(data))
    response = requests.post(url='http://127.0.0.1:8801', headers=headers, data=json.dumps(data))
    # print(response.text)
    return response.json()['response']

if __name__ == '__main__':
    print(get_completion('你好'))