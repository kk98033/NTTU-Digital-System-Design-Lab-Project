import requests

def call_api(message):
    url = 'http://localhost:6969/chat'
    data = {'message': message}
    with requests.post(url, json=data, stream=True) as response:
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    print("API 回應：", line.decode('utf-8'))
        else:
            print("發生錯誤，狀態碼：", response.status_code)

print("輸入 'exit' 來結束程序。")
while True:
    user_input = input("請輸入文字：")
    if user_input.lower() == 'exit':
        break
    call_api(user_input)
