import os
import streamlit as st
import requests
import json

current_path = os.getcwd()
print("當前工作目錄是：", current_path)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    # Add Font Awesome
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">', unsafe_allow_html=True)

local_css("style.css")

# Ensure the response list is preserved between runs
if 'responses' not in st.session_state:
    st.session_state['responses'] = []

def call_api(message):
    url = 'http://localhost:6969/chat'
    data = {'message': message}
    try:
        with requests.post(url, json=data, stream=True, timeout=60) as response:
            response.raise_for_status()  # Trigger an exception for bad status
            for line in response.iter_lines():
                if line:
                    yield line.decode('utf-8')
    except requests.RequestException as e:
        yield f"API Error: {str(e)}"

def send_message(user_input):
    if user_input:
        # st.session_state.user_input = ""  

        # 避免重複輸出 
        if not st.session_state.responses:
            st.session_state.responses.append({"user": "user", "text": user_input})
        if st.session_state.responses[-1]["user"] != "user":
            st.session_state.responses.append({"user": "user", "text": user_input})

        response_text = ""

        # 暫時的顯示出來，等收到所有訊息後刪除
        with user_message_container.container():
            st.markdown(f"<div style='text-align: right;'><i class='fa fa-user icon'></i></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='message user'>{user_input}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: left;'><i class='fa fa-robot icon'></i></div>", unsafe_allow_html=True)

        # 為了可以 stream response
        # 下面註解的這行是可以讓她文字有背景框框，但是這樣就無法用 MD 格式顯示(沒有程式碼框框等功能...)
        # bot_message_container.markdown(f"<div class='message bot'>{""}", unsafe_allow_html=True)
        with st.spinner():
            for api_response in call_api(user_input):
                # response_text += f'{api_response}<br>'
                response_text += f'{api_response}\n'
                # 每次更新回應時更新容器內容
                # 下面註解的這行是可以讓她文字有背景框框，但是這樣就無法用 MD 格式顯示(沒有程式碼框框等功能...)
                # bot_message_container.markdown(f"<div class='message bot'>{response_text}</div>", unsafe_allow_html=True)
                bot_message_container.markdown(response_text)

        st.session_state.responses.append({"user": "bot", "text": response_text})
        
        user_message_container.empty()
        bot_message_container.empty()

        

def scroll_to_button():
    st.markdown(
            """
            <script>
            scrollToBottom();
            </script>
            """,
            unsafe_allow_html=True
        )

def display_chat_history(message_display_area):
    """Displays the chat history in a specified area."""
    with message_display_area.container():
        for message in st.session_state.responses:
            print(message)
            if message['user'] == "user":
                st.markdown(f"<div style='text-align: right;'><i class='fa fa-user icon'></i></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='message user'>{message['text']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: left;'><i class='fa fa-robot icon'></i></div>", unsafe_allow_html=True)
                # 下面註解的這行是可以讓她文字有背景框框，但是這樣就無法用 MD 格式顯示(沒有程式碼框框等功能...)
                # st.markdown(f"<div class='message bot'>{message['text']}</div>", unsafe_allow_html=True)
                st.markdown(message['text'])
# Title Container
title_container = st.container()
title_container.title('NTTU 原住民老師')

chat_container = st.container()
user_message_container = st.empty()
bot_message_container = st.empty()

if user_input := st.chat_input("Please enter your message:", key="user_input"):
    send_message(user_input)

# Main Chat Container
with chat_container:
    display_chat_history(st.empty())


# Input Container
# input_container = st.container()
# with input_container:
    # user_input = st.text_input("Please enter your message:", key="user_input", on_change=send_message, placeholder="Type a message and press enter")
    # if st.button("Send"):
    #     send_message()
    #     scroll_to_button()

# Add sidebar with image and text



st.sidebar.image("llama_logo.png", use_column_width=True)
st.sidebar.write("NTTU 原住民老師")
st.sidebar.header('This is a header with a divider', divider='grey')
st.sidebar.header('This is a header with a divider', divider='rainbow')
llm_model = st.sidebar.selectbox("Select Model", options=["llama3", "phi3", "openhermes", "llama2"])
embeddings_model = st.sidebar.selectbox(
    "Select Embeddings",
    options=["nomic-embed-text", "llama3", "openhermes", "phi3"],
    help="When you change the embeddings model, the documents will need to be added again.",
)

input_url = st.sidebar.text_input(
            "Add URL to Knowledge Base", type="default"
        )
st.sidebar.markdown("""---""")

alert = st.sidebar.info("Processing URLs...", icon="ℹ️")
# if f"{input_url}_scraped" not in st.session_state:
    # scraper = WebsiteReader(max_links=2, max_depth=1)
    # web_documents: List[Document] = scraper.read(input_url)
    # if web_documents:
    #     rag_assistant.knowledge_base.load_documents(web_documents, upsert=True)
    # else:
st.sidebar.error("Could not read website")
# input_url = st.sidebar.text_input(
#             "Add URL to Knowledge Base", type="default", key=st.session_state["url_scrape_key"]
#         )
add_url_button = st.sidebar.button("Add URL")

uploaded_file = st.sidebar.file_uploader(
    "Add a PDF :page_facing_up:", type="pdf"
)
# uploaded_file = st.sidebar.file_uploader(
#     "Add a PDF :page_facing_up:", type="pdf", key=st.session_state["file_uploader_key"]
# )
alert = st.sidebar.info("Processing PDF...", icon="🧠")