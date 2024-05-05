import os

from dotenv import load_dotenv
import nltk
import nest_asyncio

from llama_index.core import (
    VectorStoreIndex, StorageContext, 
    load_index_from_storage, 
    SimpleDirectoryReader, 
    PromptTemplate,
    Settings
)
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.core.query_engine import CitationQueryEngine, SubQuestionQueryEngine 
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

Settings.embed_model = HuggingFaceEmbedding(
    model_name="intfloat/multilingual-e5-large-instruct"
)

# Settings.llm = Ollama(model="llama3:instruct", request_timeout=60.0)
# Settings.llm = Ollama(model="ycchen/breeze-7b-instruct-v1_0:latest", request_timeout=60.0)
# Settings.llm = Ollama(model="gemma:7b", request_timeout=60.0)
Settings.llm = Ollama(model="llama3:instruct", request_timeout=60.0)

# llm = Ollama(model="llama3:instruct", request_timeout=60.0)

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

# prompt_file_path = 'NTTU-Digital-System-Design-Lab-Project\\react_system_header_str.txt'
prompt_file_path = 'NTTU-Digital-System-Design-Lab-Project\\react_system_header_str_CN.txt'

# file_path = 'NTTU-Digital-System-Design-Lab-Project\\react_system_header_str.txt'

nltk.download('averaged_perceptron_tagger')

current_path = os.getcwd()
print("當前工作目錄是：", current_path)
print(os.path.exists("./storage/"))

# load .env file
# load_dotenv()

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
        persist_dir="./storage/taiwanese",
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

response = tw_citation_engine.query("台灣有哪些原住民族？請你說出每一族的特色")
print(response)
print('=================')
for source in response.source_nodes:
    print(source.node.get_text())

citation_query_engine_tools = [
   QueryEngineTool(
       query_engine=tw_citation_engine,
       metadata=ToolMetadata(
           name="Taiwanese_indigenous",
           description=(
               "PLEASE ALWAYS employ the this tool when fielding questions regarding `Taiwanese indigenous peoples`."
               "提供台灣的原住民資料、節慶、慶典、歷史故事。 "
               "當被問到關於台灣原住民的問題時一律使用他。"
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
        name="Taiwanese_indigenous_sub_question_query_engine",
        description=(
            "PLEASE ALWAYS employ the this tool when fielding questions regarding `Taiwanese indigenous peoples`."
            "提供台灣的原住民資料、節慶、慶典、歷史故事。 "
            "當被問到關於台灣原住民的問題時一律使用他。"
            "useful for when you want to answer questions about Taiwanese indigenous peoples"
        ),
    ),
)

def show_RAG_sources() -> int:
    """
        用來輸出參考資料的來源。
        如果用戶向你索取資料，請使用他。
        請你將 `sources` 完整的輸出給用 戶。
    """
    print('=======SOURCE=======')
    for source in response.source_nodes:
        print(source.node.get_text())
        print()
    print('=======END-SOURCE=======')

    try:
        sources = [ source.node.get_text() for source in response.source_nodes]
    except:
        return "目前沒有來源"
    # return sources
    return "所有的資料來源皆已經輸出!"

show_RAG_sources_tool = FunctionTool.from_defaults(fn=show_RAG_sources)

# tools = citation_query_engine_tools
tools = citation_query_engine_tools + [query_engine_tool, show_RAG_sources_tool]

agent = ReActAgent.from_tools(tools=tools, verbose=True, embed_model="local")
# agent = ReActAgent.from_tools(tools=tools, llm=llm, verbose=True, embed_model="local")

react_system_header_str = load_string_from_file(prompt_file_path)
# print(react_system_header_str)
if react_system_header_str:
    print("檔案內容讀取成功！")
else:
    print("檔案內容讀取失敗。")

react_system_prompt = PromptTemplate(react_system_header_str)
agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})

# Debug: print system prompt
# prompt_dict = agent.get_prompts()
# for k, v in prompt_dict.items():
#     print(f"Prompt: {k}\n\nValue: {v.template}")

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
    # agent.reset()