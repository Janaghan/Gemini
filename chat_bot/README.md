# Gemini Chatbot

This directory contains the core chatbot implementation using the Google GenAI SDK.

## Files

-   **`thinking.py`**: The main entry point for the chatbot. It supports:
    -   **Function Calling (`-f`)**: Automatically detects and executes tools (e.g., Air Quality).
    -   **Multichat (`-m`)**: Interactive multi-turn conversation loop.
    -   **Thinking (`-t <budget>`)**: Uses the model's reasoning capabilities with a specified token budget.
-   **`main.py`**: A simplified or alternative entry point (ensure to check specific logic).
-   **`tools.py`**: Defines the tools available to the bot (currently `get_air_quality`).
-   **`log_setup.py`**: Handles structured logging using Laminar.
-   **`config.py`**: (Excluded from git) Should contain your `client` initialization and API keys.

## Configuration

Ensure you have a `.env` file or `config.py` set up with your `GOOGLE_API_KEY`.

## Usage Examples

### 1. Air Quality Check (Function Calling)
```bash
uv run thinking.py -f
# Prompt: "What is the air quality in New York?"
```

### 2. Interactive Chat
```bash
uv run thinking.py -m
# You: "Hello"
# Gemini: "Hi there!"
```

### 3. Reasoning Task
```bash
uv run thinking.py -t 1024
# Prompt: "Explain the theory of relativity in simple terms."
```
