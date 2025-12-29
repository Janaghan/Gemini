# AI Assistant (Gemini Live API)

A real-time, multimodal AI assistant built with Google's **Gemini Live API**. This project supports both a terminal-based **CLI** and a modern **Web Interface**, featuring advanced audio handling, secure session management, and observability integration.

##  Modes of Operation

You can run the assistant from this directory:

###  Web Interface (Recommended)
A full-featured browser interface supporting Audio loops, Text chat, and PDF uploads.

*   **Command**: `uv run app.py`
*   **Architecture**: Backend Proxy (`flask-sock`)
    *   **Browser**: Connects to local WebSocket (`/ws_stream`) using a secure, short-lived **Local JWT**.
    *   **Backend**: Authenticates the JWT, then proxies the connection to Gemini Live using your **Real API Key**.
    *   **Security**: Your real Gemini API Key never leaves the server.



##  Architecture & Features

### Core Components
*   **`src/session.py`**: The shared brain. Handles session management, token generation (Local JWT), and message loops.
*   **`src/audio.py`**: Audio engine with VAD and Split-Rate I/O (16kHz in / 24kHz out).
*   **`app.py`**: Flask server for the Web Interface. Implements the WebSocket Proxy.


### Key Features
*   **Multimodal**: Simultaneous Audio, Text, and PDF interaction.
*   **Secure Auth**: Implements a **Backend Proxy** pattern. The frontend never sees the API Key.
*   **Resiliency**: Auto-reconnection and extensive error handling (Code 1007/1008 fixes).
*   **Live Tools**:
    *   **Google Search**: Built-in grounding.
    *   **Air Quality**: Real-time data fetching.
*   **Observability**: Integrated with **Laminar** for session tracing.



##  How to Run

### Prerequisites
*   Python 3.11+
*   `uv` (Package Manager) - Recommended for dependency management.

### Setup
1.  **Clone & Navigate**:
    ```bash
    git clone https://github.com/Janaghan/Gemini.git
    cd Gemini/ai_assistant
    ```

2.  **Environment Variables**:
    Create a `.env` file in the root directory:
    ```env
    gemini_api_key="YOUR_GOOGLE_KEY"
    laminar_api_key="YOUR_LAMINAR_KEY" # Optional
    JWT_SECRET="JWT_SECRET"            
    ```

### Running the Web Interface
1.  Start the server:
    ```bash
    uv run app.py
    ```
2.  Open your browser to: `http://localhost:1234` (or the port shown in terminal).
3.  Click **Connect** to start talking!



---

## Technical Details

### Backend Proxy Flow (Web)
1.  **Connect**: Browser requests `/token`. Backend issues a **Local JWT** (TTL 10 mins).
2.  **WebSocket**: Browser connects to `ws://localhost:1234/ws_stream?token=JWT`.
3.  **Proxy**: Backend verifies valid JWT. If valid, opens a secure WebSocket to Google's `v1alpha` endpoint using the **Real API Key**.
4.  **Stream**: Audio/Text chunks are piped bidirectionally between Browser <-> Backend <-> Gemini.

### Audio Pipeline
*   **Input**: `navigator.mediaDevices` (Web) -> 16kHz PCM.
*   **Output**: Gemini 24kHz PCM -> Web Audio API (Web) 
