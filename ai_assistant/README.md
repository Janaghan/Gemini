# AI Assistant (Gemini Live API)

A real-time, multimodal AI assistant built with Google's **Gemini Live API**. This project demonstrates advanced audio handling, functional session management, and observability integration.

##  Architecture

The application is designed using a **Functional Event Loop** architecture, avoiding complex class hierarchies for clarity and performance.

*   **`main.py`**: Entry point. Handles environment setup, Laminar initialization, and starts the async session.
*   **`src/session.py`**: The core brain.
    *   **`run_chat_session`**: Orchestrates the WebSocket connection.
    *   **Input Loops**: `text_input_loop` (Text/PDF) and `send_loop` (Audio) capture user intent.
    *   **Output Loop**: `receive_loop` processes AI responses (Text/Audio) and triggers tools.
    *   **Tags**: Uses strict tags (`--input --text`, `--input --audio`) to ensure the model distinguishes modalities.
*   **`src/audio.py`**: Advanced Audio Engine.
    *   **VAD (Voice Activity Detection)**: Uses a Hysteresis Gate (Start/Stop thresholds) to filter noise.
    *   **Pre-roll Buffering**: Captures the split-second before speech to prevent cut-off words.
    *   **Split-Rate I/O**: Microsphone @ 16kHz (Stability), Speaker @ 24kHz (High Quality).
*   **`tools/`**: Modular tool definitions (e.g., `google_search`, `air_quality`).
*   **Observability**: Integrated with **Laminar** (`lmnr`) for real-time tracing of sessions and tool calls.

##  Live API Flow

1.  **Connect**: The client establishes a bidirectional WebSocket connection with `gemini-2.5-flash-native-audio-preview`.
2.  **Session Start**: System instructions are sent, defining the assistant's persona and modality rules (Text -> Text, Audio -> Audio).
3.  **Interaction Loop**:
    *   **User Audio**: Captures -> VAD Filter -> Stream to API.
    *   **User Text**: Captures -> Tagging -> Send to API.
    *   **Model Response**: Streams back audio chunks (played immediately) and text chunks (printed).
    *   **Tool Call**: If the model requests a tool, the client executes it locally and sends the result back in the same session.

##  Token & Key Handling

Security is managed via environment variables. The application does **not** hardcode keys.

*   **`gemini_api_key`**: Authenticates with Google GenAI.
*   **`laminar_api_key`**: Authenticates with Laminar for observability.
*   **`.env` File**: All keys are loaded from a `.env` file at runtime using `python-dotenv`.

### Key Features
1.  **Ephemeral Tokens**: Securely mints temporary tokens (10 min TTL) for every session connection.
2.  **Auto-Reconnection**: Automatically detects connection loss and reconnects using a fresh token.
3.  **Real Tools**: 
    *   **Native Google Search**: Leverages Gemini's built-in grounding (no extra keys required).
    *   **Air Quality**: Real-time data via OpenMeteo API.

##  How to Run

### Prerequisites
*   Python 3.11+
*   `uv` (Package Manager) or `pip`

### Setup
1.  **Clone & Navigate**:
    ```bash
    git clone https://github.com/Janaghan/Gemini.git
    cd Gemini/ai_assistant
    ```

2.  **Environment Variables**:
    Create a `.env` file in the `ai_assistant` directory:
    ```env
    gemini_api_key="YOUR_GOOGLE_KEY"
    laminar_api_key="YOUR_LAMINAR_KEY"
    ```

3.  **Run**:
    Use `uv` to handle dependencies and execution automatically:
    ```bash
    uv run main.py
    ```

### CLI Interaction
*   **Speak**: Just talk! The VAD will detect your voice.
*   **Type**: Type your message in the console and hit Enter.
*   **PDF**: Type the path to a PDF file (e.g., `/path/to/doc.pdf`) to have the AI analyze it.
