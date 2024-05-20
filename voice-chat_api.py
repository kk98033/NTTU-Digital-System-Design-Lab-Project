from ChatBot import ChatBot
from WhisperTranscriber import WhisperTranscriber
from Denoiser import Denoiser

from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
import logging
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['DENOSIED_FOLDER'] = 'denoised/'
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'ogg'}

logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
        file.save(input_path)

        # Initialize Denoiser and process the file
        denoiser = Denoiser()
        denoiser.process(input_path, denoised_wav)

        # Initialize WhisperTranscriber and transcribe the denoised file
        transcriber = WhisperTranscriber()
        transcription = transcriber.transcribe(denoised_wav)

        return jsonify({"message": "File uploaded and processed successfully", "transcription": transcription}), 200
    else:
        return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.logger.info("Loading chat bot...")
    chat_agent = ChatBot()
    app.logger.info("Chat bot loaded!")

    app.logger.info("Loading Whisper model...")
    transcriber = WhisperTranscriber('medium')
    app.logger.info('Model loaded!')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DENOSIED_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=6969, debug=True)