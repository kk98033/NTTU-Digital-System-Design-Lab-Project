'''
這個 Flask 應用程式主要功能是接受上傳的音訊文件，經過降噪處理後，轉錄成文本，然後調用 ChatBot 進行對話，最後將生成的回應轉換為音頻文件並回傳給用戶。

主要流程如下：
1. 接收上傳的音訊文件，驗證文件類型是否允許。
2. 將文件儲存在指定的上傳文件夾中。
3. 使用 Denoiser 類別對音訊文件進行降噪處理，並將結果儲存在另一個文件夾中。
4. 使用 WhisperTranscriber 類別對降噪後的音訊文件進行轉錄，將語音轉換為文本。
5. 調用 ChatBot 進行對話，獲得回應文本。
6. 將 ChatBot 的回應文本轉換為音頻文件並儲存。
7. 將音頻文件以附件形式回傳給用戶。
'''

from ChatBot import ChatBot
from WhisperTranscriber import WhisperTranscriber
from Denoiser import Denoiser

from flask import Flask, request, jsonify, send_file, make_response
from requests_toolbelt.multipart.encoder import MultipartEncoder
from werkzeug.utils import secure_filename
import requests
import logging
import os
import re

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # 藍色
        'INFO': '\033[92m',   # 綠色
        'WARNING': '\033[93m', # 黃色
        'ERROR': '\033[91m',  # 紅色
        'CRITICAL': '\033[1;91m', # 粗體紅色
        'PURPLE': '\033[95m'  # 紫色
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '\033[0m')
        reset_color = '\033[0m'
        message = super().format(record)
        return f"{log_color}{message}{reset_color}"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['DENOSIED_FOLDER'] = os.path.join(os.getcwd(), 'denoised')
app.config['OUTPUT_FOLDER'] = os.path.join(os.getcwd(), 'output')
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'ogg'}

# 設置日誌記錄器
handler = logging.StreamHandler()
formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# 清除現有的所有處理器
if app.logger.hasHandlers():
    app.logger.handlers.clear()

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def parse_custom_tag(response):
    pattern = r'<action>(\d+)</action>'
    match = re.match(pattern, response)
    if match:
        action_value = match.group(1)
        return {"action": action_value}
    else:
        return {"action": -1}

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # 藍色
        'INFO': '\033[92m',   # 綠色
        'WARNING': '\033[93m', # 黃色
        'ERROR': '\033[91m',  # 紅色
        'CRITICAL': '\033[1;91m', # 粗體紅色
        'PURPLE': '\033[95m'  # 紫色
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '\033[0m')
        reset_color = '\033[0m'
        message = super().format(record)
        return f"{log_color}{message}{reset_color}"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['DENOSIED_FOLDER'] = os.path.join(os.getcwd(), 'denoised')
app.config['OUTPUT_FOLDER'] = os.path.join(os.getcwd(), 'output')
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'ogg'}

# 設置日誌記錄器
handler = logging.StreamHandler()
formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# 清除現有的所有處理器
if app.logger.hasHandlers():
    app.logger.handlers.clear()

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def parse_custom_tag(response):
    pattern = r'<action>(\d+)</action>'
    match = re.match(pattern, response)
    if match:
        action_value = match.group(1)
        return {"action": action_value}
    else:
        return {"action": -1}

@app.route('/voice_chat', methods=['POST'])
def normal_chat():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        try:
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
            app.logger.info(f"\033[94m [Whisper transcription] {transcription}\033[0m")

            response = chat_agent.normal_chat(transcription)
            
            # 假設 response 有一個 response 屬性
            response_text = response.response
            
            app.logger.info(f'\033[94m [Bot response] {response_text}')

            parsed_response = parse_custom_tag(response_text)
            action = parsed_response.get('action')
            app.logger.info(f'Parsed action: {action}')

            call_tts_and_save(response_text, output_audio)

            # 構建多部分表單數據響應
            with open(output_audio, 'rb') as audio_file:
                encoder = MultipartEncoder(
                    fields={
                        'json': ('json', jsonify({'action': action}).get_data(as_text=True), 'application/json'),
                        'file': ('output.ogg', audio_file, 'audio/ogg')
                    }
                )
                response = make_response(encoder.to_string())
                response.headers['Content-Type'] = encoder.content_type
                return response
        except Exception as e:
            app.logger.error(f"Error processing file: {e}")
            return jsonify({"error": "Internal server error"}), 500
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(denoised_wav):
                os.remove(denoised_wav)
            if os.path.exists(output_audio):
                os.remove(output_audio)
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
    app.run(host='0.0.0.0', port=6969, debug=True, use_reloader=False)