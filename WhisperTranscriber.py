import whisper

class WhisperTranscriber:
    def __init__(self, model_name="base"):
        """
        - "tiny": 最小的模型，適合快速識別，但精度較低。
        - "base": 平衡了速度和精度的模型。
        - "small": 小型模型，精度和速度適中。
        - "medium": 中型模型，精度較高，適合需要較高識別質量的場景。
        - "large": 最大的模型，提供最高的精度，適用於計算資源充足的情況。
        """

        # Load the specified Whisper model
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_path, language="zh"):
        # Load the audio file from the given path
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)

        # Make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        if language == 'zh':
            # 設定識別選項，包括指定語言為中文
            options = whisper.DecodingOptions(language=language)
        else:
            # Detect the spoken language
            _, probs = self.model.detect_language(mel)
            detected_language = max(probs, key=probs.get)
            print(f"Detected language: {detected_language}")


        # Decode the audio
        options = whisper.DecodingOptions()
        result = whisper.decode(self.model, mel, options)

        # Return the recognized text
        return result.text

if __name__ == "__main__":
    transcriber = WhisperTranscriber()
    transcription = transcriber.transcribe("audio.mp3")
    print("Transcription:", transcription)