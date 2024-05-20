from flask import Flask, request, jsonify, Response, stream_with_context
from ChatBot import ChatBot
import logging

app = Flask(__name__)

# 設置日誌
logging.basicConfig(level=logging.INFO)

chat_agent = ChatBot()

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.json.get('message')
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400

        app.logger.info(f'Received message: {user_input}')

        def generate():
            response = chat_agent.chat(user_input)
            for token in response.response_gen:
                yield token  
                yield ''  

        return Response(stream_with_context(generate()), content_type='application/json')
    except Exception as e:
        app.logger.error(f"Error in /chat: {e}", exc_info=True)
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/normal_chat', methods=['POST'])
def normal_chat():
    try:
        user_input = request.json.get('message')
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400

        app.logger.info(f'Received message: {user_input}')
        
        response = chat_agent.normal_chat(user_input)
        app.logger.info(f'Response: {response}')

        return jsonify({'response': str(response)})
    except Exception as e:
        app.logger.error(f"Error in /normal_chat: {e}", exc_info=True)
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969)