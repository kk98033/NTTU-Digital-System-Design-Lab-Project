import os
import json

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

class ChatBot:
    def __init__(self):
        self.setup_settings()
        self.load_dotenv_file()
        self.prepare_environment()
        self.agent = self.configure_agent()
        self.response = None

    def setup_settings(self):
        Settings.embed_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-large-instruct")
        Settings.llm = Ollama(model="llama3:instruct", request_timeout=60.0)
        # Settings.llm = Ollama(model="ycchen/breeze-7b-instruct-v1_0:latest", request_timeout=60.0)

    def load_dotenv_file(self):
        load_dotenv()

    def prepare_environment(self):
        nltk.download('averaged_perceptron_tagger')
        nest_asyncio.apply()
        self.current_path = os.getcwd()
        print("當前工作目錄是：", self.current_path)
        print(os.path.exists("./storage/"))

    def configure_agent(self):
        path = "./storage/taiwanese"
        if not os.path.exists(path):
            print('storage does not exist!')
            # os.makedirs(path)
            tw_docs = SimpleDirectoryReader(
                input_files=["./原住民資料.pdf", "./原住民資料2.pdf"]
            ).load_data()

        nttu_path = "./storage/nttu"
        if not os.path.exists(nttu_path):
            nttu_docs = SimpleDirectoryReader(
                input_files=["./台東大學介紹.pdf"]
            ).load_data()

        try:
            storage_context = StorageContext.from_defaults(persist_dir=path)
            tw_index = load_index_from_storage(storage_context)

            nttu_storage_context = StorageContext.from_defaults(persist_dir=nttu_path)
            nttu_index = load_index_from_storage(nttu_storage_context)

            index_loaded = True
            print("Index loaded!")
        except:
            index_loaded = False
            print("Index not loaded!")
            if tw_docs:
                tw_index = VectorStoreIndex.from_documents(tw_docs)
                tw_index.storage_context.persist(persist_dir=path)
                index_loaded = True

            if nttu_docs:
                nttu_index = VectorStoreIndex.from_documents(nttu_docs)
                nttu_index.storage_context.persist(persist_dir=nttu_path)
                index_loaded = True

        if index_loaded:
            tw_citation_engine = CitationQueryEngine.from_args(
                tw_index, similarity_top_k=3, citation_chunk_size=512)
            
            nttu_citation_engine = CitationQueryEngine.from_args(
                nttu_index, similarity_top_k=3, citation_chunk_size=512)

            # Load custom prompts for citation engine
            with open("NTTU-Digital-System-Design-Lab-Project/query_engine_prompt_CN.json", "r", encoding="utf-8") as file:
                prompts_dict = json.load(file)
            custom_qa_prompt_str = prompts_dict.get("response_synthesizer:text_qa_template")['PromptTemplate']['template']
            custom_refine_prompt_str = prompts_dict.get("response_synthesizer:refine_template")['PromptTemplate']['template']
            tw_citation_engine.update_prompts(
                {
                    "response_synthesizer:text_qa_template": PromptTemplate(custom_qa_prompt_str),
                    "response_synthesizer:refine_template": PromptTemplate(custom_refine_prompt_str)
                }
            )

            citation_tool = QueryEngineTool(
                query_engine=tw_citation_engine,
                metadata=ToolMetadata(
                    name="Taiwanese_indigenous",
                    description="用於回答有關台灣原住民的問題。"
                )
            )

            nttu_citation_tool = QueryEngineTool(
                query_engine=nttu_citation_engine,
                metadata=ToolMetadata(
                    name="NTTU_tool",
                    description="用於回答有關'台東大學', '東大','nttu'的問題。"
                )
            )

            show_RAG_sources_tool = FunctionTool.from_defaults(fn=self.show_RAG_sources)

            tools = [nttu_citation_tool, citation_tool, show_RAG_sources_tool]
            agent = ReActAgent.from_tools(tools=tools, verbose=True, embed_model="local")

            # Load system prompts from file
            react_system_header_str = self.load_string_from_file('NTTU-Digital-System-Design-Lab-Project/react_system_header_str_CN.txt')
            if react_system_header_str:
                react_system_prompt = PromptTemplate(react_system_header_str)
                agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})
                print("System prompt updated successfully!")
            return agent
        else:
            raise Exception("Unable to load or create index. Check the configuration and data files.")

    def load_string_from_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise Exception("檔案不存在！")
        except Exception as e:
            raise Exception("讀取檔案時發生錯誤：", e)

    def show_RAG_sources(self, *args, **kwargs) -> str:
        """
            ** 此函式不接受任何輸入參數。 **
            ** 當用戶想要取得資料來源，請使用他。 **
            用來輸出參考資料的來源。
        """
        try:
            print('=======SOURCE=======')
            for source in self.response.source_nodes:
                print(source.node.get_text())
            print('=======END-SOURCE=======')
        except:
            return "[告訴用戶:發生了錯誤!]"
        # return sources
        return "[告訴用戶:所有的資料來源皆已經輸出!]"

    def chat(self, input_text):
        self.response = self.agent.chat(input_text)
        return self.response


if __name__ == "__main__":
    bot = ChatBot()
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break
        elif user_input.lower() == "reset":
            bot = ChatBot()
            print("Chatbot has been reset.")
        else:
            response = bot.chat(user_input)
            print("Agent:", response)
