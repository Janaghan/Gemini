# Research Agent

A powerful multi-modal research assistant powered by Google's Gemini models. This agent can analyze documents (PDF, Text), transcribe and analyze audio, perform Google Searches with citations, and provide structured research summaries.

## Features

-   **Multi-Modal Analysis**:
    -   **Documents**: Analyzes PDF and Text files.
    -   **Audio**: Transcribes and analyzes audio files (`.wav`, `.mp3`, etc.) using `gemini-2.5-flash`.
-   **Google Search Grounding**: Performs Google Searches with citations when no file is provided.
-   **Interactive Mode**: Engages in a multi-turn conversation about the uploaded file or search results.
-   **Structured Output**: Produces a JSON file (`research_result.json`) with:
    -   Executive summary.
    -   Key research points with confidence scores.
    -   Citations and sources.
-   **Audio Output (TTS)**: Optionally reads the summary aloud using Gemini's Text-to-Speech (`--speak`).
-   **Observability**: Integrated with Laminar for execution tracing.

## Setup

1.  **Prerequisites**:
    -   `uv` package manager

2.  **Environment Variables**:
    Create a `.env` file in the project root or `research_agent` directory:
    ```env
    gemini_api_key=YOUR_GEMINI_API_KEY
    laminar_api_key=YOUR_LAMINAR_API_KEY
    ```

3.  **Installation**:
    From the **project root** directory (parent of `research_agent`), run:
    ```bash
    uv sync
    ```

## Usage

Navigate to the `research_agent` directory:
```bash
cd research_agent
```

### 1. Analyze a Document
Analyze a local file (PDF, Text, or Audio):
```bash
python main.py --file path/to/document.pdf --query "What are the main findings?"
```

### 2. Google Search
Perform a grounded search without a file:
```bash
python main.py --query "Latest advancements in quantum computing"
```

### 3. Audio Output
Generate a spoken summary (saves to `output.wav`):
```bash
python main.py --query "Explain black holes" --speak
```

### 4. Interactive Mode
After the initial response, the agent enters an interactive loop.
-   **Follow-up**: Type your questions to continue the conversation.
-   **Exit**: Type `exit` or `quit` to terminate.

## Output

-   **Console**: Displays the summary and key points.
-   **JSON**: Saves full structured data to `research_result.json`.
-   **Audio**: Saves TTS output to `output.wav` (if `--speak` is used).

## File Structure

-   `main.py`: Core logic for file processing, search, and the interactive loop.
-   `tools.py`: Helper functions for file upload, TTS, and Pydantic models.
