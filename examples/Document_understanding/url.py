from google import genai
from google.genai import types
import httpx
from dotenv import load_dotenv
import os
from lmnr import Laminar, observe

load_dotenv()
Laminar.initialize(project_api_key=os.environ.get("laminar_api_key"))
client = genai.Client(api_key=os.environ.get("gemini_api_key"))

@observe()
def url():
    doc_url = "url.pdf"

    # Retrieve and encode the PDF byte
    doc_data = httpx.get(doc_url).content

    prompt = "Summarize this document"
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_bytes(
            data=doc_data,
            mime_type='application/pdf',
        ),
        prompt])
    print(response.text)
url()