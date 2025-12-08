from google import genai
from google.genai import types

import wave
import os
from lmnr import Laminar, observe
from dotenv import load_dotenv

load_dotenv()
Laminar.initialize(project_api_key=os.environ.get("laminar_api_key"))
client = genai.Client(api_key=os.environ.get("gemini_api_key"))
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

transcript = client.models.generate_content(
   model="gemini-2.5-flash",
   contents="""Generate a short transcript around 100 words that reads
            Tell me the current political activities.
            The hosts names are Arun and Karthik.""").text

@observe()
def audio():
    response = client.models.generate_content(
    model="gemini-2.5-flash-preview-tts",
    contents=transcript,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                types.SpeakerVoiceConfig(
                    speaker='Arun',
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name='Kore',
                        )
                    )
                ),
                types.SpeakerVoiceConfig(
                    speaker='Karthik',
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name='Puck',
                        )
                    )
                ),
                ]
            )
        )
    )
    )
    data = response.candidates[0].content.parts[0].inline_data.data

    file_name='out.wav'
    wave_file(file_name, data) # Saves the file to current directory

audio()

