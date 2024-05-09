import streamlit as st
import requests
import json

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
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()  # Trigger an exception for bad status
        return response.json()['response']
    except requests.RequestException as e:
        return f"API Error: {str(e)}"

st.title('NTTU 原住民老師')

# Input box and send button
user_input = st.text_input("Please enter your message:", key="user_input")

# Add sidebar with image and text
st.sidebar.image("llama_logo.png", use_column_width=True) 
st.sidebar.write("NTTU 原住民老師")


if st.button("Send"):
    if user_input:
        api_response = call_api(user_input)
        st.session_state.input = ""
        st.session_state.responses.append({"user": "user", "text": user_input})
        st.session_state.responses.append({"user": "bot", "text": api_response})

# Display the chat history
for message in st.session_state.responses:
    if message['user'] == "user":
        with st.container():
            st.markdown(f"<div style='text-align: right;'><i class='fa fa-user icon'></i></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='message user'>{message['text']}</div>", unsafe_allow_html=True)
    else:
        with st.container():
            st.markdown(f"<div style='text-align: left;'><i class='fa fa-robot icon'></i></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='message bot'>{message['text']}</div>", unsafe_allow_html=True)
