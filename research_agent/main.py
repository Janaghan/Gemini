
import os
from dotenv import load_dotenv
from google import genai
import tools
from lmnr import Laminar, observe
import json
import argparse

# Load environment variables
load_dotenv()

Laminar.initialize(project_api_key=os.environ.get("laminar_api_key"))
client = genai.Client(api_key=os.environ.get("gemini_api_key"))

if not client:
    print("Error: gemini_api_key not found in environment variables.")
    exit(1)

@observe()
def analyze_file(client, uploaded_file, query, chat_history, cache_name=None):
    """
    Analyzes an uploaded file using Gemini.
    """
    contents = []
    for history_item in chat_history:
        contents.append(history_item)
    
    contents.append(query)
    if not cache_name:
        contents.append(uploaded_file)
    
    prompt = f"""
        You are analyzing a provided document together with the user's query.

        Your rules:
        1. Only answer questions that can be directly answered using information present in the document.
        2. If the query is not found, not relevant, or not supported by the document, DO NOT answer the question.
        - Instead, set the 'summary' field to: "The query does not match the content of the document. Please provide a query related to the document."
        - Leave 'key_points' and 'sources' as empty lists.
        3. If the document is audio, first transcribe it accurately, then analyze.
        4. Extract key research points that directly relate to the query, and include:
            - the extracted points  
            - their relevance  
            - a confidence score (0.0-1.0)
        5. Provide a comprehensive summary ONLY of the parts of the document relevant to the query.
        6. List the specific pages, timestamps, or sections used—only if they exist in the document.

        Query: {query}
        """
    contents.append(prompt)
    
    
    is_audio = uploaded_file.mime_type.startswith("audio/")

    model_name = "gemini-2.5-flash"
    

    if cache_name:
        config["cached_content"] = cache_name

    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": tools.ResearchSummary.model_json_schema(),
        },
    )
    return response

@observe()
def perform_search(client, query, chat_history):
    """
    Performs a Google Search and structures the result.
    """
    contents = []
    for history_item in chat_history:
        contents.append(history_item)
    
    contents.append(query)
    
    tools_list = [tools.get_google_search_tool()]
    
    print(f"Searching Google for: '{query}'")
    prompt = f"""
    Search Google for the following query and provide a structured answer.
    
    Query: {query}
    """
    contents.append(prompt)
    
    # Step 1: Search
    search_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config={
            "tools": tools_list,
        },
    )
    
    if not search_response.text:
        return None

    # Step 2: Structure
    print("  Step 2: Structuring the information...")
    
    citations = []
    if search_response.candidates[0].grounding_metadata and search_response.candidates[0].grounding_metadata.grounding_chunks:
        for chunk in search_response.candidates[0].grounding_metadata.grounding_chunks:
            if chunk.web:
                citations.append(f"{chunk.web.title}: {chunk.web.uri}")
    
    citations_text = "\n".join(citations)
    
    structure_prompt = f"""
    Based on the following search results, provide a structured research summary and confidence score. It should follow the following JSON schema:
    points :[ {{
        "label": "topic",
        "source_text": "Based on the following search results, provide a structured research summary.\n\nSearch Results:\n{search_response.text}",
        "citations": "Sources/Citations found:\n{citations_text}\n\nIMPORTANT: Include the above Sources/Citations in the 'sources' list of your JSON output.",
        "confidence": between 0.0 to 1.0
        }}
        ]
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[structure_prompt],
        config={
            "response_mime_type": "application/json",
            "response_json_schema": tools.ResearchSummary.model_json_schema(),
        },
    )
    return response

@observe()
def main():
    print("--- Research Agent (Interactive) ---")
    print("Type 'exit' or 'quit' to stop.")
    
    parser = argparse.ArgumentParser(description="Research Agent")
    parser.add_argument("--file", type=str, help="Path to the file (PDF, Text, Audio) to analyze")
    parser.add_argument("--query", type=str, help="Initial query to ask about the file or general search")
    parser.add_argument("--speak", action="store_true", help="Speak the summary output")
    args = parser.parse_args()

    file_path = args.file
    initial_query = args.query
    chat_history = []
    
    uploaded_file = None
    if file_path:
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found. Please ensure the file exists.")
            return
        
        print(f"Uploading {file_path}...")
        uploaded_file = tools.upload_file(client, file_path)
        print(f"File uploaded: {uploaded_file.name}")
        
        if uploaded_file.mime_type.startswith("audio/"):
            print("Audio file detected.")

    # Select model (use gemini-2.5-flash as it is available)
    model_name = "gemini-2.5-flash"



    while True:
        if initial_query:
            query = initial_query
            initial_query = None 
        else:
            try:
                query = input("\nUser: ")
            except EOFError:
                break

        if query.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        
        if not query.strip():
            continue

        try:
            response = None
            if uploaded_file:
                response = analyze_file(client, uploaded_file, query, chat_history, cache_name=cache_name)
            else:
                response = perform_search(client, query, chat_history)
                if not response:
                    print("No results found from search.")
                    continue

            if response and response.text:
                try:
                    result = json.loads(response.text)
                    print("\nAgent:")
                    print(json.dumps(result, indent=2))
                    
                    output_filename = "research_result.json"
                    with open(output_filename, "w") as f:
                        json.dump(result, f, indent=2)
                    
                    if args.speak:
                        print("Generating audio output...")
                        tools.text_to_speech(client, result.get("summary", "No summary available."))

                    chat_history.append(f"User: {query}")
                    chat_history.append(f"Agent: {result.get('summary', 'Analysis provided.')}")

                except json.JSONDecodeError:
                    print("Error: Could not decode JSON response.")
                    print(response.text)
            else:
                print("No text response generated.")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
