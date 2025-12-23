
import asyncio
import sys
from dotenv import load_dotenv
import pyaudio
from lmnr import Laminar

# Import from src package
# Ensure the parent directory is in python path if running directly
# Add current directory to path to ensure src can be imported
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.session import run_chat_session

def main():
    print("Starting Modular Live AI Assistant...")
    
    # Load env vars
    # Load env vars from the directory of this script
    load_dotenv("/media/itel/84d1169a-c6a2-40d0-a407-889e78507341/home/itel/Downloads/gemini/codes/Gemini/AI_Assistant/.env")
    
    # Initialize Laminar if key is present
    lmnr_key = os.getenv("LMNR_PROJECT_API_KEY")
    if lmnr_key:
        try:
            Laminar.initialize(project_api_key=lmnr_key)
            print("Laminar initialized.")
        except Exception as e:
            print(f"Laminar initialization failed: {e}")
    else:
        print("Laminar API key not found. Observability disabled.")

    # Run Session
    try:
        if sys.version_info < (3, 11):
            asyncio.run(run_chat_session())
        else:
            with asyncio.Runner() as runner:
                runner.run(run_chat_session())
    except KeyboardInterrupt:
        print("\nExiting per user request.")
    except Exception as e:
        print(f"Fatal Error: {e}")

if __name__ == "__main__":
    main()
