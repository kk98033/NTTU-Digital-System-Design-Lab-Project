import requests
import json
from requests_toolbelt.multipart import decoder

url = 'http://127.0.0.1:6969/voice_chat'
file_path = 'received_audio_denoised.wav'
save_audio_path = 'downloaded_output.ogg'

with open(file_path, 'rb') as file:
    files = {'file': file}
    response = requests.post(url, files=files)

if response.status_code == 200:
    multipart_data = decoder.MultipartDecoder.from_response(response)
    
    # 解析多部分數據
    for part in multipart_data.parts:
        content_disposition = part.headers[b'Content-Disposition'].decode('utf-8')
        
        if 'name="json"' in content_disposition:
            json_data = json.loads(part.text)
            print("Action:", json_data["action"])
        elif 'name="file"' in content_disposition:
            with open(save_audio_path, 'wb') as audio_file:
                audio_file.write(part.content)
            print(f"Audio saved to {save_audio_path}")
else:
    print("Failed to upload file. Status code:", response.status_code)
    print("Response:", response.text)
