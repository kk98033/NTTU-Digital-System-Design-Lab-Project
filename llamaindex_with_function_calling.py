from dotenv import load_dotenv
import os

# load .env file
load_dotenv()

# get API key from .env file
api_key = os.getenv('OPENAI_API_KEY')

from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.tools import BaseTool, FunctionTool

def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    return a * b

multiply_tool = FunctionTool.from_defaults(fn=multiply)

def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b

add_tool = FunctionTool.from_defaults(fn=add)

def greetings(questions: list) -> str:
    """Generate 5 questions about Taiwan"""
    response = ""
    for i, q in enumerate(questions):
      response += f"{i+1}.{q}\n"
    return response

greetings_tool = FunctionTool.from_defaults(fn=greetings)

import requests

api_key = os.getenv('weather')

def fetch_current_weather(location="Taipei", aqi="no"):
    base_url = "http://api.weatherapi.com/v1/current.json"
    parameters = {
        'key': api_key,
        'q': location,
        'aqi': aqi
    }

    response = requests.get(base_url, params=parameters)
    if response.status_code == 200:
        return response.json()  # 將 API 回傳的 JSON 資料轉為 Python 的字典
    else:
        return response.status_code, response.text  # 回傳錯誤代碼和錯誤訊息

fetch_current_weather_tool = FunctionTool.from_defaults(fn=fetch_current_weather)

llm = OpenAI(model="gpt-3.5-turbo-instruct")
agent = ReActAgent.from_tools([multiply_tool, add_tool, fetch_current_weather_tool, greetings_tool], llm=llm, verbose=True)
# agent = ReActAgent.from_tools([multiply_tool, add_tool, fetch_current_weather_tool], llm=llm, verbose=True)

response = agent.chat("你好")

response = agent.chat("What is 20+(2*4)? Calculate step by step ")

response_gen = agent.stream_chat("What is 20+2*4? Calculate step by step")

response_gen = agent.chat("現在台東天氣如何？")