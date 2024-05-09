from dotenv import load_dotenv
import os

from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.llms import Ollama

# load .env file
load_dotenv()

tools = [TavilySearchResults(max_results=1)]
# tools = [TavilySearchResults(max_results=1)]

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/react")

# Choose the LLM to use
llm = Ollama(model="llama3:instruct")

# Construct the ReAct agent
agent = create_react_agent(llm, tools, prompt)

# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# agent_executor.invoke({"input": "what is LangChain?"})
agent_executor.invoke({"input": "Hello"})

# from langchain_core.messages import AIMessage, HumanMessage

# agent_executor.invoke(
#     {
#         "input": "what's my name? Only use a tool if needed, otherwise respond with Final Answer",
#         # Notice that chat_history is a string, since this prompt is aimed at LLMs, not chat models
#         "chat_history": "Human: Hi! My name is Bob\nAI: Hello Bob! Nice to meet you",
#     }
# )