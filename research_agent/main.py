import os
from dotenv import load_dotenv
from google import genai
import tools
from lmnr import Laminar, observe

# Load environment variables
load_dotenv()

Laminar.initialize(project_api_key=os.environ.get("laminar_api_key"))
client = genai.Client(api_key=os.environ.get("gemini_api_key"))

if not client:
    print("Error: gemini_api_key not found in environment variables.")
    exit(1)

@observe()
def main():
    print("--- Research Agent ---")
    
    # Configuration
    pdf_path = "sample_document.pdf"
    query = "What are the main findings and their implications?"

    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found. Please ensure the file exists.")
        return

    print(f"Analyzing {pdf_path} with query: '{query}'")
    
    try:
        # Upload file
        uploaded_file = tools.upload_file(client, pdf_path)
        
        # Get prompt
        prompt = f"""
        Analyze the following query and provided context (if any).
        Extract key research points, their relevance, and a confidence score (0.0-1.0).
        Also provide a comprehensive summary and list the sources or page numbers used.
        
        Query: {query}
        """

        print("Generating structured analysis...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[uploaded_file, prompt],
            config={
                "response_mime_type": "application/json",
                "response_json_schema": tools.ResearchSummary.model_json_schema(),
            },
        )

        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
