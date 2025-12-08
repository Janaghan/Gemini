# Research Agent

This agent is designed to analyze documents (PDFs, Text files, Audio) and provide structured research summaries using Google's Gemini models. It supports interactive multi-turn conversations, Google Search with citations, and Audio Input/Output.

## Features

-   **Interactive Chat**: Continuous multi-turn conversation loop with context awareness.
-   **Multi-Modal Analysis**: 
    -   **Documents**: Uploads and processes PDF and Text documents.
    -   **Audio Input**: Transcribes and analyzes audio files (`.mp3`, `.wav`, etc.) using `gemini-2.5-flash`.
-   **Google Search**: Performs Google Searches with **citations** when no file is provided.
-   **Structured Output**: Generates JSON responses containing:
    -   Comprehensive summary.
    -   Key research points with relevance and confidence scores.
    -   List of sources/citations (including URLs for search results).
-   **Audio Output**: Generates audio summaries using Gemini's TTS model (`--speak` flag).
-   **Laminar Integration**: Observes execution traces using Laminar.

## Setup

1.  **Environment Variables**:
    Ensure you have a `.env` file in the project root or this directory with the following keys:
    ```env
    gemini_api_key=YOUR_GEMINI_API_KEY
    laminar_api_key=YOUR_LAMINAR_API_KEY
    ```

2.  **Dependencies**:
    Install the required packages:
    ```bash
    uv sync
    ```

## Usage

Run the agent from the command line using `main.py`. The agent now runs in an **interactive mode** by default after the initial query.

### Analyze a File
To analyze a PDF, Text, or Audio file:
```bash
python main.py --file <path_to_file> --query "<your_query>"
```
**Example:**
```bash
python main.py --file sample_document.pdf --query "Summarize this document"
```

### Google Search
To perform a Google Search (without a file):
```bash
python main.py --query "<your_search_query>"
```
**Example:**
```bash
python main.py --query "Who won the 2023 Cricket World Cup?"
```

### Audio Output (TTS)
To hear the summary spoken out loud, add the `--speak` flag:
```bash
python main.py --query "Tell me about black holes" --speak
```
This will generate an `output.wav` file.

### Interactive Mode
After the initial response, the agent enters an interactive loop. You can continue asking questions about the uploaded file or perform new searches.
-   Type your follow-up query at the `User:` prompt.
-   Type `exit` or `quit` to stop the agent.

## Output

The agent will print the analysis to the console and save the structured result to `research_result.json`. If `--speak` is used, an `output.wav` file is also created.

## File Structure

-   `main.py`: Entry point. Handles interactive loop, file upload, and orchestrates analysis. Refactored for modularity (`analyze_file`, `perform_search`).
-   `tools.py`: Contains helper functions (`upload_file`, `text_to_speech`) and Pydantic models (`ResearchSummary`) for structured output.

