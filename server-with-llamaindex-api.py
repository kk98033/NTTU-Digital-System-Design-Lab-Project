""" Reference: https://github.com/Siliconifier/Python-Unity-Socket-Communication """

# Created by Youssef Elashry to allow two-way communication between Python3 and Unity to send and receive strings

# Feel free to use this in your individual or commercial projects BUT make sure to reference me as: Two-way communication between Python 3 and Unity (C#) - Y. T. Elashry
# It would be appreciated if you send me how you have used this in your projects (e.g. Machine Learning) at youssef.elashry@gmail.com

# Use at your own risk
# Use under the Apache License 2.0

# Example of a Python UDP server

import UdpComms as U
import time
import wave
from WhisperTranscriber import WhisperTranscriber
from Denoiser import Denoiser
from ChatBot import ChatBot

from dotenv import load_dotenv
import os
import requests

# load .env file
load_dotenv()

# get API key from .env file
# api_key = os.getenv('XXX API KEY')

# Create UDP socket to use for sending (and receiving)
sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)

i = 0

def call_api(message):
    url = 'http://localhost:6969/normal_chat'
    data = {'message': message}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        response_json = response.json()
        print("API 回應：", response_json['response'])
        return response_json['response']
    else:
        print("發生錯誤，狀態碼：", response.status_code)

def save_wav(audio_data, filename, channels=1, sample_width=2, frame_rate=44100):
    with wave.open(filename, "wb") as wav_file:
        wav_file.setnchannels(channels)  # 單聲道
        wav_file.setsampwidth(sample_width)  # 樣本位寬，一般設置為2
        wav_file.setframerate(frame_rate)  # 採樣率
        wav_file.writeframes(audio_data)

audio_data = bytearray()  # 用來收集接收到的音頻數據

is_receiving_audio = False

def getTTS(voiceUrl="received_audio.wav"):
     # 使用 Whisper 來轉寫這個 WAV 文件
    transcription = transcriber.transcribe(voiceUrl)
    return transcription

print("Loading Whisper model...")
transcriber = WhisperTranscriber('medium')
print('Model loaded!')

# create an assistant
# chat_bot = ChatBot()
# print("Assistant loaded!")

print("開始接收音訊!")
while True:
    data = sock.ReadReceivedData()  # read data

    if data:
        if data == "START_AUDIO":
            is_receiving_audio = True
            audio_data = bytearray()
            print("開始接收音頻數據...")
        elif data == "END_AUDIO":
            is_receiving_audio = False

            # DEBUG: Save the received audio data to WAV file
            print("音頻數據接收完畢。正在保存檔案...")
            save_wav(audio_data, "received_audio.wav")
            print("檔案保存完畢。")

            denoiser = Denoiser()
            denoiser.process('received_audio.wav', 'received_audio_denoised.wav')

            # Get user TTS
            transcription = getTTS(voiceUrl='./received_audio_denoised.wav')
            print("TTS: ", transcription)

            # Send assistant response back to unity
            chat_bot_response = call_api(transcription)
            # Debug
            print(chat_bot_response)
            sock.SendData(chat_bot_response)

        elif is_receiving_audio:
            # Ensure data is treated as raw bytes
            audio_data.extend(data)
        else:
            print(data)  # Handle other messages

    time.sleep(0.005)