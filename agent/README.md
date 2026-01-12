# Agent Development Kit (ADK) Examples

This directory contains example agents built with the Google Agent Development Kit (ADK).

## Agents

### 1. Basic Agent (`agent.py`)
A simple agent configuration located in the root of this folder. It defines a `root_agent` using the `gemini-2.5-flash` model.

**Run:**
```bash
adk run agent
```

### 2. Multi-Tool Agent (`multi_tool_agent/`)
An agent equipped with custom tools to check weather and time for cities.
- **Location**: `multi_tool_agent/agent.py`
- **Tools**:
    - `get_weather`: Retrieves mock weather reports (currently hardcoded for "New York").
    - `get_current_time`: Retrieves time information (currently hardcoded logic for "New York").

**Run:**
```bash
adk run multi_tool_agent
```

## Setup

1.  **Install ADK**:
    ```bash
    pip install google-adk
    ```

2.  **Environment Variables**:
    Ensure you have a `.env` file with your Google API Key:
    ```
    GOOGLE_API_KEY="your_api_key_here"
    ```
