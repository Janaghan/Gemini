import asyncio
import os
import sys
from dotenv import load_dotenv
from lmnr import Laminar, observe
from src.session import run_chat_session

@observe()
async def main():
    # Load environment variables
    # load_dotenv() - Loaded in __main__
    
    if not os.environ.get("gemini_api_key"):
        print("❌ Error: gemini_api_key not found in .env")
        print("Please check your configuration.")
        sys.exit(1)
        
    try:
        await run_chat_session()
    except KeyboardInterrupt:
        print("\n Goodbye!")

if __name__ == "__main__":
    load_dotenv()
    Laminar.initialize(project_api_key=os.environ.get("laminar_api_key"))
    asyncio.run(main())
