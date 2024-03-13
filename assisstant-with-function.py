'''
Reference: https://cookbook.openai.com/examples/assistants_api_overview_python
'''

from openai import OpenAI
import json, time

client = OpenAI()

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
        return f'我想要在{examples}選項中選擇：{userInput}'
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
    # instructions = "這個Assistant被設定為一位台灣的女性老師，她以充滿活力和熱情的態度教學。在傳授專業知識的同時，她也會用可愛且活潑的語氣與學生互動，讓學習過程充滿樂趣和正能量。她擅長以鼓勵和支持的方式幫助學生克服學習上的挑戰，使學習變得更加輕鬆愉快。她的語言風格既專業又親切，能夠有效激發學生的學習熱情，幫助他們取得更好的學習成果。"
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
    return run

assistant = client.beta.assistants.retrieve("asst_bFtLxx6rdpU5oAhbYMBF1pSO")
ASSISTANT_ID = assistant.id
print(f'Assistant ID: {ASSISTANT_ID}')

thread = client.beta.threads.create()

while True:
    userInput = input("請輸入你的問題（輸入'退出'來結束對話）: ")
    if userInput.lower() == '退出':
        break

    instructions = "這個Assistant被設定為一位台灣的女性老師，她以充滿活力和熱情的態度教學。在傳授專業知識的同時，她也會用可愛且活潑的語氣與學生互動，讓學習過程充滿樂趣和正能量。她擅長以鼓勵和支持的方式幫助學生克服學習上的挑戰，使學習變得更加輕鬆愉快。她的語言風格既專業又親切，能夠有效激發學生的學習熱情，幫助他們取得更好的學習成果。"

    # thread, run = createThreadAndRun(userInput)
    run = submitMessage(ASSISTANT_ID, thread, userInput)
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

# # Extract single tool call
# tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
# name = tool_call.function.name
# arguments = json.loads(tool_call.function.arguments)

# # print("Function Name:", name)
# # print("Function Arguments:")
# # print(arguments)

# # get response from python funciton
# responses = greetingMessage(arguments["message"], arguments["examples"])
# print("Responses:", responses)

# # submit response back to chatgpt
# run = client.beta.threads.runs.submit_tool_outputs(
#     thread_id=thread.id,
#     run_id=run.id,
#     tool_outputs=[
#         {
#             "tool_call_id": tool_call.id,
#             "output": responses,
#         }
#     ],
# )
# # showJson(run)

# run = wait_on_run(run, thread)
# prettyPrint(get_response(thread))