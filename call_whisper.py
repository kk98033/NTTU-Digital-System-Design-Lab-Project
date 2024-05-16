import whisper

model = whisper.load_model("base.en")
result = model.transcribe("魚.wav")
print(result["text"])
