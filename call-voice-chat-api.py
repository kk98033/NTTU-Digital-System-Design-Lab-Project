import requests

url = 'http://127.0.0.1:6969/voice_chat'
file_path = 'received_audio_denoised.wav'
save_audio_path = 'downloaded_output.ogg'

with open(file_path, 'rb') as file:
    files = {'file': file}
    response = requests.post(url, files=files)

if response.status_code == 200:
    # save audio
    with open(save_audio_path, 'wb') as audio_file:
        audio_file.write(response.content)
    print(f"Audio saved to {save_audio_path}")
    # data = response.json()
    # print("Message:", data["message"])
    # print("Transcription:", data["transcription"])
else:
    print("Failed to upload file. Status code:", response.status_code)
    print("Response:", response.text)
