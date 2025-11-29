# Gemini Chatbot

This directory contains the core chatbot implementation using the Google GenAI SDK.

## Files

-   **`main.py`**: The main entry point for the chatbot. It supports:
    -   **Function Calling **: Automatically detects and executes tools (e.g., Air Quality).
    -   **Thinking **: Uses the model's reasoning capabilities with a specified token budget.
    -   **Long Context **: Use model to explain the concepts

-   **`tools.py`**: Defines the tools available to the bot (currently `get_air_quality`).


## Configuration

Ensure you have a `.env` file set up with your `GOOGLE_API_KEY`.

## Usage Examples

### 1. Air Quality Check (Function Calling) and Long context
```bash
uv run main.py
# Prompt: "What is the air quality in chennai"
```
