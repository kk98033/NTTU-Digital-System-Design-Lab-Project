'''
Reference: https://cookbook.openai.com/examples/assistants_api_overview_python
'''

from openai import OpenAI
import json, time

from dotenv import load_dotenv
import os

# load .env file
load_dotenv()

# get API key from .env file
api_key = os.getenv('OPENAI_API_KEY')

if api_key is None:
    raise Exception("OPENAI_API_KEY 未設定在 .env 文件或環境變量中")

client = OpenAI(api_key=api_key)

''' json in json/greetingMessage.json '''
def greetingMessage(message, examples):
    print(message)
    if not examples: return "有什麼問題需要我回答的呢？ :)"
    for i, exp in enumerate(examples):
        print(f'{i+1}. {exp}')
    userInput = input("請選擇一個問題: ")
    try:
        choseQuestion = examples[int(userInput) - 1]
    except: # not select right target
        choisesText = ' '.join(examples)
        return f'請你從"{choisesText}"選項中選擇關於"{userInput}"回答（使用繁體中文）'
    return choseQuestion


def getResponse(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

# Pretty printing helper
def prettyPrint(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()

def showJson(obj):
    json_obj = json.loads(obj.model_dump_json())
    formatted_json = json.dumps(json_obj, indent=4)
    print(formatted_json)

def createThreadAndRun(user_input):
    thread = client.beta.threads.create()
    run = submitMessage(ASSISTANT_ID, thread, user_input)
    return thread, run

def submitMessage(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def waitOnRun(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
        print(run.status)
    return run

assistant = client.beta.assistants.retrieve("asst_bFtLxx6rdpU5oAhbYMBF1pSO")
ASSISTANT_ID = assistant.id
print(f'Assistant ID: {ASSISTANT_ID}')

thread = client.beta.threads.create()

while True:
    userInput = input("請輸入你的問題（輸入'退出'來結束對話）: ")
    if userInput.lower() == '退出':
        break

    # thread, run = createThreadAndRun(userInput)
    run = submitMessage(ASSISTANT_ID, thread, "(請使用繁體中文回答)" + userInput)
    run = waitOnRun(run, thread)
    print(f'Run status: {run.status}')

    if run.status == 'requires_action':
        print('Assistant called a function')
        tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
        name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        responses = greetingMessage(arguments["message"], arguments["examples"])
        print("Responses:", responses)

        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=[
                {
                    "tool_call_id": tool_call.id,
                    "output": responses,
                }
            ],
        )
        run = waitOnRun(run, thread)
    prettyPrint(getResponse(thread))