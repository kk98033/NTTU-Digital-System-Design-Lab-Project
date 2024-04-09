import torch
import torchaudio
import subprocess
from denoiser import pretrained
from denoiser.dsp import convert_audio

class Denoiser:
    def __init__(self, model_path='dns64', device='cuda'):
        self.model = pretrained.dns64().to(device)
        self.device = device

    def load_audio(self, file_path):
        wav, sr = torchaudio.load(file_path)
        return wav.to(self.device), sr

    def denoise_audio(self, wav, sr):
        wav = convert_audio(wav, sr, self.model.sample_rate, self.model.chin)
        with torch.no_grad():
            denoised = self.model(wav[None])[0]
        return denoised

    def save_audio(self, audio_tensor, file_path, sample_rate):
        torchaudio.save(file_path, audio_tensor.cpu(), sample_rate)

    def convert_to_mp3(self, wav_file, mp3_file):
        subprocess.run(['ffmpeg', '-i', wav_file, mp3_file])

    def process(self, input_path, output_wav, output_mp3=None):
        wav, sr = self.load_audio(input_path)
        denoised = self.denoise_audio(wav, sr)
        self.save_audio(denoised, output_wav, self.model.sample_rate)

        if output_mp3:
            self.convert_to_mp3(output_wav, output_mp3)

if __name__ == '__main__':
    denoiser = Denoiser()
    denoiser.process('alex_noisy.mp3', 'denoised.wav', 'denoised.mp3')
