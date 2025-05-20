import webrtcvad
import wave
import contextlib
import numpy as np
from pydub import AudioSegment
from io import BytesIO
import os

def validate_wav_file(file_path):
    """Check if the file is a valid WAV file"""
    try:
        if not os.path.exists(file_path) or os.path.getsize(file_path) < 44:  # WAV header is 44 bytes
            return False
            
        # Check for RIFF header
        with open(file_path, 'rb') as f:
            header = f.read(12)
            if header[:4] != b'RIFF' or header[8:12] != b'WAVE':
                return False
                
        # Try opening with wave module
        with wave.open(file_path, 'rb') as wf:
            if wf.getnchannels() < 1 or wf.getsampwidth() < 1 or wf.getframerate() < 1:
                return False
                
        return True
    except Exception:
        return False

class VoiceActivityDetector:
    def __init__(self, aggressiveness=3):
        """
        Initialize VAD with specified aggressiveness (0-3)
        Higher values are more strict about filtering out non-speech
        """
        self.vad = webrtcvad.Vad(aggressiveness)
        
    def detect_from_file(self, file_path):
        """Detect if speech is present in the audio file"""
        try:
            if not validate_wav_file(file_path):
                print(f"Invalid WAV file: {file_path}")
                return False
                
            pcm_data, sample_rate, sample_width, num_channels = self._read_wave(file_path)
            
            # Convert to format compatible with webrtcvad if needed
            if sample_rate not in [8000, 16000, 32000, 48000] or num_channels != 1 or sample_width != 2:
                pcm_data, sample_rate = self._convert_audio(file_path)
                
            # Split audio into 30ms frames
            frame_duration_ms = 30  # ms
            frame_size = int(sample_rate * (frame_duration_ms / 1000.0))
            frame_step = frame_size * 2  # 16-bit samples
            
            frames = []
            for i in range(0, len(pcm_data) - frame_step, frame_step):
                frames.append(pcm_data[i:i + frame_step])
            print(f"Number of frames: {len(frames)}")    
            # Check each frame for speech
            speech_frames = 0
            for frame in frames:
                if len(frame) == frame_step and self.vad.is_speech(frame, sample_rate):
                    speech_frames += 1
                    
            # If we have enough speech frames, consider it speech
            speech_percentage = speech_frames / len(frames) if frames else 0
            print(f"Speech percentage: {speech_percentage}")
            return speech_percentage > 0.05  # Adjust threshold as needed
        except Exception as e:
            print(f"Error detecting speech: {str(e)}")
            return False
    
    def _read_wave(self, path):
        """Read a .wav file and return PCM data"""
        try:
            with contextlib.closing(wave.open(path, 'rb')) as wf:
                num_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                sample_rate = wf.getframerate()
                pcm_data = wf.readframes(wf.getnframes())
                print(f"Channels: {num_channels}, Sample Width: {sample_width}, Sample Rate: {sample_rate}")
                return pcm_data, sample_rate, sample_width, num_channels
        except wave.Error as e:
            print(f"Wave error reading {path}: {str(e)}")
            raise
            
    def _convert_audio(self, file_path):
        """Convert audio to format compatible with webrtcvad"""
        try:
            audio = AudioSegment.from_file(file_path)
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(16000)
            audio = audio.set_sample_width(2)
            
            buf = BytesIO()
            audio.export(buf, format="wav")
            buf.seek(0)
            
            with wave.open(buf, 'rb') as wf:
                pcm_data = wf.readframes(wf.getnframes())
            print(f"Converted audio to 16kHz mono PCM {pcm_data[:10]}...")    
            return pcm_data, 16000
        except Exception as e:
            print(f"Error converting audio: {str(e)}")
            raise

# Function to be called from app.py
def detect_speech(audio_path):
    detector = VoiceActivityDetector(aggressiveness=2)
    return detector.detect_from_file(audio_path)