#!/usr/bin/env python3
"""
Research Agent

Usage:
  python main.py --file <path_to_file> --query "<query>"
  python main.py --query "<query>"

Examples:
  python main.py --file sample.pdf --query "Summarize this document"
  python main.py --query "Who won the 2023 Cricket World Cup?"
"""
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
def main():
    print("--- Research Agent ---")
    
    # Configuration
    
    parser = argparse.ArgumentParser(description="Research Agent")
    parser.add_argument("--file", type=str, help="Path to the file (PDF, Text, Audio) to analyze")
    parser.add_argument("--query", type=str, help="Query to ask about the file or general search")
    args = parser.parse_args()

    file_path = args.file
    query = args.query

    if not query:
        query = input("Enter your query: ")

    tools_list = [tools.get_google_search_tool()]
    contents = [query]

    if file_path:
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found. Please ensure the file exists.")
            return
        
        print(f"Analyzing {file_path} with query: '{query}'")
        # Upload file
        uploaded_file = tools.upload_file(client, file_path)
        contents.append(uploaded_file)
        
        # Get prompt
        prompt = f"""
        Analyze the provided file and the following query.
        Extract key research points, their relevance, and a confidence score (0.0-1.0).
        Also provide a comprehensive summary and list the sources or page numbers used.
        If the file is audio, transcribe and analyze the content.
        
        Query: {query}
        """
        contents.append(prompt)
    else:
        print(f"Searching Google for: '{query}'")
        prompt = f"""
        Search Google for the following query and provide a structured answer.
        
        Query: {query}
        """
        contents.append(prompt)

    try:
        # print("Generating structured analysis...")
        
        if file_path:
            # Direct structured analysis for files
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": tools.ResearchSummary.model_json_schema(),
                },
            )
        else:
            # Search mode: Two-step process
            # Step 1: Search and get text response
            # print("  Step 1: Searching and gathering information...")
            search_response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config={
                    "tools": tools_list,
                },
                # No JSON schema here, as it conflicts with tools
            )
            
            if not search_response.text:
                print("No results found from search.")
                return

            # Step 2: Structure the output
            print("  Step 2: Structuring the information...")
            structure_prompt = f"""
            Based on the following search results, provide a structured research summary.
            
            Search Results:
            {search_response.text}
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[structure_prompt],
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": tools.ResearchSummary.model_json_schema(),
                },
            )

        if response.text:
             # Parse JSON response
            try:
                result = json.loads(response.text)
                print(json.dumps(result, indent=2))
                
                # Save to file
                output_filename = "research_result.json"
                with open(output_filename, "w") as f:
                    json.dump(result, f, indent=2)
                print(f"Result saved to {output_filename}")

            except json.JSONDecodeError:
                print("Error: Could not decode JSON response.")
                print(response.text)
        else:
            print("No text response generated.")


    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
