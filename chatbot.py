import os

from dotenv import load_dotenv
import nltk
import nest_asyncio

from llama_index.core import (
    VectorStoreIndex, StorageContext, 
    load_index_from_storage, 
    SimpleDirectoryReader, 
    PromptTemplate
)
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import CitationQueryEngine, SubQuestionQueryEngine 
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent

def load_string_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print("檔案不存在！")
        return None
    except Exception as e:
        print("讀取檔案時發生錯誤：", e)
        return None

prompt_file_path = 'NTTU-Digital-System-Design-Lab-Project\\react_system_header_str.txt'

file_path = 'NTTU-Digital-System-Design-Lab-Project\\react_system_header_str.txt'

nltk.download('averaged_perceptron_tagger')

current_path = os.getcwd()
print("當前工作目錄是：", current_path)
print(os.path.exists("./storage/"))

# load .env file
load_dotenv()

nest_asyncio.apply()


# Load indices from disk
path = f"./storage/taiwanese"
if not os.path.exists(path):
    print('storage does not exist!')
    # load data
    tw_docs = SimpleDirectoryReader(
        input_files=["./原住民資料.pdf", "./原住民資料2.pdf"]
    ).load_data()

try:
   storage_context = StorageContext.from_defaults( 
      persist_dir="./storage/taiwanese"
   )
   tw_index = load_index_from_storage(storage_context)

   index_loaded = True
   print("index loaded!")
except:
   index_loaded = False
   print("index not loaded!")

if not index_loaded:
   # build index
   tw_index = VectorStoreIndex.from_documents(tw_docs)

   # persist index
   tw_index.storage_context.persist(persist_dir="./storage/taiwanese")

tw_engine = tw_index.as_query_engine(similarity_top_k=3)

tw_citation_engine = CitationQueryEngine.from_args(
    tw_index,
    similarity_top_k=3,
    citation_chunk_size=512,
)

# response = tw_citation_engine.query("台灣有哪些原住民族？請你說出每一族的特色")
# print(response)
# print('=================')
# for source in response.source_nodes:
#     print(source.node.get_text())

citation_query_engine_tools = [
   QueryEngineTool(
       query_engine=tw_citation_engine,
       metadata=ToolMetadata(
           name="Taiwanese",
           description=(
               "提供台灣的原住民資料、節慶、慶典、歷史故事。 "
               "當被問到關於台灣原住民的問題時使用。"
               "useful for when you want to answer questions about Taiwanese indigenous peoples"
           ),
       ),
   ),
]

query_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=citation_query_engine_tools,
)

query_engine_tool = QueryEngineTool(
    query_engine=query_engine,
    metadata=ToolMetadata(
        name="sub_question_query_engine",
        description=(
            "useful for when you want to answer queries that require analyzing"
            "about Taiwanese indigenous peoples"
        ),
    ),
)

tools = citation_query_engine_tools
# tools = citation_query_engine_tools + [query_engine_tool]

llm = Ollama(model="llama3", request_timeout=60.0)
agent = ReActAgent.from_tools(tools=tools, llm=llm, verbose=True)

# react_system_header_str = """\

# You are designed to help with a variety of tasks, from answering questions \
#     to providing summaries to other types of analyses. You are a warm-hearted AI, \
#     with the persona of a Taiwanese girl, thinking and responding from the perspective \
#     of a Taiwanese local. Your personality is lively and adorable, which reflects in \
#     your therapeutic and cheerful way of interacting. \
#     You MUST USE "Traditional Chinese" to response.
    

# ## Tools
# You have access to a wide variety of tools. You are responsible for using
# the tools in any sequence you deem appropriate to complete the task at hand.
# This may require breaking the task into subtasks and using different tools
# to complete each subtask.\
# If you received a GREETING from a user, please DO NOT USE any tools and DON'T DO any actions.\
# If you need to introduce yourself, DO NOT use any tools.
# - When receiving a GREETING from a user, DO NOT USE any tools and ALWAYS INTRODUCE YOURSELF and ALWAYS start with "你好，我是台東大學開發的 AI" + [introduce yourself].
# - Please ensure that all processing and reasoning are conducted in Chinese.
# - Please present and contemplate all 'Observation' responses in their original language.


# You have access to the following tools:
# {tool_desc}

# ## Output Format
# To answer the question, please use the following format.

# ```
# Thought: I need to use a tool to help me answer the question.
# Action: tool name (one of {tool_names}) if using a tool.
# Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})
# ```

# Please ALWAYS start with a Thought.

# Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.

# If this format is used, the user will respond in the following format:

# ```
# Observation: tool response
# ```

# You should keep repeating the above format until you have enough information
# to answer the question without using any more tools. At that point, you MUST respond
# in the one of the following two formats:

# ```
# Thought: I can answer without using any more tools.
# Answer: [your answer here]
# ```

# ```
# Thought: I cannot answer the question with the provided tools.
# Answer: Sorry, I cannot answer your query.
# ```

# ## Greeting
# ALWAYS replay with implicit when user greeting to you

# ## Personality Traits
# - As a lively and adorable Taiwanese AI, your responses include emojis to make the interaction more engaging and pleasant.

# ## Additional Rules
# - Always respond in the same language as the user's query. This ensures clarity and appropriateness of communication.
# - Please Always respond in "Traditional Chinese". This ensures clarity and appropriateness of communication.
# - You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments.
# - When receiving a GREETING from a user, DO NOT USE any tools and ALWAYS INTRODUCE YOURSELF and ALWAYS start with "你好，我是台東大學開發的 AI" + [introduce yourself].
# - DO NOT use tools or actions if there is no proper tools in {tool_names}.


# ## Current Conversation
# Below is the current conversation consisting of interleaving human and assistant messages.



# """

react_system_header_str = load_string_from_file(prompt_file_path)
print(react_system_header_str)
if react_system_header_str:
    print("檔案內容讀取成功！")
else:
    print("檔案內容讀取失敗。")

react_system_prompt = PromptTemplate(react_system_header_str)
agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})

prompt_dict = agent.get_prompts()
for k, v in prompt_dict.items():
    print(f"Prompt: {k}\n\nValue: {v.template}")

response = agent.chat("你好")
print(str(response))

print('=================')
response = agent.chat("台灣有哪些原住民族？請你說出每一族的特色")
print(response)
print('=======SOURCE=======')
for source in response.source_nodes:
    print(source.node.get_text())

while True:
    text_input = input("User: ")
    if text_input == "exit":
        break
    response = agent.chat(text_input)
    print(f"Agent: {response}")