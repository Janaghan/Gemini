# Research Agent

This agent is designed to analyze documents (PDFs, Text files) and provide structured research summaries using Google's Gemini models. It can also perform Google Searches when no file is provided.

## Features

-   **Document Analysis**: Uploads and processes PDF and Text documents.
-   **Google Search**: Performs Google Searches and synthesizes results when no document is provided.
-   **Structured Output**: Generates JSON responses containing:
    -   Comprehensive summary.
    -   Key research points with relevance and confidence scores.
    -   List of sources/citations.
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

Run the agent from the command line using `main.py`.

### Analyze a File
To analyze a PDF or Text file:
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

### Interactive Mode
If you run `main.py` without arguments, it will prompt you for a query (and default to search if no file is specified in code, though CLI usage is recommended).

## Output

The agent will print the analysis to the console and save the structured result to `research_result.json`.

## File Structure

-   `main.py`: Entry point. Handles file upload, generation request, and response processing.
-   `tools.py`: Contains helper functions and Pydantic models (`ResearchSummary`, `ResearchPoint`) for structured output.

