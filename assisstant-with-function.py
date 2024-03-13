'''
Reference: https://cookbook.openai.com/examples/assistants_api_overview_python
'''

from openai import OpenAI
import json, time

client = OpenAI()

''' json in json/greetingMessage.json '''
def greetingMessage(message, examples):
    print(message)
    if not examples: return "有什麼問題需要我回答的呢？"
    for i, exp in enumerate(examples):
        print(f'{ i+1 }. { exp }')
    choseQuestion = examples[int(input()) - 1]
    return choseQuestion


def get_response(thread):
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
    run = submit_message(MATH_ASSISTANT_ID, thread, user_input)
    return thread, run

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

assistant = client.beta.assistants.retrieve("asst_bFtLxx6rdpU5oAhbYMBF1pSO")
# showJson(assistant)
MATH_ASSISTANT_ID = assistant.id
print(MATH_ASSISTANT_ID)

thread, run = createThreadAndRun(
    "你好！"
)
run = wait_on_run(run, thread)
print(run.status)

# Extract single tool call
tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
name = tool_call.function.name
arguments = json.loads(tool_call.function.arguments)

# print("Function Name:", name)
# print("Function Arguments:")
# print(arguments)

# get response from python funciton
responses = greetingMessage(arguments["message"], arguments["examples"])
print("Responses:", responses)

# submit response back to chatgpt
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
# showJson(run)

run = wait_on_run(run, thread)
prettyPrint(get_response(thread))