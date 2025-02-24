import sys
import speech_recognition as sr
from pydub import AudioSegment
import whisper
import shutil
import os

# Ensure proper encoding for Windows terminals
sys.stdout.reconfigure(encoding='utf-8')

def check_ffmpeg():
    """ Check if FFmpeg is installed. """
    if shutil.which("ffmpeg") is None:
        print("Error: FFmpeg is not installed or not in system PATH.")
        print("Install it from: https://ffmpeg.org/download.html")
        sys.exit(1)

def convert_audio_to_text(file_path, use_whisper=False):
    """ Convert audio file to text using Whisper or Google Speech Recognition. """
    
    # Check if FFmpeg is installed before using pydub
    check_ffmpeg()

    # Convert MP3 to WAV if necessary
    if file_path.endswith(".mp3"):
        audio = AudioSegment.from_mp3(file_path)
        file_path = file_path.replace(".mp3", ".wav")
        audio.export(file_path, format="wav")

    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(file_path) as source:
            print("Processing audio...")
            audio_data = recognizer.record(source)  # Read entire audio file
    except Exception as e:
        print(f"Error reading audio file: {e}")
        return None

    if use_whisper:
        print("Using Whisper for transcription...")
        try:
            model = whisper.load_model("base")  # Choose "tiny", "base", "small", etc.
            result = model.transcribe(file_path)
            return result["text"]
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            return None
    else:
        print("Using Google SpeechRecognition...")
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Speech Recognition could not understand the audio."
        except sr.RequestError:
            return "Could not request results from the Speech Recognition service."

# Example usage
file_path = r"C:\Users\gauta\capstone\testcode\Datasets\Cement - Azeem.mp3"

transcribed_text = convert_audio_to_text(file_path, use_whisper=True)  # Set True for Whisper

if transcribed_text:
    print("\nTranscribed Text:\n", transcribed_text)
else:
    print("\nError: Transcription failed.")
