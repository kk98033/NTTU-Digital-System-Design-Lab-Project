from flask import Flask, request, jsonify, Response, stream_with_context
from ChatBot import ChatBot

app = Flask(__name__)

chat_agent = ChatBot()

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    def generate():
        response = chat_agent.chat(user_input)
        for token in response.response_gen:
            yield token  
            yield ''  

    return Response(stream_with_context(generate()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969)
