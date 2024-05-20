import requests

url = 'http://127.0.0.1:6969/voice_chat'
file_path = 'received_audio_denoised.wav'

with open(file_path, 'rb') as file:
    files = {'file': file}
    response = requests.post(url, files=files)

if response.status_code == 200:
    data = response.json()
    print("Message:", data["message"])
    print("Transcription:", data["transcription"])
else:
    print("Failed to upload file. Status code:", response.status_code)
    print("Response:", response.text)
