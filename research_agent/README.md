# Research Agent

This agent is designed to analyze documents (PDFs) and provide structured research summaries using Google's Gemini models.

## Features

-   **Document Analysis**: Uploads and processes PDF documents.
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

1.  **Prepare Document**:
    Place your PDF file (e.g., `sample_document.pdf`) in the `research_agent` directory.

2.  **Run the Agent**:
    ```bash
    python main.py
    ```

3.  **Output**:
    The agent will print the analysis to the console and save the structured result to `research_results.json`.

## File Structure

-   `main.py`: Entry point. Handles file upload, generation request, and response processing.
-   `tools.py`: Contains helper functions and Pydantic models (`ResearchSummary`, `ResearchPoint`) for structured output.
