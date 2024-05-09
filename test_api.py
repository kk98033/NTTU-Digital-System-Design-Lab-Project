import requests

def call_api(message):
    url = 'http://localhost:6969/chat'
    data = {'message': message}
    response = requests.post(url, json=data)
    return response.json() 

print("輸入 'exit' 來結束程序。")
while True:
    user_input = input("請輸入文字：")
    if user_input.lower() == 'exit':  
        break
    api_response = call_api(user_input) 
    print("API 回應：", api_response)  
