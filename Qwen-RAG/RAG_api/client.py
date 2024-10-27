import requests

# 发送请求到服务端
def send_query(query):
    url = 'http://localhost:5000/query'
    response = requests.post(url, json={'query': query})
    return response.json()

# 用户查询
user_query = "什么是Qwen2，和Qwen1比较，优势在哪里？"
response = send_query(user_query)
print(response)