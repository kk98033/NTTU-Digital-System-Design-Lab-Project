'''
這個 Flask 應用程式主要功能是接受上傳的音訊文件，經過降噪處理後，轉錄成文本。

主要流程如下：
1. 接收上傳的音訊文件，驗證文件類型是否允許。
2. 將文件儲存在指定的上傳文件夾中。
3. 使用 Denoiser 類別對音訊文件進行降噪處理，並將結果儲存在另一個文件夾中。
4. 使用 WhisperTranscriber 類別對降噪後的音訊文件進行轉錄，將語音轉換為文本。
5. 將轉錄結果以 JSON 格式回傳給用戶，並回傳轉錄的音頻文件。
'''

from ChatBot import ChatBot
from WhisperTranscriber import WhisperTranscriber
from Denoiser import Denoiser

from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_file
import requests
import logging
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['DENOSIED_FOLDER'] = os.path.join(os.getcwd(), 'denoised')
app.config['OUTPUT_FOLDER'] = os.path.join(os.getcwd(), 'output')
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'ogg'}

logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/voice_chat', methods=['POST'])
def normal_chat():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        denoised_wav = os.path.join(app.config['DENOSIED_FOLDER'], 'denoised.wav')
        output_audio = os.path.join(app.config['OUTPUT_FOLDER'], 'output.ogg')
        file.save(input_path)

        # Initialize Denoiser and process the file
        denoiser = Denoiser()
        denoiser.process(input_path, denoised_wav)

        # Initialize WhisperTranscriber and transcribe the denoised file
        transcriber = WhisperTranscriber()
        transcription = transcriber.transcribe(denoised_wav)
        app.logger.info(f"Whisper transcription: {transcription}")
        
        response = chat_agent.normal_chat(transcription)
        app.logger.info(f'Bot response: {response}')

        call_tts_and_save(response, output_audio)

        return send_file(output_audio, as_attachment=True)
    else:
        return jsonify({"error": "File type not allowed"}), 400

def call_tts_and_save(text, save_path):
    uri = f"http://127.0.0.1:9880/?text={text}&text_language=zh"
    stream_audio_from_api(uri, save_path)

def stream_audio_from_api(uri, save_path):
    try:
        response = requests.get(uri, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as audio_file:
            for chunk in response.iter_content(chunk_size=8192):
                audio_file.write(chunk)
        
        print(f"Audio saved to {save_path}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    current_working_directory = os.getcwd()
    app.logger.info(f"Current working directory: {current_working_directory}")

    app.logger.info("Loading chat bot...")
    chat_agent = ChatBot()
    app.logger.info("Chat bot loaded!")

    app.logger.info("Loading Whisper model...")
    transcriber = WhisperTranscriber('medium')
    app.logger.info('Model loaded!')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DENOSIED_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=6969, debug=True)
