from google import genai
from google.genai import types
import wave
import os
from lmnr import Laminar, observe
from dotenv import load_dotenv

load_dotenv("/home/itel/Downloads/gemini/codes/Gemini/research_agent/.env")
Laminar.initialize(project_api_key=os.environ.get("laminar_api_key"))
client = genai.Client(api_key=os.environ.get("gemini_api_key"))


# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

@observe()
def main():
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents="Say cheerfully:  Hello! How are you?",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name='Kore',
                    )
                )
            ),
        ),
    )
    
    data = response.candidates[0].content.parts[0].inline_data.data

    file_name='out.wav'
    wave_file(file_name, data) # Saves the file to current directory

main()
    