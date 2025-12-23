# Modular Multimodal AI Assistant

A high-performance, low-latency AI assistant capable of real-time voice interaction, text messaging, and file analysis

## Key Features


###  Advanced Audio Engine
- **Voice Activity Detection (VAD)**: Utilizes server-side detection for natural turn-talking.
- **Modular Design**: Audio hardware logic (`src/audio.py`) is decoupled from session logic (`src/session.py`).

###  Performance & Stats
- **Token Stats**: Real-time display of token consumption (e.g., `[Token Usage: 1542]`).
- **Thinking Budget**: Configurable output token limits for optimized responses.

###  Multimodal Capabilities
- **Voice**: Speak naturally (English enforced).
- **Text**: Type messages in the console *while* talking.
- **Files**: Upload files dynamically using the `/add` command.
- **Tools**:
    - **Google Search**: For current events (e.g., "Who won the World Cup?").
    - **Air Quality**: Real-time environmental data.

## Installation

1.  **System Dependencies** (Linux):
    ```bash
    sudo apt-get install python3-pyaudio portaudio19-dev
    ```
2.  **Running with `uv` (Recommended)**:
    ```bash
    uv run AI_Assistant/run_assistant.py
    ```

## Usage Logic

| Interaction | Action |
| :--- | :--- |
| **Speaking** | Wait for `***  MICROPHONE ACTIVE ***`, then speak. |
| **Typing** | Type directly in the terminal at any time. |
| **Files** | Type `/add /path/to/file.pdf` to send a file to the context. |

## Project Structure

- **`run_assistant.py`**: Entry point script.
- **`src/`**:
    - **`session.py` **: Manages API connection, tools, and tasks.
    - **`audio.py` **: Handles Microphone, Speaker, and Network I/O streams.
    - **`tools.py`**: Tool definitions (Search, Air Quality).
