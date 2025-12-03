from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import mimetypes

import json

class ResearchPoint(BaseModel):
    point: str = Field(description="A key research point extracted from the document.")
    relevance: str = Field(description="Why this point is relevant to the query.")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0 for this finding.")

class ResearchSummary(BaseModel):
    summary: str = Field(description="A comprehensive summary of the document based on the query.")
    sources: List[str] = Field(description="List of sources or page numbers cited for these findings.")
    key_points: List[ResearchPoint] = Field(description="List of key research points.")

def save_to_json(data: BaseModel, filename: str):
    """Saves the Pydantic model to a JSON file."""
    with open(filename, "w") as f:
        f.write(data.model_dump_json(indent=2))
    print(f"Data saved to {filename}")

def upload_file(client, file_path: str):
    """
    Uploads a file to Gemini.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/pdf" # Default to PDF if unknown

    print(f"Uploading {file_path}...")
    with open(file_path, "rb") as f:
        uploaded_file = client.files.upload(
            file=f,
            config=dict(mime_type=mime_type)
        )
    
    print(f"File uploaded: {uploaded_file.name}")
    return uploaded_file

def get_analysis_prompt(query: str):
    """
    Returns the prompt for analysis.
    """
    return f"""
    Analyze the following query and provided context (if any).
    Extract key research points and provide a summary and confidence score.
    
    Query: {query}
    """
