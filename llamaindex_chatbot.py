import nltk
nltk.download('averaged_perceptron_tagger')

from dotenv import load_dotenv
import os

current_path = os.getcwd()
print("當前工作目錄是：", current_path)
print(os.path.exists("./storage/"))

# load .env file
load_dotenv()

# get API key from .env file
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

import nest_asyncio

nest_asyncio.apply()

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

# initialize simple vector indices
# NOTE: don't run this cell if the indices are already loaded!
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

Settings.chunk_size = 512
Settings.chunk_overlap = 64
Settings.llm = OpenAI(model="gpt-3.5-turbo")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Load indices from disk
from llama_index.core import load_index_from_storage

from llama_index.readers.file import UnstructuredReader
from pathlib import Path

years = [2022, 2021, 2020, 2019]

loader = UnstructuredReader()
doc_set = {}
all_docs = []

index_set = {}
for year in years:
    path = f"./storage/{year}"
    if not os.path.exists(path):
        print(f"./storage/{year} does not exist, creating a new one...")

        print(f'loading: {year}')
        year_docs = loader.load_data(
            file=Path(f"./test-data/UBER/UBER_{year}.html"), split_documents=False
        )
        # insert year metadata into each year
        for d in year_docs:
            d.metadata = {"year": year}
        doc_set[year] = year_docs
        all_docs.extend(year_docs)

        storage_context = StorageContext.from_defaults()
        cur_index = VectorStoreIndex.from_documents(
            doc_set[year],
            storage_context=storage_context,
        )
        index_set[year] = cur_index
        storage_context.persist(persist_dir=f"./storage/{year}")
    else:
        print(f"loading '{path}' data from storage...")
        cur_index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=path),
        )
        index_set[year] = cur_index

from llama_index.core.tools import QueryEngineTool, ToolMetadata

individual_query_engine_tools = [
    QueryEngineTool(
        query_engine=index_set[year].as_query_engine(),
        metadata=ToolMetadata(
            name=f"vector_index_{year}",
            description=(
                "useful for when you want to answer queries about the"
                f" {year} SEC 10-K for Uber"
            ),
        ),
    )
    for year in years
]

from llama_index.core.query_engine import SubQuestionQueryEngine

query_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=individual_query_engine_tools,
)

query_engine_tool = QueryEngineTool(
    query_engine=query_engine,
    metadata=ToolMetadata(
        name="sub_question_query_engine",
        description=(
            "useful for when you want to answer queries that require analyzing"
            " multiple SEC 10-K documents for Uber"
        ),
    ),
)

tools = individual_query_engine_tools + [query_engine_tool]


from llama_index.agent.openai import OpenAIAgent

agent = OpenAIAgent.from_tools(tools, verbose=True)

response = agent.chat("hi, i am bob")
print(str(response))

response = agent.chat(
    "What were some of the biggest risk factors in 2020 for Uber?"
)
print(str(response))

cross_query_str = (
    "Compare/contrast the risk factors described in the Uber 10-K across"
    " years. Give answer in bullet points."
)

response = agent.chat(cross_query_str)
print(str(response))

agent = OpenAIAgent.from_tools(tools)  # verbose=False by default

while True:
    text_input = input("User: ")
    if text_input == "exit":
        break
    response = agent.chat(text_input)
    print(f"Agent: {response}")

# User: What were some of the legal proceedings against Uber in 2022?