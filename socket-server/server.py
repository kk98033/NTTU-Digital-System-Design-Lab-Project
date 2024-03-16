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

# Create UDP socket to use for sending (and receiving)
sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)

i = 0

def save_wav(audio_data, filename, channels=1, sample_width=2, frame_rate=44100):
    with wave.open(filename, "wb") as wav_file:
        wav_file.setnchannels(channels)  # 單聲道
        wav_file.setsampwidth(sample_width)  # 樣本位寬，一般設置為2
        wav_file.setframerate(frame_rate)  # 採樣率
        wav_file.writeframes(audio_data)

audio_data = bytearray()  # 用來收集接收到的音頻數據

is_receiving_audio = False

def getTTS():
     # 使用 Whisper 來轉寫這個 WAV 文件
    transcription = transcriber.transcribe("received_audio.wav")
    return transcription

transcriber = WhisperTranscriber('medium')
print('Model loaded!')

while True:
    data = sock.ReadReceivedData()  # read data

    if data:
        if data == "START_AUDIO":
            is_receiving_audio = True
            audio_data = bytearray()
            print("開始接收音頻數據...")
        elif data == "END_AUDIO":
            is_receiving_audio = False
            print("音頻數據接收完畢。正在保存檔案...")

            # Save the received audio data to a WAV file
            save_wav(audio_data, "received_audio.wav")

            print("檔案保存完畢。")
            sock.SendData("檔案保存完畢:D")
            transcription = getTTS()
            print("TTS: ", transcription)
            sock.SendData("TTS: " + transcription)
        elif is_receiving_audio:
            # Ensure data is treated as raw bytes
            audio_data.extend(data)
        else:
            print(data)  # Handle other messages

    time.sleep(0.005)