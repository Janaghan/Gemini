from google import genai
from google.genai import types
from dotenv import load_dotenv
from lmnr import Laminar,observe
import os


load_dotenv("/home/itel/Downloads/gemini/codes/Gemini/research_agent/.env")
Laminar.initialize(project_api_key=os.environ.get("laminar_api_key"))
client = genai.Client(api_key=os.environ.get("gemini_api_key"))

grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

config = types.GenerateContentConfig(
    tools=[grounding_tool]
)

def add_citations(response):
    text = response.text
    supports = response.candidates[0].grounding_metadata.grounding_supports
    chunks = response.candidates[0].grounding_metadata.grounding_chunks

    # Sort supports by end_index in descending order to avoid shifting issues when inserting.
    # This ensures that inserting text at the end doesn't change the indices for earlier insertions.
    sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)

    for support in sorted_supports:
        # Get the end index of the segment where the citation should be inserted
        end_index = support.segment.end_index
        # Check if there are any chunk indices associated with this support
        if support.grounding_chunk_indices:
            # Create citation string like [1](link1)[2](link2)
            citation_links = []
            # Iterate through each chunk index
            for i in support.grounding_chunk_indices:
                if i < len(chunks):
                    # Get the URI from the web metadata of the chunk
                    uri = chunks[i].web.uri
                    # Format the citation as a markdown link
                    citation_links.append(f"[{i + 1}]({uri})")

            citation_string = ", ".join(citation_links)
            # Insert the citation string into the text at the specified end index
            text = text[:end_index] + citation_string + text[end_index:]

    # Return the modified text with citations
    return text

@observe()
def main():
    response = client.models.generate_content(  
        model="gemini-2.5-flash",
        contents="Who won the cricket world cup 2023?",
        config=config,
    )
    return add_citations(response)

if __name__ == "__main__":
    print(main())