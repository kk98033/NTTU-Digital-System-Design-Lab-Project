import requests

def call_api(message):
    url = 'http://localhost:6969/normal_chat'
    data = {'message': message}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        response_json = response.json()
        print("API 回應：", response_json['response'])
    else:
        print("發生錯誤，狀態碼：", response.status_code)

print("輸入 'exit' 來結束程序。")
while True:
    user_input = input("請輸入文字：")
    if user_input.lower() == 'exit':
        break
    call_api(user_input)
