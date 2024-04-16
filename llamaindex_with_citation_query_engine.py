from dotenv import load_dotenv
import os

# load .env file
load_dotenv()

# get API key from .env file
api_key = os.getenv('OPENAI_API_KEY')

from llama_index.core import (
   SimpleDirectoryReader,
   VectorStoreIndex,
   StorageContext,
   load_index_from_storage
)
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import CitationQueryEngine

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
except:
   index_loaded = False

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

for source in response.source_nodes:
    print(source.node.get_text())



query_engine_tools = [
   QueryEngineTool(
       query_engine=tw_citation_engine,
       metadata=ToolMetadata(
           name="Taiwanese",
           description=(
               "提供台灣的原住民資料、節慶、慶典、歷史故事。 "
               "Use a detailed plain text question as input to the tool."
           ),
       ),
   ),
]

from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
llm = OpenAI(model="gpt-3.5-turbo-0613")

agent = ReActAgent.from_tools(
   query_engine_tools,
   llm=llm,
   verbose=True
)

response = agent.chat("你知道阿美族嗎？可以詳細介紹他嗎？")
print(str(response))

response = agent.chat("豐年祭在什麼時候")
print(str(response))

for source in response.source_nodes:
   print(source.node.get_text())

response = agent.chat("台灣最高樓是什麼？")
print(str(response))

response = agent.chat("在火星上的條件下，植物生長需要哪些特別考慮？")
print(str(response))