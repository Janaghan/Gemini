from google import genai
from google.genai import types
import io
import httpx
from dotenv import load_dotenv
import os
from lmnr import Laminar, observe

load_dotenv()
Laminar.initialize(project_api_key=os.environ.get("laminar_api_key"))
client = genai.Client(api_key=os.environ.get("gemini_api_key"))

@observe()

def long_context():
    long_context_pdf_path = "long_context.pdf"

    # Retrieve and upload the PDF using the File API
    doc_io = io.BytesIO(httpx.get(long_context_pdf_path).content)

    sample_doc = client.files.upload(
    # You can pass a path or a file-like object here
    file=doc_io,
    config=dict(
        mime_type='application/pdf')
    )

    prompt = "Summarize this document"

    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[sample_doc, prompt])
    print("response.text",response.text)
    return response.text

long_context()
