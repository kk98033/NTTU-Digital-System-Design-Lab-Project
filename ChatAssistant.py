import json
import time
from openai import OpenAI

class ChatAssistant:
    def __init__(self):
        self.client = OpenAI()
        self.assistant = self.client.beta.assistants.retrieve("asst_bFtLxx6rdpU5oAhbYMBF1pSO")
        self.ASSISTANT_ID = "asst_bFtLxx6rdpU5oAhbYMBF1pSO"
        self.thread = self.client.beta.threads.create()

        self.waitingForFunctionCallback = False
        self.currentToolCall = None
        self.run = None

    def sendMessage(self, user_input):
        run = self.submitMessage(self.assistant.id, self.thread, user_input)
        run = self.waitOnRun(run, self.thread) # wait for assistant to response
        return run

    def getGreetingMessage(self, greetingMsg, examples):
        ''' combime greeting message and example questions '''

        fullMsg = greetingMsg + "\n"

        if not examples: 
            return greetingMsg + "有什麼問題需要我回答的呢？ :)"
        for i, exp in enumerate(examples):
            fullMsg += f'{i+1}. {exp}\n'
        return fullMsg

    def getGreetingMessageResponse(self, userResponse, examples):
        try:
            # if user response index
            choseQuestion = examples[int(userResponse) - 1]
        except:  
            # User did not response a valid option
            choicesText = ' '.join(examples)

            # user this prompt to help assistant api know the quesiton user wanted
            # TODO: 自由回答
            return f'Please select an option from "{choicesText}" for "{userResponse}"'
        return choseQuestion

    def submitMessage(self, assistant_id, thread, user_message):
        # send message to assistant through api
        self.client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=user_message
        )
        return self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )
    
    def answerFunciton(self, userResponses):
        run = self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id,
            run_id=self.run.id,
            tool_outputs=[
                {
                    "tool_call_id": self.currentToolCall.id,
                    "output": userResponses,
                }
            ],
        )
        return run

    def waitOnRun(self, run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
            print(run.status)
        return run

    def getLatestAssistantResponse(self):
        # Fetch all messages in the thread, sorted in ascending order
        messages = self.getResponse()

        lastAssistantMessage = None

        for message in messages:
            if message.role == "assistant":
                lastAssistantMessage = message

        conversations = []
        for message in messages:
            conversations.append(f"{message.role}: {message.content[0].text.value}")

        lastResponse = "沒有找到 assistant 的回應哦~ :)"
        if lastAssistantMessage and lastAssistantMessage.content[0].type == "text":
            lastResponse = lastAssistantMessage.content[0].text.value

        return lastResponse

    def getResponse(self):
        return self.client.beta.threads.messages.list(thread_id=self.thread.id, order="asc")

    def prettyPrint(self, messages):
        print("# Messages")
        for m in messages:
            print(f"{m.role}: {m.content[0].text.value}")
        print()

    def getPrettyFormat(self, messages):
        result = "# Messages\n"
        for m in messages:
            result += f"{m.role}: {m.content[0].text.value}\n"
        return result


    def sendMessageToAssistant(self, user_input):
        if user_input.lower() == 'exit':
            return 'Exit'

        if not self.waitingForFunctionCallback:
            print('entering normal ')
            self.run = self.sendMessage(user_input)
            print(f'Run status: {self.run.status}')

        if self.run.status == 'requires_action' and not self.waitingForFunctionCallback:
            # return funcion response to user
            print('Assistant called a function')
            tool_call = self.run.required_action.submit_tool_outputs.tool_calls[0]
            arguments = json.loads(tool_call.function.arguments)

            self.waitingForFunctionCallback = True
            self.currentToolCall = tool_call

            fullGreetingMsg = self.getGreetingMessage(arguments["message"], arguments["examples"])
            return fullGreetingMsg

        elif self.run.status == 'requires_action' and self.waitingForFunctionCallback:
            tool_call = self.run.required_action.submit_tool_outputs.tool_calls[0]
            arguments = json.loads(tool_call.function.arguments)
            # print("examples: ", arguments["examples"])
            # if function needs a response
            # TODO: 可能會有多個funciton的情況
            self.run = self.answerFunciton(userResponses=self.getGreetingMessageResponse(user_input, arguments["examples"]))
            self.run = self.waitOnRun(self.run, self.thread)

            # TODO: test
            time.sleep(0.25)
            self.run = self.waitOnRun(self.run, self.thread)

            self.waitingForFunctionCallback = False
            self.currentToolCall = None

            return self.getLatestAssistantResponse()
        
        else:
            self.waitingForFunctionCallback = False
            self.currentToolCall = None
            
        return self.getLatestAssistantResponse()

if __name__ == "__main__":
    # assistant_id = "asst_bFtLxx6rdpU5oAhbYMBF1pSO"
    assistant = ChatAssistant()

    while True:
        userInput = input("Please enter your question ('exit' to end the conversation): ")
        response = assistant.sendMessageToAssistant(userInput)
        print(response)

        if response == 'Exit':
            break