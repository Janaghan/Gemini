# Gemini AI Project

This repository contains code for interacting with Google's Gemini API, including a versatile chatbot and various example implementations.

## Structure

-   **`chat_bot/`**: Contains the main chatbot implementation ( `main.py`) with advanced features like:
    -   **Thinking Mode**: Uses a "thinking budget" to reason before answering.
    -   **Tool Use**: Integrates with external tools (e.g., Air Quality monitoring via OpenMeteo).
    -   **Multi-turn Chat**: Supports conversational history.
    -   **Laminar Logging**: Structured logging for observability.

-   **`examples/`**: A collection of standalone scripts demonstrating specific Gemini capabilities:
    -   `Image_understanding`: Vision capabilities.
    -   `Text-to-Text`: Basic text generation.
    -   `function_calling`: Examples of tool usage.
    -   `thinking`: Experiments with the thinking model.

## Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Janaghan/Gemini.git
    cd Gemini
    ```

2.  **Install dependencies**:
    (Assuming you are using `uv` or `pip`)
    ```bash
    uv sync
    # or
    pip install -r requirements.txt
    ```

3.  **Environment Variables**:
    Create a `.env` file in `chat_bot/` (and other relevant directories) with your API keys:
    ```env
    GOOGLE_API_KEY=your_api_key_here
    LAMINAR_API_KEY=your_laminar_key_here
    ```

