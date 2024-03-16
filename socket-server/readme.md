```markdown
# Unity-Python Socket 語音通信項目

## English Description
This project enables two-way voice communication between Unity and Python using sockets, with voice recognition provided by Whisper STT. It allows Unity to send audio data to a Python server, which then uses Whisper to transcribe the audio and send the text back to Unity.

### How to Use
1. Run the `server.py` script in Python to start the server.
2. In Unity, establish a connection to the server and start sending audio data.
3. The Python server will receive the audio, transcribe it using Whisper, and send the transcription back to Unity.

### Requirements
- Python 3
- Unity
- Whisper STT library

### Acknowledgements
Thanks to Youssef Elashry for the foundational socket communication code. The project utilizes his Python-Unity Socket Communication framework.

---

## 中文說明
此項目通過套接字在Unity和Python之間實現雙向語音通信，並使用Whisper STT進行語音識別。它允許Unity將音頻數據發送到Python服務器，然後服務器使用Whisper轉寫音頻並將文本發回Unity。

### 如何使用
1. 在Python中運行`server.py`腳本以啟動服務器。
2. 在Unity中，建立與服務器的連接並開始發送音頻數據。
3. Python服務器將接收音頻，使用Whisper進行轉寫，並將轉寫文本發回Unity。

### 需求
- Python 3
- Unity
- Whisper STT庫

### 致謝
感謝Youssef Elashry提供基礎的套接字通信代碼。該項目使用了他的Python-Unity套接字通信框架。
```
