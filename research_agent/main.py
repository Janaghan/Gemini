import argparse
import os
import time
from google import genai
from dotenv import load_dotenv
from lmnr import Laminar
import tools

# Load environment variables
load_dotenv()

# Initialize Laminar and Gemini Client
Laminar.initialize(project_api_key=os.environ.get("laminar_api_key"))
client = genai.Client(api_key=os.environ.get("gemini_api_key"))

def main():
    parser = argparse.ArgumentParser(description="Multi-Modal Agent: Audio/PDF/Text Input -> Text & Speech Output")
    parser.add_argument("--file", help="Path to an audio or PDF file")
    parser.add_argument("--prompt", default="Describe this content in detail.", help="Text prompt for the model")
    parser.add_argument("--tone", default="us", choices=['us', 'co.uk', 'com.au', 'co.in'], 
                        help="Voice tone/accent (us, co.uk, com.au, co.in)")
    parser.add_argument("--output_audio", default="output.mp3", help="Filename for the output audio")

    args = parser.parse_args()
    
    gemini_inputs = []

    # Handle File Input
    if args.file:
        try:
            uploaded_file = tools.upload_file(client, args.file)
            gemini_inputs.append(uploaded_file)
            
            # For audio files, we might want to wait a bit or check state, 
            # but usually Flash is fast enough for small files.
            if args.file.lower().endswith(('.mp3', '.wav', '.m4a')):
                 print("Processing audio file...")
                 time.sleep(2) 

        except Exception as e:
            print(f"Error handling file: {e}")
            return

    # Handle Prompt Input
    gemini_inputs.append(args.prompt)

    # Generate Content
    try:
        response_text = tools.generate_response(client, gemini_inputs)
        print("\n--- Gemini Response ---")
        print(response_text)
        print("-----------------------")

        # Generate Speech
        tools.text_to_speech(response_text, args.output_audio, tone=args.tone)

    except Exception as e:
        print(f"Error during generation: {e}")

if __name__ == "__main__":
    main()
